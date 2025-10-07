import hashlib
import os

def hash_password(password, salt=None):
    """
    Hash a password for storing using SHA-256 with a random salt.
    If salt is not provided, a new one is generated.
    """
    if salt is None:
        salt = os.urandom(32)  # 32 bytes = 256 bits

    # Hash the password with the salt
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    # Return both salt and hash for storage
    return salt + pwdhash

def verify_password(stored_password, provided_password):
    """
    Verify a stored password against a provided one.
    The stored password contains the salt at the beginning.
    """
    salt = stored_password[:32]  # First 32 bytes are the salt
    stored_hash = stored_password[32:]

    # Hash the provided password with the stored salt
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)

    # Compare the computed hash with the stored hash
    return pwdhash == stored_hash

def convert_to_binary(password_hash):
    """Convert password hash to binary for SQLite storage"""
    return password_hash

def convert_from_binary(binary_hash):
    """Convert binary data from SQLite to password hash"""
    return binary_hash
