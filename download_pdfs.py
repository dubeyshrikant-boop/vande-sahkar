#!/usr/bin/env python3
"""
==========================================================================
  वंदे सहकार · Vande Sahkar — PDF Downloader
==========================================================================
  सर्व ६० अधिकृत परिपत्रके, GR, अधिनियम, उपविधी एका click मध्ये
  आपल्या computer वर download करते — विषयानुसार folders मध्ये.

  वापर पद्धत:
  ─────────────
    1. Python 3.7+ install असणे आवश्यक
    2. terminal/command-prompt मध्ये जा
    3. हा command चालवा:
           pip install requests
    4. नंतर:
           python download_pdfs.py

  ─────────────────────────────────────────────────────────────────────
  CA श्रीकांत जगदीशप्रसाद दुबे
  सदस्य, पतसंस्था नियामक मंडळ, महाराष्ट्र राज्य
  📞 ९४०३ ५८६ ९००   ·   💬 wa.me/919403586900

  WhatsApp ग्रुप: chat.whatsapp.com/G0lxPU0bckgCGjKdS3CNlN
  ─────────────────────────────────────────────────────────────────────
  "सहकारातून समृद्धीकडे — वंदे सहकार"   ·   EST. 2026 · संवत् २०८३
==========================================================================
"""
import json
import sys
import os
import re
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("\n❌ 'requests' library missing. Install करण्यासाठी:")
    print("   pip install requests\n")
    sys.exit(1)


def safe_name(s, max_len=80):
    """File name सुरक्षित करा."""
    s = re.sub(r'[\\/:*?"<>|]', '_', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:max_len]


def download_file(url, dest, session, headers):
    """Single PDF download with progress."""
    try:
        r = session.get(url, headers=headers, timeout=120, stream=True, allow_redirects=True)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        total = int(r.headers.get('content-length', 0))
        downloaded = 0
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        kb = downloaded // 1024
        return True, f"{kb} KB"
    except Exception as e:
        return False, str(e)[:60]


def main():
    print("=" * 76)
    print("                     वंदे सहकार · Vande Sahkar")
    print("                      परिपत्रक PDF Downloader")
    print("                   CA श्रीकांत जगदीशप्रसाद दुबे")
    print("=" * 76)

    # Load data
    here = Path(__file__).resolve().parent
    json_paths = [here / "data" / "circulars.json", here / "circulars.json"]
    data_file = None
    for p in json_paths:
        if p.exists():
            data_file = p
            break
    if not data_file:
        print(f"\n❌ circulars.json not found in {here} or {here / 'data'}")
        sys.exit(1)

    with open(data_file, encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n📁 एकूण {len(data)} दस्तऐवज download करायचे आहेत.")
    print(f"📂 Output folder: ./Vande_Sahkar_PDFs/")
    print()

    confirm = input("➤ पुढे जायचे का? (y/n): ").strip().lower()
    if confirm not in ('y', 'yes', 'हो', 'h'):
        print("\nरद्द केले.")
        return

    base = here / "Vande_Sahkar_PDFs"
    base.mkdir(exist_ok=True)

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*;q=0.8",
    }

    success = 0
    failed = []
    print()
    print("─" * 76)

    for idx, doc in enumerate(data, 1):
        category = safe_name(doc.get('category_mr', doc.get('category', 'इतर')))
        cat_dir = base / category
        cat_dir.mkdir(exist_ok=True)

        title = doc.get('title_mr') or doc.get('title_en') or doc.get('id', 'untitled')
        year = doc.get('year') or 'NoYr'
        prefix = f"{year}_{doc.get('id', '')}"
        filename = safe_name(f"{prefix}_{title}") + ".pdf"
        dest = cat_dir / filename

        if dest.exists():
            print(f"  [{idx:2d}/{len(data)}] ✓ Already exists: {title[:55]}")
            success += 1
            continue

        url = doc.get('pdf_url', '')
        if not url:
            print(f"  [{idx:2d}/{len(data)}] ✗ No URL: {title[:55]}")
            failed.append((title, "No URL"))
            continue

        print(f"  [{idx:2d}/{len(data)}] ⬇ {title[:60]}", end=" ", flush=True)
        ok, info = download_file(url, dest, session, headers)
        if ok:
            print(f"✓ {info}")
            success += 1
        else:
            print(f"✗ {info}")
            failed.append((title, info))
            if dest.exists():
                dest.unlink()

    print("─" * 76)
    print(f"\n📊 निकाल:")
    print(f"   ✓ Success: {success}/{len(data)}")
    print(f"   ✗ Failed:  {len(failed)}/{len(data)}")
    print(f"\n📂 Files saved in: {base.resolve()}")

    if failed:
        print(f"\n⚠️  खालील files download नाही झाल्या:")
        for title, reason in failed:
            print(f"   • {title[:50]:50s}  →  {reason}")

    print()
    print("=" * 76)
    print("  धन्यवाद! · वंदे सहकार · WhatsApp ग्रुपात सामील व्हा:")
    print("  https://chat.whatsapp.com/G0lxPU0bckgCGjKdS3CNlN")
    print("=" * 76)


if __name__ == "__main__":
    main()
