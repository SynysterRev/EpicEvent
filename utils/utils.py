from argon2 import PasswordHasher


def hash_password(password):
    ph = PasswordHasher()
    return ph.hash(password)

def verify_password(plain_password, hashed_password):
    ph = PasswordHasher()
    return ph.verify(plain_password, hashed_password)
