import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.exceptions import InvalidSignature


class CryptoManager:
    """Manages cryptographic operations for diary entries."""

    def __init__(self, key_manager):
        """
        Initialize CryptoManager

        Args:
            key_manager: KeyManager instance with loaded keys and certificate
        """
        self.key_manager = key_manager

    def encrypt_entry(self, plaintext):
        """
        Encrypt diary entry using hybrid encryption (AES + RSA)

        Args:
            plaintext: Plain text diary entry

        Returns:
            Dictionary containing encrypted data and metadata
        """
        aes_key = os.urandom(32)  # 256-bit key
        iv = os.urandom(16)

        # AES-CBC encryption
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        plaintext_bytes = plaintext.encode()
        padding_length = 16 - (len(plaintext_bytes) % 16)
        padded_plaintext = plaintext_bytes + bytes([padding_length] * padding_length)

        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        # Encrypt AES key with RSA public key
        public_key = self.key_manager.get_public_key()
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return {
            'encrypted_key': base64.b64encode(encrypted_aes_key).decode(),
            'iv': base64.b64encode(iv).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def decrypt_entry(self, encrypted_data):
        """
        Decrypt diary entry

        Args:
            encrypted_data: Dictionary containing encrypted data

        Returns:
            Decrypted plaintext
        """
        try:
            encrypted_aes_key = base64.b64decode(encrypted_data['encrypted_key'])
            iv = base64.b64decode(encrypted_data['iv'])
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])

            private_key = self.key_manager.get_private_key()
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            padding_length = padded_plaintext[-1]
            plaintext = padded_plaintext[:-padding_length]

            return plaintext.decode()

        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

    def _prepare_signed_data(self, data):
        """
        Prepare data for signing by including a timestamp to prevent replay attacks.
        """
        if isinstance(data, str):
            data = data.encode()
        # Create a signed structure with timestamp
        signed_structure = {
            'data': base64.b64encode(data).decode() if isinstance(data, bytes) else data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        return json.dumps(signed_structure, sort_keys=True).encode()

    def sign_entry(self, data):
        """
        Create digital signature for diary entry (includes timestamp for replay protection).

        Args:
            data: Data to sign (string or bytes)

        Returns:
            Dictionary with signature, timestamp, and certificate serial number
        """
        prepared = self._prepare_signed_data(data)
        private_key = self.key_manager.get_private_key()
        signature = private_key.sign(
            prepared,
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # Return signature and the timestamp used
        signed_structure = json.loads(prepared.decode())
        
        # Include certificate serial number for revocation checking
        cert_serial = self.key_manager.get_certificate_serial()
        
        return {
            'signature': base64.b64encode(signature).decode(),
            'signed_timestamp': signed_structure['timestamp'],
            'cert_serial': cert_serial
        }

    def verify_signature(self, data, signature_b64, timestamp, cert_serial=None, public_key=None, certificate=None):
        """
        Verify digital signature using either a public key or a certificate.
        Also checks if the certificate has been revoked.

        Args:
            data: Original data (string or bytes)
            signature_b64: Base64-encoded signature
            timestamp: The timestamp that was signed (ISO string)
            cert_serial: Certificate serial number (for revocation check)
            public_key: RSA public key (optional, if certificate not provided)
            certificate: X.509 certificate (optional)

        Returns:
            Tuple (is_valid, is_revoked) where is_valid is signature validity,
            and is_revoked indicates if the certificate has been revoked.
        """
        try:
            # First check if certificate is revoked
            is_revoked = False
            if cert_serial:
                is_revoked = self.key_manager.is_revoked(cert_serial)
                if is_revoked:
                    print(f"Certificate {cert_serial} has been revoked")
            
            # Reconstruct the signed structure
            if isinstance(data, str):
                data = data.encode()
            signed_structure = {
                'data': base64.b64encode(data).decode() if isinstance(data, bytes) else data,
                'timestamp': timestamp
            }
            prepared = json.dumps(signed_structure, sort_keys=True).encode()

            signature = base64.b64decode(signature_b64)

            # Get public key from certificate if provided
            if certificate:
                pub_key = certificate.public_key()
            elif public_key:
                pub_key = public_key
            else:
                pub_key = self.key_manager.get_public_key()

            pub_key.verify(
                signature,
                prepared,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # Optional: check timestamp freshness (e.g., not older than 30 days)
            try:
                sig_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                now = datetime.utcnow().replace(tzinfo=sig_time.tzinfo)
                if (now - sig_time).days > 30:
                    print("Warning: Signature timestamp is older than 30 days.")
            except:
                pass  # Ignore timestamp parsing errors

            return True, is_revoked

        except InvalidSignature:
            return False, False
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False, False

    def encrypt_and_sign(self, plaintext):
        """
        Encrypt and sign diary entry with replay protection.

        Returns:
            Dictionary with encrypted data, signature, timestamp, and certificate serial.
        """
        encrypted = self.encrypt_entry(plaintext)
        signature_info = self.sign_entry(encrypted['ciphertext'])
        encrypted['signature'] = signature_info['signature']
        encrypted['signed_timestamp'] = signature_info['signed_timestamp']
        encrypted['cert_serial'] = signature_info['cert_serial']
        return encrypted

    def verify_and_decrypt(self, encrypted_data):
        """
        Verify signature and decrypt diary entry.
        Also checks if the signer's certificate has been revoked.

        Returns:
            Tuple (plaintext, is_valid, is_revoked)
        """
        is_valid = False
        is_revoked = False
        
        if 'signature' in encrypted_data and 'signed_timestamp' in encrypted_data:
            cert_serial = encrypted_data.get('cert_serial')
            # Verify signature using own public key
            is_valid, is_revoked = self.verify_signature(
                encrypted_data['ciphertext'],
                encrypted_data['signature'],
                encrypted_data['signed_timestamp'],
                cert_serial=cert_serial
            )
        
        plaintext = self.decrypt_entry(encrypted_data)
        return plaintext, is_valid, is_revoked

    # --- Export / Import for secure sharing ---
    def export_entry(self, entry_id, metadata, encrypted_data):
        """
        Package an entry for secure export, including the signer's certificate.
        """
        cert_pem = self.key_manager.export_certificate_pem()
        if not cert_pem:
            raise ValueError("No certificate available to export.")

        package = {
            'entry_id': entry_id,
            'title': metadata['title'],
            'created': metadata['created'],
            'encrypted_data': encrypted_data,
            'signer_certificate': cert_pem
        }
        return package

    def import_entry(self, package):
        """
        Import an entry package, verifying the signer's certificate and signature.
        Also checks if the certificate has been revoked.

        Returns:
            Tuple (metadata_dict, encrypted_data, is_valid, is_revoked, cert)
        """
        # Load certificate from package
        cert_pem = package['signer_certificate'].encode()
        cert = x509.load_pem_x509_certificate(cert_pem, default_backend())

        # Check revocation using global list
        cert_serial = str(cert.serial_number)
        is_revoked = self.key_manager.is_revoked(cert_serial)

        # Verify signature using the certificate's public key
        enc_data = package['encrypted_data']
        sig_valid, _ = self.verify_signature(
            enc_data['ciphertext'],
            enc_data['signature'],
            enc_data['signed_timestamp'],
            cert_serial=cert_serial,
            certificate=cert
        )

        # For metadata, we create a minimal structure
        metadata = {
            'title': package['title'],
            'created': package['created'],
            'imported_from': cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        }
        return metadata, package['encrypted_data'], sig_valid, is_revoked, cert
