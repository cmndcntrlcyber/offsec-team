"""
Cryptographic utilities for cybersecurity AI workflow integration.

This module provides encryption, decryption, digital signatures, and other
cryptographic operations for secure data handling and communication.
"""

import os
import secrets
import hashlib
import logging
from typing import Any, Dict, Optional, Tuple, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hmac
import base64


class EncryptionError(Exception):
    """Exception raised for encryption-related errors."""
    pass


class DecryptionError(Exception):
    """Exception raised for decryption-related errors."""
    pass


class SignatureError(Exception):
    """Exception raised for digital signature errors."""
    pass


class CryptoManager:
    """
    Cryptographic manager providing encryption, decryption, and digital signature services.
    Supports both symmetric and asymmetric cryptography operations.
    """
    
    def __init__(self):
        """Initialize the crypto manager."""
        self.backend = default_backend()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("CryptoManager")
    
    def generate_key(self, key_type: str = "fernet") -> bytes:
        """
        Generate a cryptographic key.
        
        Args:
            key_type: Type of key to generate ("fernet", "aes256", "random")
            
        Returns:
            Generated key bytes
            
        Raises:
            ValueError: If key_type is not supported
        """
        if key_type == "fernet":
            return Fernet.generate_key()
        elif key_type == "aes256":
            return secrets.token_bytes(32)  # 256-bit key
        elif key_type == "random":
            return secrets.token_bytes(32)
        else:
            raise ValueError(f"Unsupported key type: {key_type}")
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None,
                                key_length: int = 32, iterations: int = 100000) -> Tuple[bytes, bytes]:
        """
        Derive a cryptographic key from a password using PBKDF2.
        
        Args:
            password: Password string
            salt: Salt bytes (generated if not provided)
            key_length: Desired key length in bytes
            iterations: Number of iterations for PBKDF2
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
            backend=self.backend
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def derive_key_scrypt(self, password: str, salt: Optional[bytes] = None,
                         key_length: int = 32, n: int = 2**14, r: int = 8, p: int = 1) -> Tuple[bytes, bytes]:
        """
        Derive a cryptographic key from a password using Scrypt.
        
        Args:
            password: Password string
            salt: Salt bytes (generated if not provided)
            key_length: Desired key length in bytes
            n: CPU/memory cost parameter
            r: Block size parameter
            p: Parallelization parameter
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            n=n,
            r=r,
            p=p,
            backend=self.backend
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def encrypt_fernet(self, data: Union[str, bytes], key: bytes) -> str:
        """
        Encrypt data using Fernet symmetric encryption.
        
        Args:
            data: Data to encrypt (string or bytes)
            key: Fernet encryption key
            
        Returns:
            Base64-encoded encrypted data
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            if isinstance(data, str):
                data = data.encode()
            
            f = Fernet(key)
            encrypted_data = f.encrypt(data)
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"Fernet encryption error: {str(e)}")
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt_fernet(self, encrypted_data: str, key: bytes) -> bytes:
        """
        Decrypt data using Fernet symmetric encryption.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            key: Fernet decryption key
            
        Returns:
            Decrypted data bytes
            
        Raises:
            DecryptionError: If decryption fails
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_bytes)
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Fernet decryption error: {str(e)}")
            raise DecryptionError(f"Decryption failed: {str(e)}")
    
    def encrypt_aes_gcm(self, data: Union[str, bytes], key: bytes, 
                       associated_data: Optional[bytes] = None) -> Dict[str, str]:
        """
        Encrypt data using AES-GCM (Galois/Counter Mode).
        
        Args:
            data: Data to encrypt
            key: 256-bit encryption key
            associated_data: Additional authenticated data
            
        Returns:
            Dictionary containing encrypted data, nonce, and tag (all base64-encoded)
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            if isinstance(data, str):
                data = data.encode()
            
            # Generate a random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce),
                backend=self.backend
            )
            
            encryptor = cipher.encryptor()
            
            # Add associated data if provided
            if associated_data:
                encryptor.authenticate_additional_data(associated_data)
            
            # Encrypt the data
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            return {
                "ciphertext": base64.b64encode(ciphertext).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "tag": base64.b64encode(encryptor.tag).decode()
            }
            
        except Exception as e:
            self.logger.error(f"AES-GCM encryption error: {str(e)}")
            raise EncryptionError(f"AES-GCM encryption failed: {str(e)}")
    
    def decrypt_aes_gcm(self, encrypted_data: Dict[str, str], key: bytes,
                       associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using AES-GCM.
        
        Args:
            encrypted_data: Dictionary containing ciphertext, nonce, and tag
            key: 256-bit decryption key
            associated_data: Additional authenticated data
            
        Returns:
            Decrypted data bytes
            
        Raises:
            DecryptionError: If decryption fails
        """
        try:
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            nonce = base64.b64decode(encrypted_data["nonce"])
            tag = base64.b64decode(encrypted_data["tag"])
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=self.backend
            )
            
            decryptor = cipher.decryptor()
            
            # Add associated data if provided
            if associated_data:
                decryptor.authenticate_additional_data(associated_data)
            
            # Decrypt the data
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            self.logger.error(f"AES-GCM decryption error: {str(e)}")
            raise DecryptionError(f"AES-GCM decryption failed: {str(e)}")
    
    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate an RSA key pair.
        
        Args:
            key_size: RSA key size in bits (2048, 3072, or 4096)
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        if key_size not in [2048, 3072, 4096]:
            raise ValueError("Key size must be 2048, 3072, or 4096 bits")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        self.logger.info(f"Generated RSA key pair ({key_size} bits)")
        return private_pem, public_pem
    
    def encrypt_rsa(self, data: Union[str, bytes], public_key_pem: bytes) -> str:
        """
        Encrypt data using RSA public key encryption.
        
        Args:
            data: Data to encrypt (limited by key size)
            public_key_pem: RSA public key in PEM format
            
        Returns:
            Base64-encoded encrypted data
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            if isinstance(data, str):
                data = data.encode()
            
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=self.backend
            )
            
            # Encrypt using OAEP padding
            ciphertext = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return base64.b64encode(ciphertext).decode()
            
        except Exception as e:
            self.logger.error(f"RSA encryption error: {str(e)}")
            raise EncryptionError(f"RSA encryption failed: {str(e)}")
    
    def decrypt_rsa(self, encrypted_data: str, private_key_pem: bytes) -> bytes:
        """
        Decrypt data using RSA private key decryption.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            private_key_pem: RSA private key in PEM format
            
        Returns:
            Decrypted data bytes
            
        Raises:
            DecryptionError: If decryption fails
        """
        try:
            ciphertext = base64.b64decode(encrypted_data.encode())
            
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=self.backend
            )
            
            # Decrypt using OAEP padding
            plaintext = private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return plaintext
            
        except Exception as e:
            self.logger.error(f"RSA decryption error: {str(e)}")
            raise DecryptionError(f"RSA decryption failed: {str(e)}")
    
    def sign_rsa(self, data: Union[str, bytes], private_key_pem: bytes) -> str:
        """
        Create a digital signature using RSA private key.
        
        Args:
            data: Data to sign
            private_key_pem: RSA private key in PEM format
            
        Returns:
            Base64-encoded signature
            
        Raises:
            SignatureError: If signing fails
        """
        try:
            if isinstance(data, str):
                data = data.encode()
            
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=self.backend
            )
            
            # Create signature using PSS padding
            signature = private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return base64.b64encode(signature).decode()
            
        except Exception as e:
            self.logger.error(f"RSA signing error: {str(e)}")
            raise SignatureError(f"RSA signing failed: {str(e)}")
    
    def verify_rsa_signature(self, data: Union[str, bytes], signature: str, 
                           public_key_pem: bytes) -> bool:
        """
        Verify a digital signature using RSA public key.
        
        Args:
            data: Original data that was signed
            signature: Base64-encoded signature
            public_key_pem: RSA public key in PEM format
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if isinstance(data, str):
                data = data.encode()
            
            signature_bytes = base64.b64decode(signature.encode())
            
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=self.backend
            )
            
            # Verify signature using PSS padding
            public_key.verify(
                signature_bytes,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            self.logger.warning(f"RSA signature verification failed: {str(e)}")
            return False
    
    def create_hmac(self, data: Union[str, bytes], key: bytes, 
                   algorithm: str = "sha256") -> str:
        """
        Create HMAC (Hash-based Message Authentication Code).
        
        Args:
            data: Data to authenticate
            key: HMAC key
            algorithm: Hash algorithm ("sha256", "sha512")
            
        Returns:
            Base64-encoded HMAC
            
        Raises:
            ValueError: If algorithm is not supported
        """
        if isinstance(data, str):
            data = data.encode()
        
        if algorithm == "sha256":
            hash_algo = hashes.SHA256()
        elif algorithm == "sha512":
            hash_algo = hashes.SHA512()
        else:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
        
        h = hmac.HMAC(key, hash_algo, backend=self.backend)
        h.update(data)
        mac = h.finalize()
        
        return base64.b64encode(mac).decode()
    
    def verify_hmac(self, data: Union[str, bytes], mac: str, key: bytes,
                   algorithm: str = "sha256") -> bool:
        """
        Verify HMAC.
        
        Args:
            data: Original data
            mac: Base64-encoded HMAC to verify
            key: HMAC key
            algorithm: Hash algorithm
            
        Returns:
            True if HMAC is valid, False otherwise
        """
        try:
            if isinstance(data, str):
                data = data.encode()
            
            mac_bytes = base64.b64decode(mac.encode())
            
            if algorithm == "sha256":
                hash_algo = hashes.SHA256()
            elif algorithm == "sha512":
                hash_algo = hashes.SHA512()
            else:
                raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
            
            h = hmac.HMAC(key, hash_algo, backend=self.backend)
            h.update(data)
            h.verify(mac_bytes)
            
            return True
            
        except Exception as e:
            self.logger.warning(f"HMAC verification failed: {str(e)}")
            return False
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """
        Hash data using specified algorithm.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm ("md5", "sha1", "sha256", "sha512")
            
        Returns:
            Hexadecimal hash string
            
        Raises:
            ValueError: If algorithm is not supported
        """
        if isinstance(data, str):
            data = data.encode()
        
        if algorithm == "md5":
            hash_obj = hashlib.md5()
        elif algorithm == "sha1":
            hash_obj = hashlib.sha1()
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256()
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        hash_obj.update(data)
        return hash_obj.hexdigest()
    
    def generate_secure_random(self, length: int) -> bytes:
        """
        Generate cryptographically secure random bytes.
        
        Args:
            length: Number of bytes to generate
            
        Returns:
            Random bytes
        """
        return secrets.token_bytes(length)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a secure random token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            URL-safe base64-encoded token
        """
        return secrets.token_urlsafe(length)
    
    def constant_time_compare(self, a: Union[str, bytes], b: Union[str, bytes]) -> bool:
        """
        Compare two strings/bytes in constant time to prevent timing attacks.
        
        Args:
            a: First value
            b: Second value
            
        Returns:
            True if values are equal, False otherwise
        """
        if isinstance(a, str):
            a = a.encode()
        if isinstance(b, str):
            b = b.encode()
        
        return secrets.compare_digest(a, b)
    
    def encrypt_sensitive_config(self, config_data: Dict[str, Any], password: str) -> Dict[str, str]:
        """
        Encrypt sensitive configuration data.
        
        Args:
            config_data: Configuration dictionary
            password: Encryption password
            
        Returns:
            Dictionary containing encrypted data and metadata
        """
        import json
        
        # Serialize config data
        json_data = json.dumps(config_data)
        
        # Derive key from password
        key, salt = self.derive_key_from_password(password)
        
        # Encrypt using AES-GCM
        encrypted = self.encrypt_aes_gcm(json_data, key)
        
        return {
            "encrypted_data": encrypted["ciphertext"],
            "nonce": encrypted["nonce"],
            "tag": encrypted["tag"],
            "salt": base64.b64encode(salt).decode(),
            "algorithm": "aes256-gcm",
            "kdf": "pbkdf2"
        }
    
    def decrypt_sensitive_config(self, encrypted_config: Dict[str, str], password: str) -> Dict[str, Any]:
        """
        Decrypt sensitive configuration data.
        
        Args:
            encrypted_config: Encrypted configuration dictionary
            password: Decryption password
            
        Returns:
            Decrypted configuration dictionary
            
        Raises:
            DecryptionError: If decryption fails
        """
        import json
        
        try:
            # Extract encryption parameters
            salt = base64.b64decode(encrypted_config["salt"])
            
            # Derive key from password
            key, _ = self.derive_key_from_password(password, salt)
            
            # Prepare encrypted data
            encrypted_data = {
                "ciphertext": encrypted_config["encrypted_data"],
                "nonce": encrypted_config["nonce"],
                "tag": encrypted_config["tag"]
            }
            
            # Decrypt
            decrypted_json = self.decrypt_aes_gcm(encrypted_data, key)
            
            # Parse JSON
            config_data = json.loads(decrypted_json.decode())
            
            return config_data
            
        except Exception as e:
            self.logger.error(f"Configuration decryption error: {str(e)}")
            raise DecryptionError(f"Failed to decrypt configuration: {str(e)}")
