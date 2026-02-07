from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os

def generate_self_signed_cert():
    # 1. Privaten Schlüssel generieren
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Zertifikatsdetails festlegen
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # 10 Jahre gültig
        datetime.datetime.utcnow() + datetime.timedelta(days=3650)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False,
    ).sign(key, hashes.SHA256())

    # 3. Dateien schreiben
    with open("server.key", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open("server.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Erfolgreich erstellt im Ordner: {os.getcwd()}")
    print("Dateien: server.key und server.crt")

if __name__ == "__main__":
    generate_self_signed_cert()