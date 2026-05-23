"""
Quickstart: create a model, save a version, load it back, then clean up.

Run:
    python examples/quickstart.py

Requires: AWS credentials with execute-api:Invoke on the artifact-mgmt API.
"""
from __future__ import annotations

import os
from artifact_mgmt import ArtifactMgmtClient, ModelNotFoundError

STAGE = os.environ.get("ARTIFACT_MGMT_STAGE", "gamma")
MODEL_NAME = "sandbox-quickstart"


def main() -> None:
    client = ArtifactMgmtClient(stage=STAGE)
    print(f"Connected to stage: {STAGE}")

    # 1. Create the model (skip if it already exists)
    try:
        model_record = client.create_model(
            MODEL_NAME,
            framework_hint="pickle",
            description="Sandbox quickstart model",
        )
        print(f"Created model: {model_record.model_name}")
    except Exception as e:
        print(f"Model already exists or error: {e}")

    # 2. Save a plain Python object as a model version (uses pickle serializer)
    native_model = {"weights": [0.1, 0.2, 0.3], "bias": 0.5}
    version = client.save_model(native_model, MODEL_NAME, serializer="pickle")
    print(f"Saved version: {version}")

    # 3. Load it back
    artifact = client.load_model(MODEL_NAME, version=version)
    print(f"Loaded: {artifact}")
    print(f"  model_name : {artifact.model_name}")
    print(f"  version    : {artifact.version}")
    print(f"  framework  : {artifact.dep_snapshot.framework.name}")
    print(f"  model data : {artifact.model}")

    # 4. Confirm round-trip
    assert artifact.model == native_model, "Round-trip mismatch!"
    print("Round-trip check passed.")

    # 5. Cleanup
    client.delete_version(MODEL_NAME, version)
    client.delete_model(MODEL_NAME)
    print(f"Cleaned up model '{MODEL_NAME}'")


if __name__ == "__main__":
    main()
