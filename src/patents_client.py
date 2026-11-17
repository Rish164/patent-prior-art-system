import sys
import re
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from typing import List
import requests
from bs4 import BeautifulSoup
from src.schemas import PatentDocument

GOOGLE_PATENTS_URL = "https://patents.google.com/xhr/query"
GOOGLE_PATENT_DETAIL_URL = "https://patents.google.com/patent/{patent_id}/en"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_cpc_codes(patent_id: str) -> List[str]:
    """
    Fetch the individual patent detail page to extract its real CPC classification codes.
    """
    url = GOOGLE_PATENT_DETAIL_URL.format(patent_id=patent_id)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cpc_codes = []
        # Google Patents embeds CPC symbols in <meta name="DC.subject"> and classification spans
        for meta in soup.find_all("meta", {"name": "DC.subject"}):
            content = meta.get("content", "").strip()
            # Match standard CPC format (e.g., A61K8/00, B64C39/02)
            if re.match(r"^[A-HY]\d{2}[A-Z]\d+/\d+$", content):
                cpc_codes.append(content)

        # Fallback: scan classification elements in HTML if meta tags are sparse
        if not cpc_codes:
            for item in soup.select('span[itemprop="Code"]'):
                code = item.get_text(strip=True)
                if re.match(r"^[A-HY]\d{2}[A-Z]\d+/\d+$", code):
                    cpc_codes.append(code)

        return list(dict.fromkeys(cpc_codes))[:5]
    except Exception:
        return []


def search_patents(query_text: str, max_results: int = 5, enrich_cpc: bool = True) -> List[PatentDocument]:
    """
    Search historical global/USPTO patents via Google Patents' public endpoint.
    Optionally enriches each result with real CPC codes from its detail page.
    """
    params = {
        "url": f"q={query_text}&country=US&type=PATENT&num={max_results}"
    }

    response = requests.get(GOOGLE_PATENTS_URL, params=params, headers=HEADERS, timeout=15)
    response.raise_for_status()
    data = response.json()

    documents: List[PatentDocument] = []
    cluster = data.get("results", {}).get("cluster", [])

    for item in cluster:
        for doc_entry in item.get("result", []):
            patent_info = doc_entry.get("patent", {})
            patent_id = patent_info.get("publication_number", "UNKNOWN")
            title = patent_info.get("title", "No title")
            snippet = patent_info.get("snippet", "")

            cpc_list = fetch_cpc_codes(patent_id) if enrich_cpc and patent_id != "UNKNOWN" else []

            documents.append(
                PatentDocument(
                    patent_id=patent_id,
                    title=title.replace("<b>", "").replace("</b>", "").strip(),
                    abstract=snippet.replace("<b>", "").replace("</b>", "").strip(),
                    cpc_codes=cpc_list,
                    claims=[]
                )
            )
            if len(documents) >= max_results:
                return documents

    return documents


if __name__ == "__main__":
    test_query = "Hair Color"
    print(f"Querying patents for: '{test_query}'...")
    try:
        patents = search_patents(test_query, max_results=3, enrich_cpc=True)
        print(f"\nRetrieved {len(patents)} patents successfully:\n")
        for p in patents:
            print(f"ID       : {p.patent_id}")
            print(f"Title    : {p.title}")
            print(f"Snippet  : {p.abstract[:100]}...")
            print(f"CPC      : {p.cpc_codes}")
            print("-" * 50)
    except Exception as exc:
        print(f"Failed: {exc}")