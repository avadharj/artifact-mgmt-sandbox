"""
List all models in the stage and show their latest version info.

Run:
    python examples/list_models.py
"""
from __future__ import annotations

import os
from artifact_mgmt import ArtifactMgmtClient, VersionNotFoundError

STAGE = os.environ.get("ARTIFACT_MGMT_STAGE", "gamma")


def main() -> None:
    client = ArtifactMgmtClient(stage=STAGE)
    print(f"Stage: {STAGE}\n")

    count = 0
    for model in client.list_models():
        count += 1
        print(f"  {model.model_name}")
        print(f"    owner      : {model.owner}")
        print(f"    framework  : {model.framework_hint or '(unset)'}")
        print(f"    latest     : v{model.latest_major}.{model.latest_minor}")
        print(f"    status     : {model.status}")

        try:
            latest = client.get_latest_version(model.model_name)
            print(f"    py_version : {latest.dep_snapshot.python_version}")
            print(f"    fw_version : {latest.dep_snapshot.framework.version}")
        except VersionNotFoundError:
            print(f"    (no READY version)")
        print()

    if count == 0:
        print("No models found. Run quickstart.py to create one.")
    else:
        print(f"Total: {count} model(s)")


if __name__ == "__main__":
    main()
