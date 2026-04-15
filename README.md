# envault

> A CLI tool to securely manage and sync `.env` files across projects using encrypted local storage.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Initialize a vault for your project:**
```bash
envault init
```

**Store your `.env` file:**
```bash
envault push --env .env --project myapp
```

**Pull and restore a saved `.env` file:**
```bash
envault pull --project myapp
```

**List all stored projects:**
```bash
envault list
```

All secrets are encrypted at rest using AES-256 encryption. A master password is required on first use and cached securely in your system keychain.

---

## How It Works

1. `envault` encrypts your `.env` file using a master password derived key.
2. The encrypted vault is stored locally at `~/.envault/vault.db`.
3. You can sync the vault file across machines using any file sync tool (Dropbox, iCloud, etc.).

---

## Requirements

- Python 3.8+
- `cryptography`
- `click`
- `keyring`

---

## License

This project is licensed under the [MIT License](LICENSE).