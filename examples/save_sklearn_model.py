"""
Save and load a scikit-learn LogisticRegression model.

Run:
    pip install scikit-learn joblib
    python examples/save_sklearn_model.py
"""
from __future__ import annotations

import os
import numpy as np
from sklearn.linear_model import LogisticRegression

from artifact_mgmt import ArtifactMgmtClient

STAGE = os.environ.get("ARTIFACT_MGMT_STAGE", "gamma")
MODEL_NAME = "sandbox-sklearn-logreg"


def main() -> None:
    client = ArtifactMgmtClient(stage=STAGE)

    # Train a tiny model
    X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    y = np.array([0, 0, 0, 1])
    model = LogisticRegression().fit(X, y)
    print(f"Trained LogisticRegression: classes={model.classes_}")

    # Create model record
    try:
        client.create_model(MODEL_NAME, framework_hint="sklearn")
    except Exception:
        pass  # already exists

    # Save
    version = client.save_model(model, MODEL_NAME)
    print(f"Saved as version: {version}")

    # Load back
    artifact = client.load_model(MODEL_NAME, version=version)
    print(f"Loaded artifact: {artifact}")

    # Predict
    predictions = artifact.predict(X)
    print(f"Predictions: {predictions}")
    assert list(predictions) == [0, 0, 0, 1]
    print("Predictions correct.")

    # Cleanup
    client.delete_version(MODEL_NAME, version)
    client.delete_model(MODEL_NAME)
    print("Done.")


if __name__ == "__main__":
    main()
