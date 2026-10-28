import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import boto3
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import torch
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

CLASS_NAMES = ["Small", "Medium", "Large"]
NORMALIZATION = {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]}

#PyTorch retrieves each satellite image 
class DataCenterDataset(Dataset):
    def __init__(self, frame):
        self.rows = list(frame[["tensor_path", "size_label"]].itertuples(index=False, name=None))
        self.normalize = transforms.Normalize(**NORMALIZATION)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        path, label = self.rows[index]
        data = torch.load(path, map_location="cpu", weights_only=True)
        return self.normalize(data["image"].float()), int(label)

#prepares training data
def load_and_split_data(train_dir, metadata_dir):
    csv_path = next(Path(metadata_dir).rglob("*.csv"))
    metadata = pd.read_csv(csv_path, dtype={"id": str})

    metadata["sqft"] = pd.to_numeric(metadata["sqft"], errors="coerce")
    metadata = metadata[metadata["sqft"] > 0].copy()

    q1, q3 = metadata["sqft"].quantile([0.25, 0.75])
    metadata["size_label"] = metadata["sqft"].apply(
        lambda x: 0 if x < q1 else 1 if x <= q3 else 2
    )

    records = [
        {"id": path.stem, "tensor_path": str(path)}
        for path in Path(train_dir).rglob("*.pt")
    ]

    images = pd.DataFrame(records).merge(
        metadata[["id", "size_label"]], on="id"
    )

    facilities = images[["id", "size_label"]].drop_duplicates()

    train, remainder = train_test_split(
        facilities,
        test_size=0.30,
        random_state=42,
        stratify=facilities["size_label"]
    )

    validation, test = train_test_split(
        remainder,
        test_size=0.50,
        random_state=42,
        stratify=remainder["size_label"]
    )

    frames = [
        images[images["id"].isin(split["id"])].copy()
        for split in (train, validation, test)
    ]

    return frames, {"q1": float(q1), "q3": float(q3)}

#handle both training and validation.
#training calculates loss and updates weights, validation only measures performance.
def run_epoch(model, loader, criterion, device, optimizer=None):
    model.eval()
    if optimizer is not None:
        model.fc.train()
    total_loss, correct, total = 0.0, 0, 0
    with torch.set_grad_enabled(optimizer is not None):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            # Clear the previous batch's gradients before calculating new ones.
            if optimizer is not None:
                optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            # Calculate gradients and use them to update the trainable weights.
            if optimizer is not None:
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * labels.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total

#calculate accuracy, precision, recall, F1, and the confusion matrix, then save visuals.
def save_evaluation(model, loader, device, history, artifact_dir):
    predictions, actual = [], []
    model.eval()
    with torch.no_grad():
        for images, labels in loader:
            predictions.extend(model(images.to(device)).argmax(1).cpu().tolist())
            actual.extend(labels.tolist())
    #rows are actual classes, columns are predicted classes.
    matrix = confusion_matrix(actual, predictions, labels=[0, 1, 2])
    report_args = dict(labels=[0, 1, 2], target_names=CLASS_NAMES, zero_division=0)
    report = classification_report(actual, predictions, **report_args)
    metrics = {
        "test_accuracy": float(accuracy_score(actual, predictions)),
        "test_macro_f1": float(
            f1_score(
                actual,
                predictions,
                labels=[0, 1, 2],
                average="macro",
                zero_division=0,
            )
        ),
        "classification_report": classification_report(actual, predictions, output_dict=True, **report_args),
        "confusion_matrix": matrix.tolist(),
    }
    (artifact_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (artifact_dir / "classification_report.txt").write_text(report, encoding="utf-8")
    pd.DataFrame(history).to_csv(artifact_dir / "training_history.csv", index=False)
    print(f"Test accuracy: {metrics['test_accuracy']:.4f} | Macro F1: {metrics['test_macro_f1']:.4f}")
    print(report, flush=True)

    #compare training and validation over time to show learning and possible overfitting.
    for metric in ("loss", "accuracy"):
        fig, ax = plt.subplots()
        for split, label in (("train", "Training"), ("val", "Validation")):
            ax.plot([row["epoch"] for row in history],
                    [row[f"{split}_{metric}"] for row in history], label=label)
        ax.set(xlabel="Epoch", ylabel=metric.capitalize(),
               title=f"Training and validation {metric}")
        if metric == "accuracy":
            ax.set_ylim(0, 1)
        ax.legend()
        fig.tight_layout()
        fig.savefig(artifact_dir / f"{metric}_curve.png", dpi=150)
        plt.close(fig)
    display = ConfusionMatrixDisplay(matrix, display_labels=CLASS_NAMES)
    display.plot(cmap="Blues", values_format="d")
    display.ax_.set_title("Test confusion matrix")
    display.figure_.tight_layout()
    display.figure_.savefig(artifact_dir / "confusion_matrix.png", dpi=150)
    plt.close(display.figure_)


def main():
    parser = argparse.ArgumentParser(
        description="Train the ATLAS ResNet-18 size classifier as a SageMaker job."
    )
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    args = parser.parse_args()
    
    torch.manual_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    job_name = os.environ.get("TRAINING_JOB_NAME") or datetime.now(timezone.utc).strftime("local-%Y%m%d-%H%M%S-%f")
    
    artifact_dir = Path(os.environ.get("SM_OUTPUT_DATA_DIR", "./artifacts")) / job_name
    model_dir = Path(os.environ.get("SM_MODEL_DIR", "./model"))
    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    #SageMaker makes the S3 train and metadata input channels available as local folders.
    frames, thresholds = load_and_split_data(
        os.environ["SM_CHANNEL_TRAIN"], os.environ["SM_CHANNEL_METADATA"]
    )

    #feed images in batches, shuffling only the training set.
    loaders = [
        DataLoader(DataCenterDataset(frame), batch_size=args.batch_size, shuffle=index == 0)
        for index, frame in enumerate(frames)
    ]

    #reuse pretrained image features and train a new three-class classification head.
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for parameter in model.parameters():
        parameter.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))
    model.to(device)

    #cross-entropy measures classification error; Adam updates only the new head.
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.fc.parameters(), lr=args.learning_rate)
    history = []
    print(f"Job: {job_name} | Device: {device}", flush=True)

    #learn from the training set, then check validation performance after every epoch.
    for epoch in range(1, args.epochs + 1):
        train_loss, train_accuracy = run_epoch(model, loaders[0], criterion, device, optimizer)
        val_loss, val_accuracy = run_epoch(model, loaders[1], criterion, device)
        history.append(dict(epoch=epoch, train_loss=train_loss, train_accuracy=train_accuracy,
                            val_loss=val_loss, val_accuracy=val_accuracy))
        print(f"Epoch {epoch}/{args.epochs} | Train Loss: {train_loss:.4f} | "
              f"Train Acc: {train_accuracy:.2%} | Val Loss: {val_loss:.4f} | "
              f"Val Acc: {val_accuracy:.2%}", flush=True)

    #evaluate the held-out test set once training is finished.
    save_evaluation(model, loaders[2], device, history, artifact_dir)
    #save weights on CPU plus the information needed to interpret future predictions.
    checkpoint = {
        "model_state_dict": {name: value.cpu() for name, value in model.state_dict().items()},
        "architecture": "resnet18",
        "class_names": CLASS_NAMES,
        "size_thresholds": thresholds,
        "normalization": NORMALIZATION,
        "hyperparameters": vars(args),
    }
    #keep SageMaker's standard model output and a copy alongside the other artifacts.
    torch.save(checkpoint, model_dir / "model.pth")
    torch.save(checkpoint, artifact_dir / "model.pth")
    #save facility assignments to make the evaluation reproducible.
    pd.concat([frame.assign(split=name) for name, frame in
               zip(("train", "validation", "test"), frames)]).to_csv(
        artifact_dir / "data_splits.csv", index=False
    )
    
    #upload each file separately so metrics and graphs can be opened directly in S3.
    s3 = boto3.client("s3")
    for path in sorted(artifact_dir.iterdir()):
        s3.upload_file(str(path), 
            "atlas-acm-research-f26", 
            f"artifacts/baseline/{job_name}/{path.name}"
        )
    print(
        f"Artifacts uploaded to "
        f"s3://atlas-acm-research-f26/artifacts/baseline/{job_name}/",
        flush=True,
    )



if __name__ == "__main__":
    main()
