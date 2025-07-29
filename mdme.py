import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import re

COMMON_PATHS = [
    "/modules/contrib/{mod}/{mod}.info.yml",
    "/modules/custom/{mod}/{mod}.info.yml",
    "/modules/contrib/{mod}/README.txt",
    "/modules/contrib/{mod}/LICENSE.txt",
    "/modules/contrib/{mod}/{mod}.js",
    "/modules/contrib/{mod}/",
    "/modules/custom/{mod}/",
    "/sites/all/modules/{mod}/{mod}.info.yml",
    "/sites/all/modules/{mod}/README.txt",
    "/sites/all/modules/{mod}/LICENSE.txt",
    "/sites/all/modules/{mod}/{mod}.js",
    "/sites/all/modules/{mod}/",
]

def load_modules(wordlist_path):
    with open(wordlist_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def extract_version(text):
    match = re.search(r'^\s*version\s*:\s*(.+)$', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def test_module(base_url, module, session, headers, verify, debug):
    for template in COMMON_PATHS:
        path = template.format(mod=module)
        url = base_url.rstrip("/") + path
        try:
            r = session.get(url, headers=headers, timeout=5, allow_redirects=False, verify=verify)
            if r.status_code in (200, 403):
                version = None
                if path.endswith(".info.yml") and r.status_code == 200:
                    version = extract_version(r.text)
                return module, url, r.status_code, version
        except requests.RequestException as e:
            if debug:
                tqdm.write(f"[!] Exception for {url}: {e}")
            continue
    return None

def scan_modules(base_url, module_list, user_agent, threads, proxy, verify, debug):
    headers = {"User-Agent": user_agent}
    proxies = {"http": proxy, "https": proxy} if proxy else None
    found = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        with requests.Session() as session:
            if proxies:
                session.proxies.update(proxies)

            futures = {
                executor.submit(test_module, base_url, mod, session, headers, verify, debug): mod
                for mod in module_list
            }

            with tqdm(total=len(module_list), desc="Scanning modules", ncols=100) as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        mod, url, code, version = result
                        version_str = f" | version: {version}" if version else ""
                        tqdm.write(f"[+] {mod:<30} ({code}) → {url}{version_str}")
                        found.append(result)
                    pbar.update(1)
    return found


def main():
    parser = argparse.ArgumentParser(description="Modern Drupal Module Enumerator")
    parser.add_argument("url", help="Target Drupal site base URL")
    parser.add_argument("wordlist", help="Path to file with module names")
    parser.add_argument("--user-agent", default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36", help="Custom User-Agent string")
    parser.add_argument("--threads", type=int, default=20, help="Number of concurrent threads")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--insecure", action="store_true", help="Disable SSL certificate validation")
    parser.add_argument("--debug", action="store_true", help="Print request exceptions for debugging")
    args = parser.parse_args()

    print(f"[i] Scanning: {args.url}")
    modules = load_modules(args.wordlist)
    scan_modules(
        base_url=args.url,
        module_list=modules,
        user_agent=args.user_agent,
        threads=args.threads,
        proxy=args.proxy,
        verify=not args.insecure,
        debug=args.debug
    )

if __name__ == "__main__":
    main()