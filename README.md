# graph-bot

This repository provides a small utility to encrypt or decrypt sensitive
configuration values stored in JSON files.

## env_crypto.py

`env_crypto.py` uses the [Fernet](https://cryptography.io/en/latest/fernet/)
implementation from the `cryptography` package. The key to perform encryption
or decryption is read from the `graph-dev-env` environment variable.

### Generate a key

```
python env_crypto.py generate-key
```

### Encrypt a JSON file

```
export graph-dev-env=<key-from-generate>
python env_crypto.py encrypt settings.json
```

### Decrypt a JSON file

```
export graph-dev-env=<key-from-generate>
python env_crypto.py decrypt settings.json
```

Only values associated with the following fields are processed:
`password`, `key`, `secret`, `api_key`, `client_id`, `client_secret`, `orgId`.
