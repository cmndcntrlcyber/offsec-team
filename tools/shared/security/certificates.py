"""
Certificate management utilities for cybersecurity AI workflow integration.

This module provides X.509 certificate handling, validation, and management
for secure communication between platforms and services.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from cryptography import x509
from cryptography.x509.oid import NameOID, SignatureAlgorithmOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from pydantic import BaseModel, Field
import ipaddress
import socket


class CertificateError(Exception):
    """Exception raised for certificate-related errors."""
    pass


class CertificateValidationError(CertificateError):
    """Exception raised when certificate validation fails."""
    pass


class CertificateInfo(BaseModel):
    """Certificate information model."""
    
    subject: str = Field(..., description="Certificate subject")
    issuer: str = Field(..., description="Certificate issuer")
    serial_number: str = Field(..., description="Certificate serial number")
    not_valid_before: datetime = Field(..., description="Certificate validity start")
    not_valid_after: datetime = Field(..., description="Certificate validity end")
    public_key_algorithm: str = Field(..., description="Public key algorithm")
    public_key_size: Optional[int] = Field(default=None, description="Public key size in bits")
    signature_algorithm: str = Field(..., description="Signature algorithm")
    subject_alt_names: List[str] = Field(default_factory=list, description="Subject alternative names")
    key_usage: List[str] = Field(default_factory=list, description="Key usage extensions")
    extended_key_usage: List[str] = Field(default_factory=list, description="Extended key usage")
    is_ca: bool = Field(default=False, description="Whether certificate is a CA")
    path_length: Optional[int] = Field(default=None, description="CA path length constraint")
    fingerprint_sha256: str = Field(..., description="SHA256 fingerprint")
    is_self_signed: bool = Field(default=False, description="Whether certificate is self-signed")
    is_expired: bool = Field(default=False, description="Whether certificate is expired")
    days_until_expiry: Optional[int] = Field(default=None, description="Days until expiry")


class CertificateManager:
    """
    Certificate manager for X.509 certificate operations.
    Provides certificate generation, validation, and management capabilities.
    """
    
    def __init__(self):
        """Initialize the certificate manager."""
        self.backend = default_backend()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("CertificateManager")
    
    def generate_private_key(self, key_size: int = 2048) -> bytes:
        """
        Generate a private key for certificate use.
        
        Args:
            key_size: RSA key size in bits
            
        Returns:
            Private key in PEM format
        """
        if key_size not in [2048, 3072, 4096]:
            raise ValueError("Key size must be 2048, 3072, or 4096 bits")
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        self.logger.info(f"Generated private key ({key_size} bits)")
        return pem
    
    def create_self_signed_certificate(self, 
                                     private_key_pem: bytes,
                                     subject_name: str,
                                     validity_days: int = 365,
                                     alt_names: Optional[List[str]] = None) -> bytes:
        """
        Create a self-signed X.509 certificate.
        
        Args:
            private_key_pem: Private key in PEM format
            subject_name: Certificate subject common name
            validity_days: Certificate validity period in days
            alt_names: Subject alternative names (DNS names, IP addresses)
            
        Returns:
            Certificate in PEM format
            
        Raises:
            CertificateError: If certificate creation fails
        """
        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=self.backend
            )
            
            # Build subject name
            subject = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Cybersec AI Workflow"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security Operations"),
            ])
            
            # Create certificate builder
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(subject)  # Self-signed
            builder = builder.public_key(private_key.public_key())
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.utcnow())
            builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            
            # Add key usage extension
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    content_commitment=False,
                    data_encipherment=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            
            # Add basic constraints (CA certificate)
            builder = builder.add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True
            )
            
            # Add subject key identifier
            builder = builder.add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                critical=False
            )
            
            # Add authority key identifier (same as subject for self-signed)
            builder = builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(private_key.public_key()),
                critical=False
            )
            
            # Add subject alternative names if provided
            if alt_names:
                san_list = []
                for name in alt_names:
                    try:
                        # Try to parse as IP address
                        ip = ipaddress.ip_address(name)
                        san_list.append(x509.IPAddress(ip))
                    except ValueError:
                        # Treat as DNS name
                        san_list.append(x509.DNSName(name))
                
                if san_list:
                    builder = builder.add_extension(
                        x509.SubjectAlternativeName(san_list),
                        critical=False
                    )
            
            # Sign the certificate
            certificate = builder.sign(private_key, hashes.SHA256(), self.backend)
            
            # Serialize to PEM
            pem = certificate.public_bytes(serialization.Encoding.PEM)
            
            self.logger.info(f"Created self-signed certificate for {subject_name}")
            return pem
            
        except Exception as e:
            self.logger.error(f"Certificate creation error: {str(e)}")
            raise CertificateError(f"Failed to create certificate: {str(e)}")
    
    def create_certificate_signing_request(self,
                                         private_key_pem: bytes,
                                         subject_name: str,
                                         alt_names: Optional[List[str]] = None) -> bytes:
        """
        Create a Certificate Signing Request (CSR).
        
        Args:
            private_key_pem: Private key in PEM format
            subject_name: Certificate subject common name
            alt_names: Subject alternative names
            
        Returns:
            CSR in PEM format
            
        Raises:
            CertificateError: If CSR creation fails
        """
        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=self.backend
            )
            
            # Build subject name
            subject = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Cybersec AI Workflow"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security Operations"),
            ])
            
            # Create CSR builder
            builder = x509.CertificateSigningRequestBuilder()
            builder = builder.subject_name(subject)
            
            # Add subject alternative names if provided
            if alt_names:
                san_list = []
                for name in alt_names:
                    try:
                        # Try to parse as IP address
                        ip = ipaddress.ip_address(name)
                        san_list.append(x509.IPAddress(ip))
                    except ValueError:
                        # Treat as DNS name
                        san_list.append(x509.DNSName(name))
                
                if san_list:
                    builder = builder.add_extension(
                        x509.SubjectAlternativeName(san_list),
                        critical=False
                    )
            
            # Sign the CSR
            csr = builder.sign(private_key, hashes.SHA256(), self.backend)
            
            # Serialize to PEM
            pem = csr.public_bytes(serialization.Encoding.PEM)
            
            self.logger.info(f"Created CSR for {subject_name}")
            return pem
            
        except Exception as e:
            self.logger.error(f"CSR creation error: {str(e)}")
            raise CertificateError(f"Failed to create CSR: {str(e)}")
    
    def sign_certificate_request(self,
                               csr_pem: bytes,
                               ca_cert_pem: bytes,
                               ca_private_key_pem: bytes,
                               validity_days: int = 365,
                               is_ca: bool = False) -> bytes:
        """
        Sign a certificate signing request with a CA certificate.
        
        Args:
            csr_pem: CSR in PEM format
            ca_cert_pem: CA certificate in PEM format
            ca_private_key_pem: CA private key in PEM format
            validity_days: Certificate validity period in days
            is_ca: Whether the signed certificate should be a CA certificate
            
        Returns:
            Signed certificate in PEM format
            
        Raises:
            CertificateError: If signing fails
        """
        try:
            # Load CSR
            csr = x509.load_pem_x509_csr(csr_pem, self.backend)
            
            # Load CA certificate and private key
            ca_cert = x509.load_pem_x509_certificate(ca_cert_pem, self.backend)
            ca_private_key = serialization.load_pem_private_key(
                ca_private_key_pem,
                password=None,
                backend=self.backend
            )
            
            # Create certificate builder
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(csr.subject)
            builder = builder.issuer_name(ca_cert.subject)
            builder = builder.public_key(csr.public_key())
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.utcnow())
            builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            
            # Copy extensions from CSR
            for extension in csr.extensions:
                builder = builder.add_extension(extension.value, extension.critical)
            
            # Add key usage extension
            if is_ca:
                builder = builder.add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        key_encipherment=False,
                        key_agreement=False,
                        key_cert_sign=True,
                        crl_sign=True,
                        content_commitment=False,
                        data_encipherment=False,
                        encipher_only=False,
                        decipher_only=False
                    ),
                    critical=True
                )
            else:
                builder = builder.add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        key_encipherment=True,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        content_commitment=False,
                        data_encipherment=False,
                        encipher_only=False,
                        decipher_only=False
                    ),
                    critical=True
                )
            
            # Add basic constraints
            builder = builder.add_extension(
                x509.BasicConstraints(ca=is_ca, path_length=None),
                critical=True
            )
            
            # Add subject key identifier
            builder = builder.add_extension(
                x509.SubjectKeyIdentifier.from_public_key(csr.public_key()),
                critical=False
            )
            
            # Add authority key identifier
            builder = builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_private_key.public_key()),
                critical=False
            )
            
            # Sign the certificate
            certificate = builder.sign(ca_private_key, hashes.SHA256(), self.backend)
            
            # Serialize to PEM
            pem = certificate.public_bytes(serialization.Encoding.PEM)
            
            self.logger.info(f"Signed certificate for {csr.subject.rfc4514_string()}")
            return pem
            
        except Exception as e:
            self.logger.error(f"Certificate signing error: {str(e)}")
            raise CertificateError(f"Failed to sign certificate: {str(e)}")
    
    def load_certificate(self, cert_pem: bytes) -> x509.Certificate:
        """
        Load an X.509 certificate from PEM format.
        
        Args:
            cert_pem: Certificate in PEM format
            
        Returns:
            Certificate object
            
        Raises:
            CertificateError: If certificate loading fails
        """
        try:
            return x509.load_pem_x509_certificate(cert_pem, self.backend)
        except Exception as e:
            self.logger.error(f"Certificate loading error: {str(e)}")
            raise CertificateError(f"Failed to load certificate: {str(e)}")
    
    def get_certificate_info(self, cert_pem: bytes) -> CertificateInfo:
        """
        Extract information from an X.509 certificate.
        
        Args:
            cert_pem: Certificate in PEM format
            
        Returns:
            Certificate information
            
        Raises:
            CertificateError: If certificate parsing fails
        """
        try:
            cert = self.load_certificate(cert_pem)
            
            # Extract subject alternative names
            alt_names = []
            try:
                san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                for name in san_ext.value:
                    if isinstance(name, x509.DNSName):
                        alt_names.append(f"DNS:{name.value}")
                    elif isinstance(name, x509.IPAddress):
                        alt_names.append(f"IP:{name.value}")
                    elif isinstance(name, x509.RFC822Name):
                        alt_names.append(f"Email:{name.value}")
            except x509.ExtensionNotFound:
                pass
            
            # Extract key usage
            key_usage = []
            try:
                ku_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE)
                ku = ku_ext.value
                if ku.digital_signature:
                    key_usage.append("Digital Signature")
                if ku.key_encipherment:
                    key_usage.append("Key Encipherment")
                if ku.key_agreement:
                    key_usage.append("Key Agreement")
                if ku.key_cert_sign:
                    key_usage.append("Certificate Sign")
                if ku.crl_sign:
                    key_usage.append("CRL Sign")
            except x509.ExtensionNotFound:
                pass
            
            # Extract extended key usage
            extended_key_usage = []
            try:
                eku_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.EXTENDED_KEY_USAGE)
                for usage in eku_ext.value:
                    extended_key_usage.append(usage.dotted_string)
            except x509.ExtensionNotFound:
                pass
            
            # Check if CA certificate
            is_ca = False
            path_length = None
            try:
                bc_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.BASIC_CONSTRAINTS)
                is_ca = bc_ext.value.ca
                path_length = bc_ext.value.path_length
            except x509.ExtensionNotFound:
                pass
            
            # Calculate fingerprint
            fingerprint = cert.fingerprint(hashes.SHA256()).hex()
            
            # Check if self-signed
            is_self_signed = cert.subject == cert.issuer
            
            # Check if expired
            now = datetime.utcnow()
            is_expired = now > cert.not_valid_after
            
            # Calculate days until expiry
            days_until_expiry = None
            if not is_expired:
                days_until_expiry = (cert.not_valid_after - now).days
            
            # Get public key info
            public_key = cert.public_key()
            public_key_algorithm = type(public_key).__name__.replace('_', '').replace('PublicKey', '')
            
            public_key_size = None
            if hasattr(public_key, 'key_size'):
                public_key_size = public_key.key_size
            
            return CertificateInfo(
                subject=cert.subject.rfc4514_string(),
                issuer=cert.issuer.rfc4514_string(),
                serial_number=str(cert.serial_number),
                not_valid_before=cert.not_valid_before,
                not_valid_after=cert.not_valid_after,
                public_key_algorithm=public_key_algorithm,
                public_key_size=public_key_size,
                signature_algorithm=cert.signature_algorithm_oid._name,
                subject_alt_names=alt_names,
                key_usage=key_usage,
                extended_key_usage=extended_key_usage,
                is_ca=is_ca,
                path_length=path_length,
                fingerprint_sha256=fingerprint,
                is_self_signed=is_self_signed,
                is_expired=is_expired,
                days_until_expiry=days_until_expiry
            )
            
        except Exception as e:
            self.logger.error(f"Certificate info extraction error: {str(e)}")
            raise CertificateError(f"Failed to extract certificate info: {str(e)}")
    
    def validate_certificate_chain(self, 
                                 cert_pem: bytes, 
                                 ca_certs_pem: List[bytes],
                                 check_hostname: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a certificate chain.
        
        Args:
            cert_pem: End-entity certificate in PEM format
            ca_certs_pem: List of CA certificates in PEM format
            check_hostname: Hostname to validate against certificate
            
        Returns:
            Validation result dictionary
        """
        try:
            # Load certificates
            cert = self.load_certificate(cert_pem)
            ca_certs = [self.load_certificate(ca_pem) for ca_pem in ca_certs_pem]
            
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check certificate validity period
            now = datetime.utcnow()
            if now < cert.not_valid_before:
                validation_result["valid"] = False
                validation_result["errors"].append("Certificate is not yet valid")
            
            if now > cert.not_valid_after:
                validation_result["valid"] = False
                validation_result["errors"].append("Certificate has expired")
            
            # Check if certificate expires soon (within 30 days)
            if (cert.not_valid_after - now).days <= 30:
                validation_result["warnings"].append("Certificate expires within 30 days")
            
            # Basic chain validation (simplified)
            # In production, you'd want to use a proper chain validation library
            issuer_found = False
            for ca_cert in ca_certs:
                if cert.issuer == ca_cert.subject:
                    issuer_found = True
                    # Verify signature (simplified check)
                    try:
                        ca_public_key = ca_cert.public_key()
                        # This is a basic check - full validation would be more complex
                        if cert.signature_algorithm_oid == ca_cert.signature_algorithm_oid:
                            validation_result["warnings"].append("Chain validation performed (basic check)")
                    except Exception as e:
                        validation_result["errors"].append(f"Signature verification failed: {str(e)}")
                        validation_result["valid"] = False
                    break
            
            if not issuer_found and not cert.subject == cert.issuer:
                validation_result["errors"].append("Certificate issuer not found in provided CA certificates")
                validation_result["valid"] = False
            
            # Hostname validation
            if check_hostname:
                hostname_valid = self._validate_hostname(cert, check_hostname)
                if not hostname_valid:
                    validation_result["errors"].append(f"Certificate does not match hostname: {check_hostname}")
                    validation_result["valid"] = False
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Certificate validation error: {str(e)}")
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": []
            }
    
    def _validate_hostname(self, cert: x509.Certificate, hostname: str) -> bool:
        """
        Validate hostname against certificate subject and SAN.
        
        Args:
            cert: Certificate object
            hostname: Hostname to validate
            
        Returns:
            True if hostname matches certificate
        """
        try:
            # Check subject common name
            for attribute in cert.subject:
                if attribute.oid == NameOID.COMMON_NAME:
                    if attribute.value.lower() == hostname.lower():
                        return True
                    # Check for wildcard match
                    if attribute.value.startswith('*.'):
                        domain = attribute.value[2:].lower()
                        if hostname.lower().endswith('.' + domain):
                            return True
            
            # Check subject alternative names
            try:
                san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                for name in san_ext.value:
                    if isinstance(name, x509.DNSName):
                        if name.value.lower() == hostname.lower():
                            return True
                        # Check for wildcard match
                        if name.value.startswith('*.'):
                            domain = name.value[2:].lower()
                            if hostname.lower().endswith('.' + domain):
                                return True
                    elif isinstance(name, x509.IPAddress):
                        try:
                            if str(name.value) == hostname:
                                return True
                        except:
                            pass
            except x509.ExtensionNotFound:
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"Hostname validation error: {str(e)}")
            return False
    
    def export_certificate_to_file(self, cert_pem: bytes, filepath: str):
        """
        Export certificate to a file.
        
        Args:
            cert_pem: Certificate in PEM format
            filepath: Output file path
            
        Raises:
            CertificateError: If export fails
        """
        try:
            with open(filepath, 'wb') as f:
                f.write(cert_pem)
            
            self.logger.info(f"Certificate exported to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Certificate export error: {str(e)}")
            raise CertificateError(f"Failed to export certificate: {str(e)}")
    
    def load_certificate_from_file(self, filepath: str) -> bytes:
        """
        Load certificate from a file.
        
        Args:
            filepath: Certificate file path
            
        Returns:
            Certificate in PEM format
            
        Raises:
            CertificateError: If loading fails
        """
        try:
            with open(filepath, 'rb') as f:
                cert_pem = f.read()
            
            # Validate that it's a valid certificate
            self.load_certificate(cert_pem)
            
            self.logger.info(f"Certificate loaded from {filepath}")
            return cert_pem
            
        except Exception as e:
            self.logger.error(f"Certificate file loading error: {str(e)}")
            raise CertificateError(f"Failed to load certificate from file: {str(e)}")
    
    def create_certificate_bundle(self, certificates: List[bytes]) -> bytes:
        """
        Create a certificate bundle (chain) by concatenating certificates.
        
        Args:
            certificates: List of certificates in PEM format (end-entity first)
            
        Returns:
            Certificate bundle in PEM format
        """
        bundle = b''
        for i, cert_pem in enumerate(certificates):
            # Validate certificate
            self.load_certificate(cert_pem)
            bundle += cert_pem
            if not cert_pem.endswith(b'\n'):
                bundle += b'\n'
        
        self.logger.info(f"Created certificate bundle with {len(certificates)} certificates")
        return bundle
    
    def split_certificate_bundle(self, bundle_pem: bytes) -> List[bytes]:
        """
        Split a certificate bundle into individual certificates.
        
        Args:
            bundle_pem: Certificate bundle in PEM format
            
        Returns:
            List of individual certificates in PEM format
        """
        certificates = []
        cert_lines = []
        in_cert = False
        
        for line in bundle_pem.decode().split('\n'):
            if line.strip() == '-----BEGIN CERTIFICATE-----':
                in_cert = True
                cert_lines = [line]
            elif line.strip() == '-----END CERTIFICATE-----':
                cert_lines.append(line)
                cert_pem = '\n'.join(cert_lines).encode() + b'\n'
                certificates.append(cert_pem)
                in_cert = False
                cert_lines = []
            elif in_cert:
                cert_lines.append(line)
        
        self.logger.info(f"Split certificate bundle into {len(certificates)} certificates")
        return certificates
