# artifact-mgmt-sandbox

Interactive playground for the Artifact Management Service Python SDK.

Use this repo to explore `save_model`, `load_model`, `promote_model`, and the low-level CRUD API against the live gamma and prod stages.

## Prerequisites

- Python 3.11+
- AWS credentials with access to the `artifact-mgmt` API (IAM user or role with `execute-api:Invoke`)
- The `artifact-mgmt-client` SDK installed (see below)

## Setup

```bash
# 1. Clone this repo
git clone https://github.com/<your-org>/artifact-mgmt-sandbox
cd artifact-mgmt-sandbox

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install the SDK and sandbox dependencies
pip install -r requirements.txt

# 4. Configure AWS credentials (one of):
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
# or: aws configure
# or: aws sso login --profile <profile>

# 5. Set the target stage (optional — defaults to gamma)
export ARTIFACT_MGMT_STAGE=gamma
```

## Running the examples

```bash
# Quickstart: create a model, save a version, load it back
python examples/quickstart.py

# Save a scikit-learn model
python examples/save_sklearn_model.py

# Save a PyTorch model (requires: pip install artifact-mgmt-client[torch])
python examples/save_torch_model.py

# List all models and their latest versions
python examples/list_models.py

# Promote the latest gamma version to prod
python examples/promote_to_prod.py

# Low-level CRUD walkthrough
python examples/crud_walkthrough.py
```

## Stages

| Stage | Purpose | Endpoint |
|---|---|---|
| `gamma` | Pre-prod (default) | `https://idco76hrk9.execute-api.us-east-1.amazonaws.com/gamma` |
| `prod` | Production | `https://afwtpvnxe7.execute-api.us-east-1.amazonaws.com/prod` |

Switch stages:
```python
from artifact_mgmt import ArtifactMgmtClient
client = ArtifactMgmtClient(stage="prod")
```

## Sample run results

All examples below were run against the live **gamma** stage on 2026-05-23.
Stage: `https://idco76hrk9.execute-api.us-east-1.amazonaws.com/gamma`

---

### `quickstart.py` — end-to-end pickle round-trip

**What it does:** Creates a model record, serializes a plain Python dict with the pickle backend, uploads it, loads it back, verifies the data is identical, then deletes everything.

**Input model:**
```python
native_model = {"weights": [0.1, 0.2, 0.3], "bias": 0.5}
```

**Output:**
```
Connected to stage: gamma
Model already exists or error: 409: {"code":"MODEL_ALREADY_EXISTS",...}
Saved version: 1.2
Loaded: ArtifactModel('sandbox-quickstart', version='1.2', ...)
  model_name : sandbox-quickstart
  version    : 1.2
  framework  : pickle
  model data : {'weights': [0.1, 0.2, 0.3], 'bias': 0.5}
Round-trip check passed.
Cleaned up model 'sandbox-quickstart'
```

**Notes:** The 409 on `create_model` is expected and handled — the model record already existed from a previous run. `save_model` always creates a new version regardless. The dict came back byte-for-byte identical after serialize → upload → download → deserialize.

---

### `save_sklearn_model.py` — scikit-learn LogisticRegression round-trip

**What it does:** Trains a `LogisticRegression` on 8 synthetic points, saves it via joblib serialization, loads it back as an `ArtifactModel`, runs `predict()`, and verifies predictions match.

**Input:**
```python
# Training data — two clearly separated clusters
X_train = [[0.1,0.1],[0.2,0.1],[0.1,0.2],[0.2,0.2],   # class 0 (near origin)
           [0.9,0.9],[0.8,0.9],[0.9,0.8],[0.8,0.8]]    # class 1 (far from origin)
y_train  = [0, 0, 0, 0, 1, 1, 1, 1]

# Test points
X_test = [[0.0,0.0], [0.15,0.15], [0.85,0.85], [1.0,1.0]]
```

**Output:**
```
Trained LogisticRegression: classes=[0 1]
Saved as version: 1.2
Loaded artifact: ArtifactModel('sandbox-sklearn-logreg', version='1.2', ...)
Predictions: [0, 0, 1, 1]  (expected [0, 0, 1, 1])
Predictions correct.
Done.
```

**Notes:** sklearn models are serialized with joblib. The `predict()` call on `ArtifactModel` forwards directly to the underlying estimator via `__getattr__`. Version bumps from `1.1` → `1.2` because the model record already existed.

---

### `list_models.py` — paginated model listing

**What it does:** Pages through all models in the stage using `list_models()` and for each one fetches the latest version's dep_snapshot metadata.

**Output:**
```
Stage: gamma

  sandbox-sklearn-logreg
    owner      : AIDA3ESG26YOCTV2DGA3I
    framework  : sklearn
    latest     : v1.1
    status     : ACTIVE
    py_version : 3.12.7
    fw_version : 1.5.1

Total: 1 model(s)
```

**Notes:** `list_models()` returns a lazy `PageIterator` — pages are fetched on demand. `py_version` and `fw_version` are pulled from the `dep_snapshot` captured automatically at `save_model` time, recording the Python and sklearn versions in use when the model was saved.

---

### `crud_walkthrough.py` — raw low-level API

**What it does:** Demonstrates every client method individually without using `save_model`/`load_model`: create model, create version (get presigned S3 URL), PUT directly to S3, confirm, get, get-latest, list, list-models, delete.

**Input:**
```python
data = b"fake-serialized-model-bytes"   # raw bytes — no serializer involved
checksum = base64.b64encode(hashlib.sha256(data).digest()).decode()
# checksum sent to CreateVersion AND as x-amz-checksum-sha256 header on S3 PUT
```

**Output:**
```
1. CreateModel
   Already exists: 409: {"code":"MODEL_ALREADY_EXISTS",...}
2. CreateVersion
   Version: 1.2  status=PENDING
   Upload URL: https://artifact-mgmt-gamma-765726488092.s3.amazonaws.com/sa...
3. S3 PUT (presigned upload)
   Upload status: 200
4. ConfirmVersion
   Confirmed: status=READY
5. GetVersion
   Got: 1.2  download_url present=True
6. GetLatestVersion
   Latest: 1.2
7. ListVersions
   Found 2 version(s)
8. ListModels (first page)
   Found 'sandbox-crud-walkthrough' in listing
9. Cleanup
   Done.
```

**Notes:** The S3 presigned URL is signed by the backend with `x-amz-checksum-sha256` in the required headers — omitting it returns 403. The download URL is only present after `ConfirmVersion` transitions the version from `PENDING` → `READY`. The two versions in step 7 are from this run and a prior run.

---

## Repo layout

```
artifact-mgmt-sandbox/
├── examples/
│   ├── quickstart.py          # end-to-end: create → save → load → delete
│   ├── save_sklearn_model.py  # sklearn LogisticRegression round-trip
│   ├── save_torch_model.py    # PyTorch nn.Linear round-trip
│   ├── list_models.py         # paginate through all models
│   ├── promote_to_prod.py     # gamma → prod promotion
│   └── crud_walkthrough.py    # raw CRUD without save_model/load_model
├── requirements.txt           # pinned SDK + sklearn for examples
└── README.md
```
