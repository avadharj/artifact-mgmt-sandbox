"""
Promote the latest READY version of a model from gamma to prod.

Run:
    MODEL=my-model python examples/promote_to_prod.py

What it does:
    1. Takes the latest READY version from gamma
    2. Uploads the same bytes (no re-serialization) to prod
    3. Returns the new prod version string

The model must already exist in prod (call create_model on the prod client first).
"""
from __future__ import annotations

import os
import sys

from artifact_mgmt import ArtifactMgmtClient

MODEL_NAME = os.environ.get("MODEL")
if not MODEL_NAME:
    print("Usage: MODEL=<model-name> python examples/promote_to_prod.py")
    sys.exit(1)


def main() -> None:
    gamma = ArtifactMgmtClient(stage="gamma")
    prod = ArtifactMgmtClient(stage="prod")

    # Show what we're promoting
    source = gamma.get_latest_version(MODEL_NAME)
    print(f"Promoting '{MODEL_NAME}'")
    print(f"  Source (gamma) : v{source.version}")
    print(f"  Framework      : {source.dep_snapshot.framework.name} {source.dep_snapshot.framework.version}")
    print(f"  Python         : {source.dep_snapshot.python_version}")

    # Ensure model exists in prod
    try:
        prod.get_model(MODEL_NAME)
    except Exception:
        print(f"\nModel '{MODEL_NAME}' does not exist in prod. Creating it...")
        prod.create_model(
            MODEL_NAME,
            framework_hint=source.dep_snapshot.framework.name,
        )
        print("Created.")

    # Promote
    prod_version = gamma.promote_model(MODEL_NAME, dest=prod)
    print(f"\nPromoted to prod version: {prod_version}")

    # Verify in prod
    confirmed = prod.get_version(MODEL_NAME, prod_version)
    print(f"Prod version status: {confirmed.status}")


if __name__ == "__main__":
    main()
