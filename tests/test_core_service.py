import pytest
from fastapi.testclient import TestClient

from src.app import app, database
from src.database import Database
from src.models import ProjectStatus
from src.services.core_service import CoreService, CoreValidationError


@pytest.fixture
def core_context(tmp_path):
    test_database = Database(f"sqlite:///{tmp_path / 'core.sqlite3'}")
    session = test_database.session()
    yield CoreService(), session
    session.close()


def test_record_audit_log_persists_tenant_and_details(core_context):
    service, session = core_context

    audit_log = service.record_audit(
        session, "tenant-a", "user-1", "project.created", "project", "42", {"name": "API"}
    )

    assert audit_log.id > 0
    assert audit_log.tenant_id == "tenant-a"
    assert audit_log.details == {"name": "API"}
    assert audit_log.created_at is not None


def test_get_audit_logs_is_tenant_scoped_and_limited(core_context):
    service, session = core_context
    service.record_audit(session, "tenant-a", "user-1", "read", "project", "1")
    service.record_audit(session, "tenant-b", "user-2", "read", "project", "2")

    logs = service.get_audit_logs(session, "tenant-a", limit=1)

    assert len(logs) == 1
    assert logs[0].tenant_id == "tenant-a"


def test_create_and_get_notifications_are_recipient_scoped(core_context):
    service, session = core_context
    notification = service.create_notification(
        session, "tenant-a", "user-1", "project.updated", "Project status changed"
    )
    service.create_notification(session, "tenant-a", "user-2", "project.updated", "Other user")
    service.create_notification(session, "tenant-b", "user-1", "project.updated", "Other tenant")

    notifications = service.get_notifications(session, "tenant-a", "user-1")

    assert notifications == [notification]
    assert notification.is_read is False


def test_mark_notification_read_requires_tenant_and_recipient(core_context):
    service, session = core_context
    notification = service.create_notification(
        session, "tenant-a", "user-1", "alert", "Please review"
    )

    updated = service.mark_notification_read(session, "tenant-a", "user-1", notification.id)

    assert updated.is_read is True
    with pytest.raises(LookupError):
        service.mark_notification_read(session, "tenant-b", "user-1", notification.id)


def test_core_service_rejects_blank_values_and_invalid_limits(core_context):
    service, session = core_context

    with pytest.raises(CoreValidationError):
        service.create_notification(session, "tenant-a", "user-1", "alert", " ")
    with pytest.raises(CoreValidationError):
        service.get_audit_logs(session, "tenant-a", limit=0)


def test_audit_endpoint_requires_tenant_header():
    response = TestClient(app).post(
        "/audit-logs",
        json={
            "actor_id": "user-1",
            "action": "project.created",
            "resource_type": "project",
            "resource_id": "42",
        },
    )

    assert response.status_code == 422


def test_notification_endpoints_create_list_and_mark_read(tmp_path, monkeypatch):
    test_database = Database(f"sqlite:///{tmp_path / 'api.sqlite3'}")
    monkeypatch.setattr("src.app.database", test_database)
    client = TestClient(app)
    headers = {"X-Tenant-ID": "tenant-api"}

    create_response = client.post(
        "/notifications",
        headers=headers,
        json={
            "recipient_id": "user-1",
            "notification_type": "project.updated",
            "message": "Project changed",
        },
    )
    notification_id = create_response.json()["id"]

    list_response = client.get(
        "/notifications", headers=headers, params={"recipient_id": "user-1"}
    )
    read_response = client.patch(
        f"/notifications/{notification_id}/read",
        headers=headers,
        params={"recipient_id": "user-1"},
    )

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200
    assert read_response.json()["is_read"] is True


def test_audit_endpoint_does_not_return_another_tenant_logs(tmp_path, monkeypatch):
    test_database = Database(f"sqlite:///{tmp_path / 'api-audit.sqlite3'}")
    monkeypatch.setattr("src.app.database", test_database)
    client = TestClient(app)

    client.post(
        "/audit-logs",
        headers={"X-Tenant-ID": "tenant-a"},
        json={
            "actor_id": "user-1",
            "action": "project.created",
            "resource_type": "project",
            "resource_id": "1",
        },
    )

    response = client.get("/audit-logs", headers={"X-Tenant-ID": "tenant-b"})

    assert response.status_code == 200
    assert response.json() == []
