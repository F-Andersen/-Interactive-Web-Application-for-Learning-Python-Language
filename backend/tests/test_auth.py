from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password


def test_password_hash_roundtrip():
    password_hash = get_password_hash("student123")
    assert verify_password("student123", password_hash)
    assert not verify_password("wrong", password_hash)


def test_jwt_roundtrip():
    token = create_access_token("42")
    assert decode_access_token(token) == "42"
