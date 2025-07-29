# mdme — Modern Drupal Module Enumerator

**mdme** is a fast and parallelized scanner designed to enumerate publicly accessible Drupal modules from an external perspective (no authentication required). It attempts to detect module existence and optionally extract version information by probing for common static files such as `.info.yml`, `README.txt`, and `.js` files.

---

## 🔍 Features

- 🚀 Multithreaded for high-speed enumeration
- 🧵 Configurable number of threads
- 🔎 Attempts to extract module version from `.info.yml`

---

## 🛠 Requirements

- Python 3.6+
- `requests` and `tqdm` libraries:
  
```bash
pip install -r requirements.txt
```

## 🚀 Usage
```bash
python3 mdme.py <target_url> <modules_wordlist.txt> [--user-agent UA] [--threads N]
```

### Example:
```bash
python3 mdme.py https://example-drupal-site.com modules.txt --threads 30
```

