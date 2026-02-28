from app.users.auth import get_password_hash, verify_password


def test_password_hashing():
    password = "SuperSecretPassword123"

    hashed = get_password_hash(password)
    assert hashed != password
    assert len(hashed) > 0

    assert verify_password(password, hashed) is True

    assert verify_password("WrongPassword", hashed) is False
