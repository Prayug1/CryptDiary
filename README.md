# CryptDiary

A secure, encrypted personal diary application with multi-user support and digital signatures.

## Features

- **Hybrid Encryption** – Diary entries are encrypted using AES-256 + RSA-2048
- **Digital Signatures** – Each entry is signed with RSA-PSS to ensure authenticity
- **X.509 Certificates** – Auto-generated self-signed certificates per user
- **Multi-User Support** – Separate keystores and diary storage per user
- **Certificate Revocation** – Global revocation list to invalidate compromised keys
- **Secure Entry Sharing** – Export/import entries with embedded certificate verification

## Project Structure

```
├── main.py                  # Application entry point
├── user_manager.py          # User registration & authentication
├── key_manager.py           # RSA key pair & certificate management
├── crypto_manager.py        # Encrypt, decrypt, sign & verify operations
├── diary_storage.py         # Diary entry storage (JSON-based)
├── performance_analyzer.py  # Benchmarking & performance tests
└── requirements.txt         # Dependencies
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py
```

## Security Overview

| Layer | Method |
|---|---|
| Entry Encryption | AES-256-CBC + RSA-2048 OAEP |
| Digital Signature | RSA-PSS + SHA-256 |
| Password Storage | PBKDF2-HMAC-SHA256 (100k iterations) |
| Keystore | AES-256-CBC encrypted JSON |
| Certificates | Self-signed X.509 (1-year validity) |

## Requirements

- Python 3.7+
- `cryptography` library
