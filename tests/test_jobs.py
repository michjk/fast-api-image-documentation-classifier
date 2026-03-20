import asyncio

from app.jobs import service as jobs_service
from app.models import JobStatus


async def _instant_process(job_id, user_id):
    return None


def test_upload_job_returns_job_id(client, monkeypatch):
    monkeypatch.setattr(jobs_service, "process_job_background", _instant_process)
    monkeypatch.setattr(jobs_service, "launch_job", lambda job_id, user_id: asyncio.get_event_loop().create_task(_instant_process(job_id, user_id)))

    register = client.post(
        "/api/v1/auth/register",
        json={"email": "jobs@example.com", "password": "secret123"},
    )
    token = register.json()["access_token"]

    files = [("files", ("docA_1.png", b"file-bytes-1", "image/png"))]
    res = client.post("/api/v1/jobs", headers={"Authorization": f"Bearer {token}"}, files=files)
    assert res.status_code == 202
    body = res.json()
    assert body["status"] == JobStatus.pending.value
    assert "job_id" in body
