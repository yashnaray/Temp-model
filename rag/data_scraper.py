import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re

def extract_main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    # Prefer <main> or <article> if found
    main = soup.find("main") or soup.find("article")
    text = main.get_text("\n") if main else soup.get_text("\n")

    # Clean up newlines
    text = re.sub(r"\n\s*\n+", "\n\n", text.strip())
    return text

def scrape_insurance_guidelines(urls, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for url in urls:
        print(f"[insurance_guidelines] Fetching {url}")
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "KB-Test/1.0"})
            r.raise_for_status()
            text = extract_main_text(r.text)
            data = {"source_url": url, "content": text[:2000]}  # truncate for quick test
            fname = re.sub(r"[^A-Za-z0-9]", "_", url)[:60] + ".json"
            dest = out_dir / fname
            dest.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"[insurance_guidelines] Saved -> {dest}")
        except Exception as e:
            print(f"[ERROR] {url}: {e}")

if __name__ == "__main__":
    urls = ["https://content.naic.org/consumer/homeowners-insurance.htm"]
    scrape_insurance_guidelines(urls, Path("./knowledge_base/insurance_guidelines"))
    print("\nDone ✅ — check the folder ./knowledge_base/insurance_guidelines/")