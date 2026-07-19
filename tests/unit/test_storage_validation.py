from apps.api.motionforge.services.storage import ALLOWED


def test_webm_upload_mime_type_is_allowed_for_public_dataset_workflow():
    assert "video/webm" in ALLOWED
