from src.services.auth_service import hash_password, verify_password


def test_hash_password_verifies_original_password():
    stored_hash = hash_password("clave-segura")

    assert verify_password("clave-segura", stored_hash)
    assert not verify_password("otra-clave", stored_hash)
