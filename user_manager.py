import os
import json
import base64
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Import KeyManager here to create certificate during registration
from key_manager import KeyManager


class UserManager:
    """Manages multiple user accounts."""

    def __init__(self, users_dir="users"):
        self.users_dir = Path(users_dir)
        self.users_dir.mkdir(exist_ok=True)
        self.users_file = self.users_dir / "users.json"
        self._load_users()

    def _load_users(self):
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                self.users_db = json.load(f)
        else:
            self.users_db = {'users': []}

    def _save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users_db, f, indent=2)

    def _hash_password(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def username_exists(self, username):
        for user in self.users_db['users']:
            if user['username'].lower() == username.lower():
                return True
        return False

    def register_user(self, username, password, full_name=""):
        """
        Register a new user and generate a self-signed certificate.
        
        Args:
            username: Unique username
            password: User password
            full_name: Optional full name
        """
        if not username or len(username) < 3:
            return "Username must be at least 3 characters"
        if self.username_exists(username):
            return "Username already exists"
        if not password or len(password) < 6:
            return "Password must be at least 6 characters"

        salt = os.urandom(16)
        password_hash = self._hash_password(password, salt)

        # Create user directory
        user_dir = self.users_dir / username
        user_dir.mkdir(exist_ok=True)

        # Generate keys and certificate for the user
        key_manager = KeyManager(user_dir=str(user_dir))
        key_manager.generate_key_pair()
        key_manager.generate_self_signed_certificate(username)
        key_manager.save_keystore(password)  # This also saves certificate

        user_record = {
            'username': username,
            'full_name': full_name,
            'password_hash': base64.b64encode(password_hash).decode(),
            'salt': base64.b64encode(salt).decode(),
            'user_dir': str(user_dir),
            'created': self._get_timestamp()
        }

        self.users_db['users'].append(user_record)
        self._save_users()
        return True

    def authenticate_user(self, username, password):
        for user in self.users_db['users']:
            if user['username'].lower() == username.lower():
                salt = base64.b64decode(user['salt'])
                password_hash = self._hash_password(password, salt)
                stored_hash = base64.b64decode(user['password_hash'])
                if password_hash == stored_hash:
                    return user
        return None

    def get_user_dir(self, username):
        return self.users_dir / username

    def list_users(self):
        return [user['username'] for user in self.users_db['users']]

    def get_user_info(self, username):
        for user in self.users_db['users']:
            if user['username'].lower() == username.lower():
                info = user.copy()
                info.pop('password_hash', None)
                info.pop('salt', None)
                return info
        return None

    def update_user_info(self, username, full_name=None):
        """
        Update user information.
        
        Args:
            username: Username
            full_name: New full name (optional)
            
        Returns:
            True if successful, False otherwise
        """
        for user in self.users_db['users']:
            if user['username'].lower() == username.lower():
                if full_name is not None:
                    user['full_name'] = full_name
                self._save_users()
                return True
        return False

    def change_password(self, username, old_password, new_password):
        user_record = self.authenticate_user(username, old_password)
        if not user_record:
            return "Current password is incorrect"
        if not new_password or len(new_password) < 6:
            return "New password must be at least 6 characters"

        salt = os.urandom(16)
        password_hash = self._hash_password(new_password, salt)

        for user in self.users_db['users']:
            if user['username'].lower() == username.lower():
                user['password_hash'] = base64.b64encode(password_hash).decode()
                user['salt'] = base64.b64encode(salt).decode()
                self._save_users()

                # Also update keystore password
                user_dir = self.get_user_dir(username)
                key_manager = KeyManager(user_dir=str(user_dir))
                if key_manager.load_keystore(old_password):
                    key_manager.save_keystore(new_password)
                return True
        return "User not found"

    def delete_user(self, username, password):
        user_record = self.authenticate_user(username, password)
        if not user_record:
            return "Authentication failed"
        self.users_db['users'] = [
            u for u in self.users_db['users']
            if u['username'].lower() != username.lower()
        ]
        self._save_users()
        return True

    def _get_timestamp(self):
        return datetime.now().isoformat()
