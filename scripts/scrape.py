#!/usr/bin/env python3
"""
=====================================================================
 वंदे सहकार — Auto Scraper
 दर आठवड्याला Patsanstha Niyamak Mandal + Sahkar Vibhag वरून
 नवीन परिपत्रके scrape करते आणि data/circulars.json update करते.

 Source 1: https://patsansthaniyamakmandal.in/Home/DownloadSections
 Source 2: https://mahasahakar.maharashtra.gov.in/en/document-category/

 GitHub Actions कडून automatic चालते (.github/workflows/weekly-update.yml).
 Existing entries unchanged — फक्त नवीन परिपत्रके जोडली जातात.
=====================================================================
"""
import json
import re
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Required: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "circulars.json"
LAST_UPDATE = ROOT / "data" / "last_update.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# ─────────────────── Source 1: Niyamak Mandal ───────────────────
def scrape_niyamak_mandal():
    """Patsanstha Niyamak Mandal वरील सर्व downloads section parse करते."""
    url = "https://patsansthaniyamakmandal.in/Home/DownloadSections"
    print(f"  → {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    results = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "FileIO/ViewDocs" not in href:
            continue
        if not href.startswith("http"):
            href = "https://patsansthaniyamakmandal.in" + (href if href.startswith("/") else "/" + href)

        parent = a.find_parent(["li", "p", "td", "div"])
        text = parent.get_text(" ", strip=True) if parent else a.get_text(strip=True)
        text = re.sub(r"\s*डाऊनलोडस?\s*$", "", text).strip()
        text = re.sub(r"^\d+\.\s*", "", text).strip()
        if not text:
            continue

        date_m = re.search(r"\((\d{1,2})[-./](\d{1,2})[-./](\d{2,4})\)?", text)
        date_str, year = "", None
        if date_m:
            d, m, y = date_m.groups()
            if len(y) == 2:
                y = "20" + y if int(y) < 50 else "19" + y
            date_str = f"{y}-{int(m):02d}-{int(d):02d}"
            year = int(y)

        results.append({
            "source": "PNM",
            "title_raw": text,
            "pdf_url": href,
            "date": date_str,
            "year": year,
        })
    print(f"    ✓ Found {len(results)} entries")
    return results


# ─────────────────── Source 2: Sahkar Vibhag ───────────────────
def scrape_sahkar_vibhag():
    """सहकार विभाग — circulars + GRs चे सर्व pages."""
    base = "https://mahasahakar.maharashtra.gov.in/en/document-category"
    categories = ["circulars-standing-orders", "government-resolution-notification"]
    all_results = []
    for cat in categories:
        for page in range(1, 10):
            url = f"{base}/{cat}/" if page == 1 else f"{base}/{cat}/page/{page}"
            print(f"  → {url}")
            try:
                r = requests.get(url, headers=HEADERS, timeout=60)
                if r.status_code != 200:
                    break
            except Exception as e:
                print(f"    ✗ {e}")
                break
            soup = BeautifulSoup(r.text, "lxml")
            rows_found = 0
            for table in soup.find_all("table"):
                for tr in table.find_all("tr"):
                    cells = tr.find_all(["td", "th"])
                    if len(cells) < 3:
                        continue
                    title = cells[0].get_text(strip=True)
                    date_raw = cells[1].get_text(strip=True)
                    link = cells[2].find("a", href=True)
                    if not link or not title:
                        continue
                    href = link["href"]
                    if not href.lower().endswith(".pdf"):
                        continue

                    date_str, year = "", None
                    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_raw)
                    if m:
                        d, mo, y = m.groups()
                        date_str = f"{y}-{int(mo):02d}-{int(d):02d}"
                        year = int(y)

                    doc_type = "GR/Notification" if "government-resolution" in cat else "Circular"
                    all_results.append({
                        "source": "MS",
                        "title_raw": title,
                        "pdf_url": href,
                        "date": date_str,
                        "year": year,
                        "doc_type": doc_type,
                    })
                    rows_found += 1
            print(f"    ✓ Page {page}: {rows_found}")
            if rows_found == 0:
                break
            time.sleep(1)
    return all_results


# ─────── Filter for Credit Cooperative + Employees Societies ───────
KEYWORDS_INCLUDE = [
    "credit", "patsanstha", "salary", "employee", "earner", "urban", "rural",
    "audit", "auditor", "recovery", "kyc", "npa", "crar", "crr", "slr",
    "interest", "loan", "deposit", "share", "ots", "registration",
    "byelaw", "bye-law", "section 156", "section 89",
    "पतसंस्था", "नागरी", "ग्रामीण", "पगारदार", "कर्मचारी",
    "लेखापरीक्षण", "लेखापरीक्षक", "वसुली", "कर्ज", "ठेव", "व्याज",
    "नियामक", "अधिनियम", "उपविधी", "नोंदणी", "क-101", "क-49", "कलम",
]
KEYWORDS_EXCLUDE = [
    "housing", "redevelopment", "conveyance", "deemed conveyance",
    "sugar", "apmc", "marketing", "industrial", "goat", "sheep", "poultry",
    "गृहनिर्माण", "पुनर्विकास", "साखर", "बाजार", "औद्योगिक",
    "promotion", "transfer", "seniority", "पदोन्नती", "बदली",
    "labor societ", "labour societ", "कामगार सहकारी",
]

def is_relevant(title):
    t = title.lower()
    for kw in KEYWORDS_EXCLUDE:
        if kw.lower() in t:
            return False
    return any(kw.lower() in t for kw in KEYWORDS_INCLUDE)


# ─────────────────── Auto-classify category ───────────────────
def classify_category(title):
    t = title.lower()
    if any(k in t for k in ["mcs act", "mcs rules", "अधिनियम 1960", "नियम 1961"]):
        return "Acts & Rules", "📜 कायदा व नियम"
    if "byelaw" in t or "उपविधी" in t or "bye-law" in t:
        return "Model Bye-laws", "📋 आदर्श उपविधी"
    if any(k in t for k in ["niyamak", "नियामक", "मंडळ गठीत"]):
        return "Niyamak Mandal Framework", "🏛️ नियामक मंडळ रचना"
    if any(k in t for k in ["npa", "crar", "crr", "slr", "विवेकपूर्ण", "non-banking asset"]):
        return "Prudential Norms (CRR/SLR/CRAR/NPA)", "🏦 विवेकपूर्ण निकष"
    if any(k in t for k in ["audit classif", "वर्गवारी", "scoring", "गुणांकन"]):
        return "Audit Classification & Reports", "📊 ऑडिट वर्गीकरण"
    if any(k in t for k in ["audit", "auditor", "लेखापरीक्षण", "empanelment", "नामतालिका"]):
        return "Audit & Empanelment", "🔍 लेखापरीक्षण व नामतालिका"
    if any(k in t for k in ["kyc", "business correspondent", "mis", "बीसी"]):
        return "KYC, BC & MIS", "🛡️ KYC, BC व MIS"
    if any(k in t for k in ["loan limit", "loan rules", "कर्ज मर्यादा", "कर्ज विषयक"]):
        return "Loan Limits & Rules", "💵 कर्ज मर्यादा व नियम"
    if any(k in t for k in ["interest rate", "व्याज दर", "deposit", "ठेव"]):
        return "Interest Rates & Capital", "💎 भागभांडवल व व्याज दर"
    if any(k in t for k in ["share holding", "भागभांडवल"]):
        return "Interest Rates & Capital", "💎 भागभांडवल व व्याज दर"
    if any(k in t for k in ["interest subvention", "व्याज परतावा", "subvention"]):
        return "Interest Subvention", "💰 व्याज परतावा योजना"
    if any(k in t for k in ["ots", "recovery", "वसुली", "section 156", "क-101"]):
        return "OTS, Recovery & Legal", "⚖️ OTS, वसुली व कायदेशीर"
    if any(k in t for k in ["disclosure", "annual report", "compliance", "अनुपालन", "ताळेबंद"]):
        return "Compliance & Reporting", "📈 अनुपालन व अहवाल"
    if any(k in t for k in ["क-49", "वेतन कपात", "salary deduction"]):
        return "Salary Deduction (K-49)", "💼 वेतन कपात"
    if any(k in t for k in ["election", "निवडणूक"]):
        return "Elections & Administration", "🗳️ निवडणूक व प्रशासन"
    if any(k in t for k in ["section 89", "कलम ८९", "inspection", "तपासणी"]):
        return "Inspection & Inquiry", "🔎 तपासणी व चौकशी"
    if any(k in t for k in ["registration", "नोंदणी", "expansion"]):
        return "Registration & Setup", "📝 नोंदणी व विस्तार"
    return "Compliance & Reporting", "📈 अनुपालन व अहवाल"


def main():
    print("=" * 70)
    print("  वंदे सहकार — Auto Scraper")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"📁 Existing: {len(existing)} documents")
    else:
        existing = []
        print("📁 Starting fresh")

    existing_urls = {d["pdf_url"] for d in existing}

    print("\n🔍 Source 1: पतसंस्था नियामक मंडळ")
    pnm = scrape_niyamak_mandal()

    print("\n🔍 Source 2: सहकार विभाग")
    ms = scrape_sahkar_vibhag()

    new_count = 0
    for entry in pnm + ms:
        if entry["pdf_url"] in existing_urls:
            continue
        title = entry.get("title_raw", "")
        if not is_relevant(title):
            continue
        cat_en, cat_mr = classify_category(title)
        new_id = f"NEW-{hashlib.md5(entry['pdf_url'].encode()).hexdigest()[:6].upper()}"
        existing.append({
            "id": new_id,
            "title_mr": title,
            "title_en": title,
            "date": entry.get("date") or "—",
            "year": entry.get("year"),
            "category": cat_en,
            "category_mr": cat_mr,
            "source": entry["source"],
            "source_full": "पतसंस्था नियामक मंडळ" if entry["source"] == "PNM" else "सहकार विभाग, महाराष्ट्र",
            "pdf_url": entry["pdf_url"],
            "doc_type": entry.get("doc_type", "Circular"),
            "tags": ["Auto-detected"],
        })
        new_count += 1
        print(f"  ⊕ NEW: {title[:65]}")

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    with open(LAST_UPDATE, "w", encoding="utf-8") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"))

    print("\n" + "=" * 70)
    print(f"  ✓ Total:      {len(existing)} documents")
    print(f"  ⊕ New:        {new_count}")
    print(f"  📅 Updated:   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
