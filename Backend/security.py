import base64, hashlib, hmac, os, secrets, time

SECRET = os.getenv("AUTH_SECRET", "dev-secret-change-me").encode()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return base64.b64encode(salt + dk).decode()


def verify_password(password: str, stored: str) -> bool:
    raw = base64.b64decode(stored.encode())
    salt, dk = raw[:16], raw[16:]
    return hmac.compare_digest(dk, hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000))


def make_token(user_id: int, ttl: int = 7 * 86400) -> str:
    payload = f"{user_id}:{int(time.time()) + ttl}"
    sig = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{sig}".encode()).decode()
