"""
Save and load a PyTorch nn.Linear model.

Run:
    pip install artifact-mgmt-client[torch]   # installs torch + pytorch-lightning
    python examples/save_torch_model.py
"""
from __future__ import annotations

import os
import torch
import torch.nn as nn

from artifact_mgmt import ArtifactMgmtClient

STAGE = os.environ.get("ARTIFACT_MGMT_STAGE", "gamma")
MODEL_NAME = "sandbox-torch-linear"


def main() -> None:
    client = ArtifactMgmtClient(stage=STAGE)

    # Build a tiny model
    model = nn.Linear(4, 2)
    print(f"Model: {model}")

    # Create model record
    try:
        client.create_model(MODEL_NAME, framework_hint="pytorch")
    except Exception:
        pass

    # Save
    version = client.save_model(model, MODEL_NAME)
    print(f"Saved as version: {version}")

    # Load back
    artifact = client.load_model(MODEL_NAME, version=version)
    print(f"Loaded: {artifact}")
    print(f"Framework: {artifact.dep_snapshot.framework.name} {artifact.dep_snapshot.framework.version}")

    # Freeze first layer and check fine-tune params
    artifact.freeze(n_layers=1)
    trainable = artifact.fine_tune_params()
    print(f"Trainable params after freeze(1): {len(trainable)}")

    # Inference
    X = torch.randn(3, 4)
    out = artifact.predict(X)
    print(f"Output shape: {out.shape}")
    assert out.shape == (3, 2)
    print("Shape check passed.")

    # Cleanup
    client.delete_version(MODEL_NAME, version)
    client.delete_model(MODEL_NAME)
    print("Done.")


if __name__ == "__main__":
    main()
