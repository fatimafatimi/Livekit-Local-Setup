import secrets
import hashlib
import base64

code_verifier = secrets.token_urlsafe(64)

digest = hashlib.sha256(code_verifier.encode()).digest()
code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")

print("CODE_VERIFIER =", code_verifier)
print("CODE_CHALLENGE =", code_challenge)