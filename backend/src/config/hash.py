import bcrypt
from passlib.context import CryptContext

from backend.src.config.logging_config import log_function


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @log_function
    def hash_password(self, password: str) -> str:
        """
        Hash the given password using bcrypt.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password.

        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    @log_function
    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to verify against.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    @log_function
    def get_password_hash(self, password):
        """
            Hash a plain password.

            Args:
                password (str): The plain text password to hash.

            Returns:
                str: The hashed password.
        """
        return self.pwd_context.hash(password)

hash_handler = Hash()
