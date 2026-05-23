"""
Low-level CRUD walkthrough — demonstrates every client method without save_model/load_model.

Run:
    python examples/crud_walkthrough.py

This shows the raw request/response cycle: create model, create version,
upload bytes manually to the presigned URL, confirm, list, get latest, delete.
"""
from __future__ import annotations

import hashlib
import base64
import os
import uuid
import requests

from artifact_mgmt import ArtifactMgmtClient, DepSnapshot, FrameworkInfo

STAGE = os.environ.get("ARTIFACT_MGMT_STAGE", "gamma")
MODEL_NAME = "sandbox-crud-walkthrough"

FAKE_SNAPSHOT = DepSnapshot(
    python_version="3.11.0",
    framework=FrameworkInfo(name="pickle", version="1.0.0"),
    packages={},
    os="darwin-arm64",
    captured_at="2026-01-01T00:00:00Z",
)


def main() -> None:
    client = ArtifactMgmtClient(stage=STAGE)

    # 1. Create model
    print("1. CreateModel")
    try:
        m = client.create_model(MODEL_NAME, framework_hint="pickle")
        print(f"   Created: {m.model_name} (owner={m.owner})")
    except Exception as e:
        print(f"   Already exists: {e}")

    # 2. Create version (get upload URL)
    print("2. CreateVersion")
    data = b"fake-serialized-model-bytes"
    checksum = base64.b64encode(hashlib.sha256(data).digest()).decode()
    version_obj = client._create_version(
        MODEL_NAME,
        idempotency_key=str(uuid.uuid4()),
        dep_snapshot=FAKE_SNAPSHOT,
        checksum_sha256=checksum,
    )
    print(f"   Version: {version_obj.version}  status={version_obj.status}")
    print(f"   Upload URL: {version_obj.upload_url[:60]}...")

    # 3. Upload bytes directly to presigned URL
    # x-amz-checksum-sha256 is signed into the presigned URL by the backend and must be sent
    print("3. S3 PUT (presigned upload)")
    resp = requests.put(
        version_obj.upload_url,
        data=data,
        headers={
            "Content-Type": "application/octet-stream",
            "x-amz-checksum-sha256": checksum,
        },
    )
    resp.raise_for_status()
    print(f"   Upload status: {resp.status_code}")

    # 4. Confirm
    print("4. ConfirmVersion")
    confirmed = client._confirm_version(MODEL_NAME, version_obj.version)
    print(f"   Confirmed: status={confirmed.status}")

    # 5. Get version
    print("5. GetVersion")
    v = client.get_version(MODEL_NAME, version_obj.version)
    print(f"   Got: {v.version}  download_url present={v.download_url is not None}")

    # 6. Get latest
    print("6. GetLatestVersion")
    latest = client.get_latest_version(MODEL_NAME)
    print(f"   Latest: {latest.version}")

    # 7. List versions
    print("7. ListVersions")
    all_versions = list(client.list_versions(MODEL_NAME))
    print(f"   Found {len(all_versions)} version(s)")

    # 8. List models
    print("8. ListModels (first page)")
    for model in client.list_models():
        if model.model_name == MODEL_NAME:
            print(f"   Found '{model.model_name}' in listing")
            break

    # 9. Cleanup
    print("9. Cleanup")
    client.delete_version(MODEL_NAME, version_obj.version)
    client.delete_model(MODEL_NAME)
    print("   Done.")


if __name__ == "__main__":
    main()
