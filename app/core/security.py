from passlib.context import CryptContext

bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt_context.verify(password, hashed)