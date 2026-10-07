"""Smoke tests: the app factory builds and core pages respond."""
import pytest

from app import create_app, db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.chdir(tmp_path)
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        db.create_all()
    return app.test_client()


def test_app_factory_registers_blueprints(client):
    rules = {rule.endpoint for rule in client.application.url_map.iter_rules()}
    assert "upload.upload" in rules


def test_home_page_responds(client):
    response = client.get("/")
    assert response.status_code in (200, 302)


def test_photo_upload_does_not_crash(client):
    """Regression: the upload handler used uploader_name/user_identifier before assigning them."""
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "white").save(buf, format="PNG")
    buf.seek(0)
    response = client.post(
        "/upload/",
        data={"photo": (buf, "test.png"), "uploader_name": "Tester"},
        content_type="multipart/form-data",
    )
    assert response.status_code in (200, 302)
