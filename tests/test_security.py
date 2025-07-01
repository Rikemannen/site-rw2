from app.utils import security

def test_hash_and_verify_password():
    password = "supersecret123"
    hashed = security.hash_password(password)
    assert hashed != password
    assert security.verify_password(hashed, password)
    assert not security.verify_password(hashed, "wrongpassword")
