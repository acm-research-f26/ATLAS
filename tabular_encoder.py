# %% [markdown]
# # ATLAS – Tabular feature encoder (EIA/WRI final dataset → 64-d embeddings)
# Read final tabular CSV from S3 → validate shape → preprocess → MLP encoder → 64-d vector per row.
# Run locally

# %% Config
BUCKET = "atlas-acm-research-f26"
KEY = "dataset/im3_atlas_wri_13scorescombined.csv" 
PROFILE = "ATLAS"

EXPECTED_ROWS = 317                # roughly 
ROW_TOLERANCE = 0.10               # ±10%
MAX_COLS = 40

ID_COLS = ["id", "name", "ref", "operator", "county", "state", "state_abb", "state_id", "county_id", "pfaf_id"]                  
EMB_DIM = 64
SEED = 42

# %% Find the file in S3 
import boto3

session = boto3.Session(profile_name=PROFILE)
s3 = session.client("s3")
for obj in s3.list_objects_v2(Bucket=BUCKET).get("Contents", []):
    if obj["Key"].endswith(".csv"):
        print(f'{obj["Size"]:>12,}  {obj["Key"]}')

# %% Read from S3
import io
import pandas as pd

body = s3.get_object(Bucket=BUCKET, Key=KEY)["Body"].read()
df = pd.read_csv(io.BytesIO(body))
print(df.shape)
df.head()

# %% Validate size and contents
n_rows, n_cols = df.shape
lo, hi = EXPECTED_ROWS * (1 - ROW_TOLERANCE), EXPECTED_ROWS * (1 + ROW_TOLERANCE)

assert 1 <= n_cols <= MAX_COLS, f"Expected 1–{MAX_COLS} columns, got {n_cols}"
if not (lo <= n_rows <= hi):
    print(f"WARNING: {n_rows} rows, expected about {EXPECTED_ROWS}")
else:
    print(f"OK: {n_rows} rows, {n_cols} columns")

dupes = df.duplicated().sum()
print(f"Duplicate rows: {dupes}")

summary = pd.DataFrame({
    "dtype": df.dtypes.astype(str),
    "n_unique": df.nunique(),
    "pct_null": (df.isna().mean() * 100).round(1),
})
print(summary.to_string())

# %% Split columns into ID/numeric/categorical
import numpy as np

if not ID_COLS:
    # object columns that are (nearly) unique per row are identifiers
    ID_COLS = [c for c in df.columns
               if df[c].dtype == object and df[c].nunique() > 0.9 * n_rows]

feature_df = df.drop(columns=ID_COLS)
# drop columns that carry no information
constant = [c for c in feature_df.columns if feature_df[c].nunique(dropna=False) <= 1]
feature_df = feature_df.drop(columns=constant)

num_cols = feature_df.select_dtypes(include=np.number).columns.tolist()
cat_cols = [c for c in feature_df.columns if c not in num_cols]

print("ID cols:      ", ID_COLS)
print("Dropped const:", constant)
print(f"Numeric ({len(num_cols)}):", num_cols)
print(f"Categorical ({len(cat_cols)}):", cat_cols)

# %% Preprocess: impute + scale numeric, one-hot categorical
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]), num_cols),
    ("cat", Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ]), cat_cols),
])

X = preprocess.fit_transform(feature_df).astype(np.float32)
print("Encoded input shape:", X.shape)
assert not np.isnan(X).any(), "NaNs left after preprocessing"

# %% MLP encoder (trained as an autoencoder so the 64-d vector keeps the row's information)
import torch
import torch.nn as nn

torch.manual_seed(SEED)
in_dim = X.shape[1]

class TabularEncoder(nn.Module):
    def __init__(self, in_dim, emb_dim=64, hidden=128, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.LayerNorm(hidden), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden, emb_dim), nn.LayerNorm(emb_dim),
        )
    def forward(self, x):
        return self.net(x)

class AutoEncoder(nn.Module):
    def __init__(self, in_dim, emb_dim=64):
        super().__init__()
        self.encoder = TabularEncoder(in_dim, emb_dim)
        self.decoder = nn.Sequential(nn.Linear(emb_dim, 128), nn.GELU(), nn.Linear(128, in_dim))
    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z), z

model = AutoEncoder(in_dim, EMB_DIM)
print(model)

# %% Train (small dataset → full-batch is fine, holds out 15% to check overfitting)
from sklearn.model_selection import train_test_split

idx_train, idx_val = train_test_split(np.arange(len(X)), test_size=0.15, random_state=SEED)
X_t = torch.from_numpy(X)
opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
loss_fn = nn.MSELoss()

for epoch in range(1, 501):
    model.train()
    opt.zero_grad()
    recon, _ = model(X_t[idx_train])
    loss = loss_fn(recon, X_t[idx_train])
    loss.backward()
    opt.step()
    if epoch % 50 == 0:
        model.eval()
        with torch.no_grad():
            val = loss_fn(model(X_t[idx_val])[0], X_t[idx_val]).item()
        print(f"epoch {epoch:3d}  train {loss.item():.4f}  val {val:.4f}")

# %% Produce 64-d embeddings for every row
model.eval()
with torch.no_grad():
    emb = model.encoder(X_t).numpy()

assert emb.shape == (n_rows, EMB_DIM), emb.shape
emb_df = pd.DataFrame(emb, columns=[f"tab_emb_{i}" for i in range(EMB_DIM)])
if ID_COLS:
    emb_df = pd.concat([df[ID_COLS].reset_index(drop=True), emb_df], axis=1)
print(emb_df.shape)
emb_df.head()

#Save locally
import joblib

emb_df.to_csv("tabular_embeddings_64d.csv", index=False)
torch.save(model.encoder.state_dict(), "tabular_encoder.pt")
joblib.dump(preprocess, "tabular_preprocess.joblib")
print("Saved tabular_embeddings_64d.csv, tabular_encoder.pt, tabular_preprocess.joblib")

# %% Plot setup 
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

df_plot = df.reset_index(drop=True)

# Print good color candidates for plotting
candidates = [c for c in df_plot.columns
              if df_plot[c].dtype == object or df_plot[c].nunique() <= 30]
for c in candidates:
    print(f"{c}: {df_plot[c].nunique()} unique")

COLOR_COL = "ba_code" 

# %% t-SNE: squash 64-d embeddings to 2-D and plot
xy = TSNE(n_components=2, perplexity=30, random_state=42, init="pca").fit_transform(emb)

labels = df_plot[COLOR_COL].astype(str).fillna("missing")
top = labels.value_counts().index[:10]              # top 10 groups get their own color
labels = labels.where(labels.isin(top), "Other")

fig, ax = plt.subplots(figsize=(10, 7))
colors = plt.cm.tab20.colors[::2] + plt.cm.tab20.colors[1::2]
for i, lab in enumerate(sorted(labels.unique())):
    m = (labels == lab).values
    ax.scatter(xy[m, 0], xy[m, 1], s=18, alpha=0.75, label=lab, color=colors[i % 20])
ax.set_title(f"ATLAS tabular embeddings (t-SNE), colored by {COLOR_COL}")
ax.set_xticks([]); ax.set_yticks([])
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(f"tsne_by_{COLOR_COL}.png", dpi=200)
plt.show()


# %% Nearest neighbors
from sklearn.neighbors import NearestNeighbors

nn = NearestNeighbors(n_neighbors=6, metric="cosine").fit(emb)

SITE = 0          
SHOW_COLS = [c for c in ["id", "state", COLOR_COL] if c in df_plot.columns]

dist, idx = nn.kneighbors(emb[[SITE]])
result = df_plot.loc[idx[0], SHOW_COLS].copy()
result["cosine_dist"] = dist[0].round(3)
print("First row = the site itself, the rest = its 5 closest matches")
result




# %% find the correct file 
