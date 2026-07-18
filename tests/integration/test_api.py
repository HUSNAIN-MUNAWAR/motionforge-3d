import os
import tempfile
from pathlib import Path

test_db = Path(tempfile.gettempdir()) / f"motionforge-test-{os.getpid()}.db"
test_db.unlink(missing_ok=True)
os.environ["MOTIONFORGE_DATABASE_URL"] = f"sqlite:///{test_db.as_posix()}"
os.environ["MOTIONFORGE_SECRET_KEY"] = "test-secret-key-that-is-longer-than-32-bytes"
from fastapi.testclient import TestClient
from motionforge.main import app

client = TestClient(app)


def test_auth_and_tenant_isolation():
    token = client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "verystrongpass1", "display_name": "Analyst"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org = client.post(
        "/api/v1/organizations", json={"name": "Org A", "slug": "org-a"}, headers=headers
    ).json()
    tenant = {**headers, "X-Organization-ID": org["id"]}
    subject = client.post("/api/v1/subjects", json={"display_name": "ATH-1"}, headers=tenant)
    assert subject.status_code == 201
    assert (
        client.get(
            "/api/v1/subjects",
            headers={**headers, "X-Organization-ID": "00000000-0000-0000-0000-000000000000"},
        ).status_code
        == 403
    )
