#!/usr/bin/env python3
"""Utility to encrypt or decrypt sensitive fields in JSON files.

The encryption key must be provided via the ``graph-dev-env`` environment
variable. Keys listed in ``FIELDS`` are encrypted or decrypted recursively
throughout the JSON structure.
"""

from __future__ import annotations

import argparse
import json
import os
from importlib import import_module
from typing import Any

# Import ``cryptography.fernet`` dynamically as required.
fernet = import_module("cryptography.fernet")

FIELDS = [
    "password",
    "key",
    "secret",
    "api_key",
    "client_id",
    "client_secret",
    "orgId",
]

ENV_KEY_NAME = "graph-dev-env"


def _process(data: Any, cipher: "fernet.Fernet", encrypt: bool) -> Any:
    """Recursively encrypt or decrypt fields in a JSON structure."""
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if k in FIELDS and isinstance(v, str):
                if encrypt:
                    result[k] = cipher.encrypt(v.encode()).decode()
                else:
                    try:
                        result[k] = cipher.decrypt(v.encode()).decode()
                    except Exception:
                        # If value was not encrypted, leave it as-is
                        result[k] = v
            else:
                result[k] = _process(v, cipher, encrypt)
        return result
    if isinstance(data, list):
        return [_process(item, cipher, encrypt) for item in data]
    return data


def _load_cipher() -> "fernet.Fernet":
    key = os.environ.get(ENV_KEY_NAME)
    if not key:
        raise SystemExit(f"Environment variable {ENV_KEY_NAME} is not set")
    return fernet.Fernet(key.encode())


def encrypt_file(path: str, output: str | None) -> None:
    cipher = _load_cipher()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    processed = _process(data, cipher, encrypt=True)
    with open(output or path, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)


def decrypt_file(path: str, output: str | None) -> None:
    cipher = _load_cipher()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    processed = _process(data, cipher, encrypt=False)
    with open(output or path, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)


def generate_key() -> None:
    print(fernet.Fernet.generate_key().decode())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt sensitive values in a JSON file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("generate-key", help="Generate a new encryption key")

    enc_parser = subparsers.add_parser("encrypt", help="Encrypt JSON file")
    enc_parser.add_argument("input", help="Input JSON file")
    enc_parser.add_argument(
        "output",
        nargs="?",
        help="Output file (defaults to overwriting the input file)",
    )

    dec_parser = subparsers.add_parser("decrypt", help="Decrypt JSON file")
    dec_parser.add_argument("input", help="Input JSON file")
    dec_parser.add_argument(
        "output",
        nargs="?",
        help="Output file (defaults to overwriting the input file)",
    )

    args = parser.parse_args()

    if args.command == "generate-key":
        generate_key()
    elif args.command == "encrypt":
        encrypt_file(args.input, args.output)
    elif args.command == "decrypt":
        decrypt_file(args.input, args.output)


if __name__ == "__main__":
    main()
