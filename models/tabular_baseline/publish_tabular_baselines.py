
from pathlib import Path
import hashlib
import json
import boto3
from botocore.exceptions import ClientError

ROOT = Path("outputs/tabular_baselines")
BUCKET = "atlas-acm-research-f26"
PREFIX = "artifacts/baseline/im3_eia_tabular_v1"
AWS_PROFILE = "ATLAS"
REGION = "us-east-2"

# Safety switches
DRY_RUN = True
UPLOAD = False

MODEL_FILES = {
    "EIA__Dummy.joblib",
    "EIA__LogisticRegression.joblib",
    "EIA__RandomForest.joblib",
    "IM3_EIA__LogisticRegression.joblib",
    "IM3_EIA__RandomForest.joblib",
    "IM3__LogisticRegression.joblib",
    "IM3__RandomForest.joblib",
    "selected_tabular_model.joblib",
}

EVALUATION_FILES = {
    "final_test_classification_report.csv",
    "final_test_confusion_matrix.csv",
    "final_test_metrics.json",
    "validation_macro_f1.png",
    "validation_metrics.csv",
}

METADATA_FILES = {
    "selected_model_metadata.json",
    "split_manifest.csv",
}

# All 15 files must be accounted for
EXPECTED = MODEL_FILES | EVALUATION_FILES | METADATA_FILES

assert ROOT.is_dir(), f"Missing directory: {ROOT}"

actual = {p.name for p in ROOT.iterdir() if p.is_file()}
assert actual == EXPECTED, (
    f"Missing: {EXPECTED - actual}\n"
    f"Unexpected: {actual - EXPECTED}"
)

session = boto3.Session(
    profile_name=AWS_PROFILE,
    region_name=REGION,
)
s3 = session.client("s3")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def destination(name):
    if name in MODEL_FILES:
        folder = "models"
    elif name in EVALUATION_FILES:
        folder = "evaluation"
    else:
        folder = "metadata"
    return f"{PREFIX}/{folder}/{name}"


# Preflight: refuse publication if any destination exists
records = []

for name in sorted(EXPECTED):
    path = ROOT / name
    data = path.read_bytes()
    key = destination(name)

    try:
        s3.head_object(Bucket=BUCKET, Key=key)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        status = e.response.get("ResponseMetadata", {}).get(
            "HTTPStatusCode"
        )
        if code not in ("404", "NoSuchKey", "NotFound") and status != 404:
            raise
    else:
        raise RuntimeError(
            f"Destination already exists; refusing overwrite: s3://{BUCKET}/{key}"
        )

    records.append({
        "filename": name,
        "s3_uri": f"s3://{BUCKET}/{key}",
        "key": key,
        "bytes": len(data),
        "sha256": sha256(data),
    })

print(f"Preflight passed: {len(records)} files")
print(f"Total: {sum(r['bytes'] for r in records) / 1024**2:.2f} MiB")

for r in records:
    print(r["s3_uri"])

if DRY_RUN or not UPLOAD:
    print("\nDRY RUN — no files uploaded.")
else:
    for record in records:
        data = (ROOT / record["filename"]).read_bytes()

        try:
            s3.put_object(
                Bucket=BUCKET,
                Key=record["key"],
                Body=data,
                IfNoneMatch="*",
                Metadata={"sha256": record["sha256"]},
            )
        except ClientError as e:
            raise RuntimeError(
                f"Upload failed for {record['s3_uri']}"
            ) from e

        # Independently read back the S3 object and verify content
        remote = s3.get_object(
            Bucket=BUCKET,
            Key=record["key"],
        )["Body"].read()

        assert sha256(remote) == record["sha256"], (
            f"SHA-256 mismatch: {record['filename']}"
        )

        print(f"VERIFIED: {record['filename']}")

    manifest = {
        "experiment": "im3_eia_tabular_v1",
        "files": records,
    }

    manifest_bytes = json.dumps(
        manifest, indent=2
    ).encode("utf-8")

    manifest_key = f"{PREFIX}/publication_manifest.json"

    s3.put_object(
        Bucket=BUCKET,
        Key=manifest_key,
        Body=manifest_bytes,
        ContentType="application/json",
        IfNoneMatch="*",
    )

    saved_manifest = s3.get_object(
        Bucket=BUCKET,
        Key=manifest_key,
    )["Body"].read()

    assert saved_manifest == manifest_bytes

    print("\nPUBLICATION COMPLETE")
    print(f"Verified {len(records)} artifacts and manifest.")
