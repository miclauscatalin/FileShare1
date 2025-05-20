import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Schimbă calea dacă folosești alt director
PRIVATE_PEM = "/www/private_key.pem"
PUBLIC_PEM  = "/www/public_key.pem"

# --- public key ---
with open(PUBLIC_PEM, "rb") as f:
    pub = serialization.load_pem_public_key(f.read(), backend=default_backend())
    raw_pub = pub.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    vapid_public = base64.urlsafe_b64encode(raw_pub).rstrip(b"=").decode("ascii")

# --- private key ---
with open(PRIVATE_PEM, "rb") as f:
    priv = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    # P-256 private values sunt pe 32 de octeți
    priv_num  = priv.private_numbers().private_value
    raw_priv  = priv_num.to_bytes(32, byteorder="big")
    vapid_private = base64.urlsafe_b64encode(raw_priv).rstrip(b"=").decode("ascii")

print("VAPID_PUBLIC_KEY =", vapid_public)
print("VAPID_PRIVATE_KEY =", vapid_private)
