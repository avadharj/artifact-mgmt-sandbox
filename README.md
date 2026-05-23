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
