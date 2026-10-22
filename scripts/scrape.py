#!/usr/bin/env python3
"""
=====================================================================
 वंदे सहकार — Auto Scraper
 दिवसातून ३ वेळा खालील अधिकृत स्रोतांवरून नवीन दस्तऐवज शोधते
 आणि data/circulars.json update करते.

 Source 1: https://patsansthaniyamakmandal.in/Home/DownloadSections
 Source 2: https://mahasahakar.maharashtra.gov.in/en/document-category/
 Source 3: https://gr.maharashtra.gov.in  (सहकार विभागाचे सर्व नवीन शासन निर्णय — त्याच दिवशी)

 GitHub Actions कडून automatic चालते (.github/workflows/weekly-update.yml).
 Existing entries unchanged — फक्त नवीन दस्तऐवज जोडले जातात.
 तिन्ही स्रोत अयशस्वी झाल्यास exit code 1 — म्हणजे Actions मध्ये लाल ✗ दिसतो.
=====================================================================
"""
import json
import re
import sys
import time
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Required: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gr_portal  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "circulars.json"
LAST_UPDATE = ROOT / "data" / "last_update.txt"
IST = timezone(timedelta(hours=5, minutes=30))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_with_retry(url, attempts=3):
    """सरकारी साइट तात्पुरती बंद असल्यास ३ वेळा प्रयत्न. अपयशी झाल्यास None."""
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            if r.status_code == 404:
                return r
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"    ✗ {e} (attempt {attempt})")
            time.sleep(10 * attempt)
    return None


# ─────────────────── Source 1: Niyamak Mandal ───────────────────
def scrape_niyamak_mandal():
    """Patsanstha Niyamak Mandal वरील सर्व downloads section parse करते. अपयशी झाल्यास None."""
    url = "https://patsansthaniyamakmandal.in/Home/DownloadSections"
    print(f"  → {url}")
    r = get_with_retry(url)
    if r is None or r.status_code != 200:
        return None

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
    return results or None  # साइटवर नेहमी ~४० दस्तऐवज असतात; शून्य = साइट बदलली


# ─────────────────── Source 2: Sahkar Vibhag ───────────────────
MS_CATEGORIES = {
    "circulars-standing-orders": "Circular",
    "government-resolution-notification": "GR/Notification",
    "acts-rules": "Act",
}


def scrape_sahkar_vibhag():
    """सहकार विभाग — circulars, GRs व acts-rules चे सर्व pages. एकही page न मिळाल्यास None."""
    base = "https://mahasahakar.maharashtra.gov.in/en/document-category"
    all_results = []
    for cat, doc_type in MS_CATEGORIES.items():
        for page in range(1, 30):
            url = f"{base}/{cat}/" if page == 1 else f"{base}/{cat}/page/{page}/"
            print(f"  → {url}")
            r = get_with_retry(url)
            if r is None or r.status_code != 200:
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
    return all_results or None  # शून्य दस्तऐवज = साइट बदलली किंवा बंद


# ─────────────────── Source 3: GR Portal (सहकार विभाग) ───────────────────
def scrape_gr_portal(known_gr_numbers):
    """gr.maharashtra.gov.in वरील सहकार विभागाचे नवीन शासन निर्णय. Portal अपयशी असल्यास None."""
    grs = gr_portal.fetch_latest(known_ids=known_gr_numbers)
    if not grs:
        return None
    coop = [g for g in grs if "सहकार" in g["department"]]
    print(f"    ✓ सहकार विभाग: {len(coop)} of {len(grs)}")
    return [{
        "source": "GR",
        "title_raw": g["title"],
        "pdf_url": g["pdf_url"],
        "date": g["date"],
        "year": g["year"],
        "doc_type": "GR/Notification",
        "gr_number": g["gr_number"],
        "department": g["department"],
    } for g in coop]


# ─────── पतसंस्था-संबंधित ओळख (⭐ filter साठी) ───────
PATSANSTHA_KEYWORDS = [
    "पतसंस्था", "पत संस्था", "पगारदार", "नियामक मंडळ", "बिगर कृषी", "बिगरशेती",
    "credit societ", "credit co-op", "credit coop", "patsanstha", "salary earner",
    "niyamak", "non-agricultural",
]

# Sahkar Vibhag website वरील गैर-सहकार / अप्रासंगिक दस्तऐवज वगळा
KEYWORDS_EXCLUDE_MS = ["goat", "sheep", "poultry"]


def is_patsanstha(title):
    t = title.lower()
    return any(kw.lower() in t for kw in PATSANSTHA_KEYWORDS)


# ─────────────────── Auto-classify category ───────────────────
# क्रम महत्त्वाचा: पहिला जुळणारा विषय निवडला जातो.
CATEGORY_RULES = [
    # विभागीय आस्थापना — बदली/पदोन्नती इ. (इतर विषयांतील शब्द असले तरी)
    ("Department Staff & Establishment", "👔 विभागीय आस्थापना (बदली/पदोन्नती)",
     ["बदली", "पदोन्नती", "पदस्थापना", "ज्येष्ठता", "सेवाज्येष्ठता", "आस्थापना", "सेवानिवृत्त",
      "वेतनश्रेणी", "पदनिर्मिती", "पद निर्मिती", "पदे भरण्या", "अतिरिक्त कार्यभार", "प्रतिनियुक्ती",
      "transfer by", "promotion", "seniority", "deputation", "career progression", "service continuation",
      "suspension", "departmental enquiry", "presenting officer", "anticorruption", "anti-corruption",
      "vigilance", "group secretory", "group secretary"]),
    ("Acts & Rules", "📜 कायदा व नियम",
     ["mcs act", "mcs rules", "अधिनियम", "नियम, १९६१", "नियम 1961", "अध्यादेश", "act, 1960", "rules, 1961",
      "societies act", "societies rules", "societies (amendment)", "societies ( amendment", "regulation act",
      "regulation rules", "amendment act", "amendments to the maharashtra", "election) rules"]),
    ("Model Bye-laws", "📋 आदर्श उपविधी", ["byelaw", "bye-law", "उपविधी"]),
    ("Niyamak Mandal Framework", "🏛️ नियामक मंडळ रचना", ["niyamak", "नियामक", "मंडळ गठीत"]),
    ("Prudential Norms (CRR/SLR/CRAR/NPA)", "🏦 विवेकपूर्ण निकष",
     ["npa", "crar", "crr", "slr", "विवेकपूर्ण", "non-banking asset", "अनुत्पादक"]),
    ("Audit Classification & Reports", "📊 ऑडिट वर्गीकरण", ["audit classif", "वर्गवारी", "scoring", "गुणांकन"]),
    ("Audit & Empanelment", "🔍 लेखापरीक्षण व नामतालिका",
     ["audit", "auditor", "लेखापरीक्षण", "लेखापरीक्षक", "empanelment", "नामतालिका"]),
    ("KYC, BC & MIS", "🛡️ KYC, BC व MIS", ["kyc", "business correspondent", "mis", "बीसी"]),
    ("Salary Deduction (K-49)", "💼 वेतन कपात", ["क-49", "क-४९", "कलम ४९", "वेतन कपात", "salary deduction"]),
    ("Elections & Administration", "🗳️ निवडणूक व प्रशासन",
     ["election", "निवडणूक", "प्राधिकरण", "प्रशासक", "administrator"]),
    ("Interest Subvention", "💰 व्याज परतावा योजना", ["interest subvention", "व्याज परतावा", "subvention", "व्याज सवलत"]),
    ("OTS, Recovery & Legal", "⚖️ OTS, वसुली व कायदेशीर",
     ["ots", "one time settlement", "सामोपचार", "recovery", "वसुली", "section 156", "कलम १५६", "क-101", "क-१०१", "जप्ती"]),
    ("Inspection & Inquiry", "🔎 तपासणी व चौकशी",
     ["section 89", "कलम ८९", "कलम ८३", "कलम ८८", "inspection", "तपासणी", "चौकशी", "inquiry"]),
    # ── व्यापक सहकार क्षेत्र ──
    ("Cooperative Banks", "🏦 सहकारी बँका",
     ["बँक", "bank"]),
    ("Agri Credit & Crop Loans", "🌾 कृषी पतपुरवठा व पीक कर्ज",
     ["पीक कर्ज", "पीककर्ज", "crop loan", "कर्जमाफी", "कर्जमुक्ती", "कृषी पत", "विकास सोसायटी",
      "विविध कार्यकारी", "प्राथमिक कृषी", "pacs", "शेतकऱ्यांना", "शेतकरी"]),
    ("Housing Societies", "🏘️ गृहनिर्माण संस्था",
     ["गृहनिर्माण", "housing", "पुनर्विकास", "redevelopment", "conveyance", "अभिहस्तांतरण", "अपार्टमेंट"]),
    ("Sugar Cooperatives", "🍬 साखर कारखाने",
     ["साखर", "sugar", "ऊस", "गाळप", "frp"]),
    ("Marketing, APMC & Procurement", "🛒 पणन, बाजार समिती व खरेदी",
     ["पणन", "बाजार समिती", "apmc", "marketing", "हमीभाव", "आधारभूत किंमत", "खरेदी केंद्र",
      "कापूस", "सोयाबीन", "धान", "भरडधान्य", "कांदा", "तूर", "हरभरा", "msp", "nafed", "नाफेड"]),
    ("Textiles & Spinning Mills", "🧵 वस्त्रोद्योग व सूतगिरणी",
     ["वस्त्रोद्योग", "यंत्रमाग", "हातमाग", "सूतगिरणी", "सुतगिरणी", "textile", "powerloom", "handloom", "रेशीम"]),
    ("Labour & Other Societies", "👷 मजूर व इतर संस्था",
     ["मजूर", "labour", "labor", "दुग्ध", "मत्स्य", "dairy", "fisheries"]),
    ("Loan Limits & Rules", "💵 कर्ज मर्यादा व नियम", ["loan limit", "loan rules", "कर्ज मर्यादा", "कर्जमर्यादा", "कर्ज विषयक"]),
    ("Interest Rates & Capital", "💎 भागभांडवल व व्याज दर",
     ["interest rate", "व्याज दर", "deposit", "ठेव", "share holding", "भागभांडवल"]),
    ("Registration & Setup", "📝 नोंदणी व विस्तार", ["registration", "नोंदणी", "expansion", "कार्यक्षेत्र"]),
    ("Schemes, Funds & Grants", "💰 योजना, निधी व अनुदान",
     ["निधी", "अनुदान", "योजना", "वितरण", "अर्थसहाय्य", "fund", "scheme", "grant"]),
    ("Compliance & Reporting", "📈 अनुपालन व अहवाल",
     ["disclosure", "annual report", "compliance", "अनुपालन", "ताळेबंद", "विवरणपत्र", "return"]),
]
DEFAULT_PAT = ("Compliance & Reporting", "📈 अनुपालन व अहवाल")
DEFAULT_OTHER = ("Other Cooperative Decisions", "📄 इतर सहकार निर्णय")


def _matches(keyword, text):
    """छोटे इंग्रजी शब्द (mis, ots, npa…) पूर्ण शब्द म्हणूनच जुळवा — 'Permission' मधील 'mis' नव्हे."""
    k = keyword.lower()
    if k.isascii() and len(k) <= 4:
        return re.search(r"\b" + re.escape(k) + r"\b", text) is not None
    return k in text


def classify_category(title, pat, forced=None):
    if forced:
        return next((c_en, c_mr) for c_en, c_mr, _ in CATEGORY_RULES if c_en == forced)
    t = title.lower()
    for cat_en, cat_mr, kws in CATEGORY_RULES:
        if any(_matches(k, t) for k in kws):
            return cat_en, cat_mr
    return DEFAULT_PAT if pat else DEFAULT_OTHER


SOURCE_FULL = {
    "PNM": "पतसंस्था नियामक मंडळ",
    "MS": "सहकार विभाग, महाराष्ट्र",
    "GR": "शासन निर्णय पोर्टल (gr.maharashtra.gov.in)",
}


def main():
    now = datetime.now(IST)
    print("=" * 70)
    print("  वंदे सहकार — Auto Scraper")
    print(f"  {now.strftime('%Y-%m-%d %H:%M:%S')} IST")
    print("=" * 70)

    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"📁 Existing: {len(existing)} documents")
    else:
        existing = []
        print("📁 Starting fresh")

    existing_urls = {d["pdf_url"] for d in existing} | {d["pdf_url_alt"] for d in existing if d.get("pdf_url_alt")}
    known_gr = {d["gr_number"] for d in existing if d.get("gr_number")}

    print("\n🔍 Source 1: पतसंस्था नियामक मंडळ")
    pnm = scrape_niyamak_mandal()

    print("\n🔍 Source 2: सहकार विभाग")
    ms = scrape_sahkar_vibhag()

    print("\n🔍 Source 3: शासन निर्णय पोर्टल")
    gr = scrape_gr_portal(known_gr)

    failed = [name for name, res in (("Niyamak Mandal", pnm), ("Sahkar Vibhag", ms), ("GR Portal", gr)) if res is None]

    new_count = 0
    for entry in (pnm or []) + (ms or []) + (gr or []):
        if entry["pdf_url"] in existing_urls or entry.get("gr_number") in known_gr:
            continue
        title = entry.get("title_raw", "")
        if entry["source"] == "MS" and any(k in title.lower() for k in KEYWORDS_EXCLUDE_MS):
            continue
        pat = entry["source"] == "PNM" or is_patsanstha(title)
        forced = "Acts & Rules" if entry.get("doc_type") == "Act" else None
        cat_en, cat_mr = classify_category(title, pat, forced)
        new_id = f"NEW-{hashlib.md5(entry['pdf_url'].encode()).hexdigest()[:6].upper()}"
        doc = {
            "id": new_id,
            "title_mr": title,
            "title_en": title,
            "date": entry.get("date") or "—",
            "year": entry.get("year"),
            "category": cat_en,
            "category_mr": cat_mr,
            "source": entry["source"],
            "source_full": SOURCE_FULL[entry["source"]],
            "pdf_url": entry["pdf_url"],
            "doc_type": entry.get("doc_type", "Circular"),
            "tags": ["Auto-detected"],
            "pat": pat,
            "added_on": now.strftime("%Y-%m-%d"),
        }
        if entry.get("gr_number"):
            doc["gr_number"] = entry["gr_number"]
            doc["department"] = entry["department"]
        existing.append(doc)
        existing_urls.add(entry["pdf_url"])
        if entry.get("gr_number"):
            known_gr.add(entry["gr_number"])
        new_count += 1
        print(f"  ⊕ NEW [{cat_en}]{' ⭐' if pat else ''}: {title[:65]}")

    if new_count:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    # last_update फक्त नवीन दस्तऐवज आल्यावर किंवा आठवड्यातून एकदा बदलतो —
    # त्यामुळे निरर्थक commits टळतात, पण repo "active" राहतो (GitHub 60 दिवसांनी schedule बंद करते).
    previous = LAST_UPDATE.read_text(encoding="utf-8").strip()[:10] if LAST_UPDATE.exists() else ""
    stale = previous < (now - timedelta(days=7)).strftime("%Y-%m-%d")
    if new_count or stale:
        LAST_UPDATE.write_text(now.strftime("%Y-%m-%d %H:%M:%S IST"), encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"  ✓ Total:      {len(existing)} documents")
    print(f"  ⊕ New:        {new_count}")
    if failed:
        print(f"  ⚠ Failed:     {', '.join(failed)}")
    print("=" * 70)

    if failed:
        # डेटा आधीच save झाला आहे; हा exit code फक्त Actions मध्ये ✗ दाखवतो
        # जेणेकरून GitHub email ने कळवेल की एखादा स्रोत तपासायला हवा.
        print(f"❌ अयशस्वी स्रोत: {', '.join(failed)} — scraper तपासा")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
