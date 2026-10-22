#!/usr/bin/env python3
"""
=====================================================================
 gr.maharashtra.gov.in — शासन निर्णय पोर्टल reader
 Portal वरील "नवीन शासन निर्णय" यादी (~शेवटचा आठवडा, १० प्रति पान)
 पान-दर-पान वाचते. आधीच माहीत असलेल्या GR पर्यंत पोहोचल्यावर थांबते,
 त्यामुळे एका दिवसात कितीही GR आले तरी एकही सुटत नाही.
=====================================================================
"""
import re
import time

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LIST_URL = "https://gr.maharashtra.gov.in/1145/Government-Resolutions"
PDF_URL_BASE = "https://gr.maharashtra.gov.in/Site/Upload/Government%20Resolutions/Marathi/"
NEXT_TARGET = "ctl00$SitePH$ucPaging$lnkNext"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "mr,en-US;q=0.7,en;q=0.3",
}


def _parse_rows(html):
    grs = []
    for tr in BeautifulSoup(html, "lxml").find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 6:
            continue
        sr = cells[0].get_text(strip=True)
        if not sr.replace(".", "").isdigit():
            continue
        doc_id = cells[3].get_text(strip=True)
        parts = cells[4].get_text(strip=True).split("-")
        if not doc_id.isdigit() or len(parts) != 3:
            continue
        d, m, y = parts
        grs.append({
            "department": cells[1].get_text(" ", strip=True),
            "title": cells[2].get_text(" ", strip=True),
            "gr_number": doc_id,
            "date": f"{y}-{m.zfill(2)}-{d.zfill(2)}",
            "year": int(y),
            "pdf_url": f"{PDF_URL_BASE}{doc_id}.pdf",
        })
    return grs


DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def _total_pages(html):
    m = re.search(r'id="SitePH_ucPaging_lblTotalPages"[^>]*>([^<]+)<', html)
    digits = m.group(1).strip().translate(DEVANAGARI_DIGITS) if m else ""
    return int(digits) if digits.isdigit() else None


def _form_fields(html):
    soup = BeautifulSoup(html, "lxml")
    fields = {}
    for inp in soup.find_all("input"):
        name = inp.get("name")
        if name and inp.get("type") not in ("submit", "image", "radio", "checkbox"):
            fields[name] = inp.get("value", "")
    for sel in soup.find_all("select"):
        opt = sel.find("option", selected=True) or sel.find("option")
        fields[sel["name"]] = opt.get("value", "") if opt else ""
    for radio in soup.find_all("input", type="radio", checked=True):
        fields[radio["name"]] = radio.get("value", "")
    return fields


def _request(session, method, **kw):
    for attempt in range(1, 4):
        try:
            r = session.request(method, LIST_URL, timeout=90, verify=False, **kw)
            if r.status_code == 200:
                return r
            print(f"    ✗ HTTP {r.status_code} (attempt {attempt})")
        except Exception as e:
            print(f"    ✗ {e} (attempt {attempt})")
        time.sleep(5 * attempt)
    return None


def fetch_latest(known_ids=(), max_pages=60, stop_after_known_pages=2):
    """
    Portal वरील नवीन GRs परत करते (सर्व विभाग).
    known_ids मधील GR सलग `stop_after_known_pages` पानांवर पूर्णपणे सापडल्यास थांबते.
    Portal पोहोचू न शकल्यास None परत करते (म्हणजे "अपयश", "शून्य GR" नव्हे).
    """
    known = set(known_ids)
    session = requests.Session()
    session.headers.update(HEADERS)

    print(f"  → {LIST_URL}")
    r = _request(session, "GET")
    if r is None:
        return None

    total_pages = _total_pages(r.text) or max_pages
    results, seen, known_streak = [], set(), 0
    for page in range(1, min(max_pages, total_pages) + 1):
        rows = _parse_rows(r.text)
        if not rows:
            break
        fresh = [g for g in rows if g["gr_number"] not in seen]
        if not fresh:  # portal ने तेच पान परत दिले — यादी संपली
            break
        for g in fresh:
            seen.add(g["gr_number"])
            results.append(g)
        known_streak = known_streak + 1 if all(g["gr_number"] in known for g in fresh) else 0
        if known and known_streak >= stop_after_known_pages:
            break
        if page >= total_pages:
            break

        fields = _form_fields(r.text)
        fields["__EVENTTARGET"] = NEXT_TARGET
        fields["__EVENTARGUMENT"] = ""
        time.sleep(1)
        r = _request(session, "POST", data=fields)
        if r is None:
            break

    print(f"    ✓ {len(results)} GRs read from {page} page(s)")
    return results


if __name__ == "__main__":
    grs = fetch_latest(max_pages=3)
    for g in (grs or [])[:5]:
        print(g["date"], g["department"][:30], "|", g["title"][:60])
