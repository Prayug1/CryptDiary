import os
import json
import base64
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class KeyManager:
    """Manages RSA key pairs with password-protected storage and X.509 certificates."""

    def __init__(self, keystore_path="keystore.enc", user_dir=None):
        """
        Initialize KeyManager

        Args:
            keystore_path: Path to the encrypted keystore file (relative to user_dir if provided)
            user_dir: User-specific directory for multi-user support
        """
        if user_dir:
            self.keystore_path = os.path.join(user_dir, keystore_path)
            self.cert_path = os.path.join(user_dir, "certificate.pem")
        else:
            self.keystore_path = keystore_path
            self.cert_path = "certificate.pem"
        
        # Global revocation list (shared across all users)
        self.global_revoked_path = "revoked_certificates.json"
        self.private_key = None
        self.public_key = None
        self.certificate = None

    def generate_key_pair(self, key_size=2048):
        """Generate a new RSA key pair."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def generate_self_signed_certificate(self, subject_name):
        """
        Generate a self-signed X.509 certificate for the user.

        Args:
            subject_name: Common name (e.g., username)
        """
        if not self.private_key:
            raise ValueError("Generate key pair first.")

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
        ])
        self.certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            self.public_key
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)  # 1 year validity
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).sign(self.private_key, hashes.SHA256(), default_backend())

    def _derive_key_from_password(self, password, salt):
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def save_keystore(self, password):
        """
        Save keys and certificate to password-protected keystore.

        Args:
            password: Password to encrypt the keystore
        """
        if not self.private_key:
            raise ValueError("No keys to save. Generate keys first.")

        # Serialize private key
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Serialize certificate if exists
        cert_pem = None
        if self.certificate:
            cert_pem = self.certificate.public_bytes(serialization.Encoding.PEM)

        # Create keystore data
        keystore_data = {
            'private_key': base64.b64encode(private_pem).decode(),
            'public_key': base64.b64encode(public_pem).decode(),
        }
        if cert_pem:
            keystore_data['certificate'] = base64.b64encode(cert_pem).decode()

        # Generate random salt and IV
        salt = os.urandom(16)
        iv = os.urandom(16)

        # Derive encryption key from password
        key = self._derive_key_from_password(password, salt)

        # Encrypt keystore data
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Convert to JSON and pad
        json_data = json.dumps(keystore_data).encode()
        padding_length = 16 - (len(json_data) % 16)
        padded_data = json_data + bytes([padding_length] * padding_length)

        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Save encrypted keystore
        keystore = {
            'salt': base64.b64encode(salt).decode(),
            'iv': base64.b64encode(iv).decode(),
            'data': base64.b64encode(encrypted_data).decode()
        }

        with open(self.keystore_path, 'w') as f:
            json.dump(keystore, f, indent=2)

        # Also save certificate separately for easy access (optional)
        if self.certificate:
            with open(self.cert_path, 'wb') as f:
                f.write(cert_pem)

    def load_keystore(self, password):
        """
        Load keys and certificate from password-protected keystore.

        Args:
            password: Password to decrypt the keystore

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.keystore_path):
            return False

        try:
            with open(self.keystore_path, 'r') as f:
                keystore = json.load(f)

            salt = base64.b64decode(keystore['salt'])
            iv = base64.b64decode(keystore['iv'])
            encrypted_data = base64.b64decode(keystore['data'])

            key = self._derive_key_from_password(password, salt)

            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

            padding_length = decrypted_padded[-1]
            decrypted_data = decrypted_padded[:-padding_length]

            keystore_data = json.loads(decrypted_data.decode())

            # Load private key
            private_pem = base64.b64decode(keystore_data['private_key'])
            self.private_key = serialization.load_pem_private_key(
                private_pem,
                password=None,
                backend=default_backend()
            )

            # Load public key
            public_pem = base64.b64decode(keystore_data['public_key'])
            self.public_key = serialization.load_pem_public_key(
                public_pem,
                backend=default_backend()
            )

            # Load certificate if present
            if 'certificate' in keystore_data:
                cert_pem = base64.b64decode(keystore_data['certificate'])
                self.certificate = x509.load_pem_x509_certificate(cert_pem, default_backend())
            else:
                self.certificate = None

            return True

        except Exception as e:
            print(f"Error loading keystore: {e}")
            return False

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key

    def get_certificate(self):
        return self.certificate

    def get_certificate_serial(self):
        """Get the serial number of the current certificate."""
        if self.certificate:
            return str(self.certificate.serial_number)
        return None

    def export_public_key_pem(self):
        if not self.public_key:
            return None
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()

    def export_private_key_pem(self, password=None):
        """
        Export private key in PEM format.
        WARNING: This exports the private key! Use with caution.
        
        Args:
            password: If provided, encrypt the private key with this password
            
        Returns:
            PEM-encoded private key as string
        """
        if not self.private_key:
            return None
        
        if password:
            # Encrypt the private key with password
            encryption_alg = serialization.BestAvailableEncryption(password.encode())
        else:
            encryption_alg = serialization.NoEncryption()
            
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_alg
        )
        return pem.decode()

    def export_certificate_pem(self):
        if not self.certificate:
            return None
        return self.certificate.public_bytes(serialization.Encoding.PEM).decode()

    def get_certificate_details(self):
        """
        Get detailed certificate information as a dictionary.
        
        Returns:
            Dictionary with certificate details or None
        """
        if not self.certificate:
            return None
        
        subject = self.certificate.subject
        issuer = self.certificate.issuer
        
        # Extract common name from subject
        cn = subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        cn_value = cn[0].value if cn else "Unknown"
        
        # Extract organization if present (not in self-signed, but for completeness)
        org = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
        org_value = org[0].value if org else "None"
        
        # Get key algorithm and size
        public_key = self.certificate.public_key()
        if isinstance(public_key, rsa.RSAPublicKey):
            key_size = public_key.key_size
            key_algorithm = f"RSA {key_size}"
        else:
            key_algorithm = "Unknown"
        
        return {
            'subject': cn_value,
            'issuer': cn_value,  # Self-signed, so same as subject
            'serial_number': str(self.certificate.serial_number),
            'not_valid_before': self.certificate.not_valid_before.isoformat(),
            'not_valid_after': self.certificate.not_valid_after.isoformat(),
            'key_algorithm': key_algorithm,
            'signature_algorithm': self.certificate.signature_algorithm_oid._name,
            'version': self.certificate.version.value,
            'organization': org_value,
            'is_ca': self.certificate.extensions.get_extension_for_oid(x509.oid.ExtensionOID.BASIC_CONSTRAINTS).value.ca if self.certificate.extensions.get_extension_for_oid(x509.oid.ExtensionOID.BASIC_CONSTRAINTS) else False
        }

    def get_public_key_details(self):
        """
        Get detailed public key information.
        
        Returns:
            Dictionary with public key details or None
        """
        if not self.public_key:
            return None
        
        if isinstance(self.public_key, rsa.RSAPublicKey):
            numbers = self.public_key.public_numbers()
            return {
                'algorithm': 'RSA',
                'key_size': self.public_key.key_size,
                'public_exponent': numbers.e,
                'modulus_length': numbers.n.bit_length(),
                'pem': self.export_public_key_pem()
            }
        else:
            return {
                'algorithm': 'Unknown',
                'pem': self.export_public_key_pem()
            }

    # --- Global Revocation methods ---
    def _load_global_revoked(self):
        """Load the global certificate revocation list."""
        if os.path.exists(self.global_revoked_path):
            with open(self.global_revoked_path, 'r') as f:
                return json.load(f)
        return {'revoked': []}

    def _save_global_revoked(self, revoked_data):
        """Save the global certificate revocation list."""
        with open(self.global_revoked_path, 'w') as f:
            json.dump(revoked_data, f, indent=2)

    def revoke_certificate(self, serial_number, username=None):
        """
        Add a certificate serial number to the global revocation list.
        
        Args:
            serial_number: Certificate serial number to revoke
            username: Username who revoked it (for audit)
        """
        revoked = self._load_global_revoked()
        
        # Check if already revoked
        for entry in revoked['revoked']:
            if entry['serial'] == serial_number:
                return False
        
        # Add to revocation list with timestamp
        revoked['revoked'].append({
            'serial': serial_number,
            'revoked_by': username if username else 'unknown',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
        self._save_global_revoked(revoked)
        return True

    def is_revoked(self, serial_number):
        """
        Check if a certificate serial number is revoked globally.
        
        Args:
            serial_number: Certificate serial number to check
            
        Returns:
            True if revoked, False otherwise
        """
        revoked = self._load_global_revoked()
        for entry in revoked['revoked']:
            if entry['serial'] == serial_number:
                return True
        return False

    def get_revoked_certificates(self):
        """Get the list of all revoked certificates."""
        revoked = self._load_global_revoked()
        return revoked['revoked']
