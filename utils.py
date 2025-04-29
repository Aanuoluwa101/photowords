import hashlib
import binascii
import secrets

def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2 with a randomly generated or provided salt."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=32)  # 32 bytes = 256 bits
    salt_hex = binascii.hexlify(salt).decode('utf-8')
    hash_hex = binascii.hexlify(dk).decode('utf-8')

    return f"{salt_hex}:{hash_hex}"

def verify_password(stored_hash: str, password_attempt: str) -> bool:
    """Verifies a password against a stored hash."""

    try:
        salt_hex, original_hash_hex = stored_hash.split(":")
        salt = binascii.unhexlify(salt_hex)
        attempt_hash = hash_password(password_attempt, salt).split(":")[1] #get the hash part.
        return attempt_hash == original_hash_hex
    except (ValueError, binascii.Error):
        return False #Handle bad hashes, or salt values.



# Hashing a password
password = "mysecretpassword"
hashed_password = hash_password(password)
print(f"Hashed password: {hashed_password}")

# Verifying a password
password_to_verify = "mysecretpassword"
is_valid = verify_password(hashed_password, password_to_verify)
print(f"Password valid: {is_valid}")

#Verifying a bad password.
password_to_verify = "wrongpassword"
is_valid = verify_password(hashed_password, password_to_verify)
print(f"Password valid: {is_valid}")

#Verifying a bad hash.
bad_hash = "badhash"
is_valid = verify_password(bad_hash, password_to_verify)
print(f"Bad hash valid: {is_valid}")