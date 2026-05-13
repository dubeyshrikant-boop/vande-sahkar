#!/usr/bin/env python3
"""
=====================================================================
 वंदे सहकार — HTML Builder
 scripts/template.html + data/circulars.json + assets/* पासून
 index.html तयार करते. Scrape नंतर weekly workflow मध्ये चालते.
=====================================================================
"""
import json
import io
import base64
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "scripts" / "template.html"
DATA_FILE = ROOT / "data" / "circulars.json"
LAST_UPDATE = ROOT / "data" / "last_update.txt"
OUTPUT = ROOT / "index.html"

ASSET_LOGO = ROOT / "assets" / "logo.jpg"
ASSET_PHOTO = ROOT / "assets" / "ca_dubey.jpg"
ASSET_QR = ROOT / "assets" / "whatsapp_qr.png"


def optimize_to_b64(path, max_size, quality=85, fmt=None):
    """Image optimize करून base64 string return करते."""
    try:
        from PIL import Image
        img = Image.open(path).convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        use_fmt = fmt or ("PNG" if path.suffix.lower() == ".png" else "JPEG")
        if use_fmt == "PNG":
            img.save(buf, format="PNG", optimize=True)
        else:
            img.save(buf, format="JPEG", quality=quality, optimize=True)
        return base64.b64encode(buf.getvalue()).decode("ascii")
    except ImportError:
        return base64.b64encode(path.read_bytes()).decode("ascii")


def to_marathi(s):
    m = {"0":"०","1":"१","2":"२","3":"३","4":"४","5":"५","6":"६","7":"७","8":"८","9":"९"}
    return "".join(m.get(c, c) for c in str(s))


def main():
    print("=" * 70)
    print(f"  वंदे सहकार — HTML Builder · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    if not TEMPLATE.exists():
        print(f"❌ Template missing: {TEMPLATE}")
        return 1
    if not DATA_FILE.exists():
        print(f"❌ Data missing: {DATA_FILE}")
        return 1

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    print(f"📁 Loaded {len(data)} circulars")

    total = len(data)
    pnm_count = sum(1 for d in data if "PNM" in d.get("source", ""))
    ms_count = sum(1 for d in data if d.get("source") in ("MS", "PNM+MS"))
    years = sorted({d["year"] for d in data if d.get("year")})
    year_span = f"{to_marathi(min(years))} — {to_marathi(max(years))}" if years else "—"

    print("🖼️  Optimizing images...")
    logo_b64 = optimize_to_b64(ASSET_LOGO, (300, 300), 82)
    photo_b64 = optimize_to_b64(ASSET_PHOTO, (600, 600), 85)
    qr_b64 = optimize_to_b64(ASSET_QR, (400, 400), 88, "PNG")
    print(f"   logo: {len(logo_b64)//1024} KB · photo: {len(photo_b64)//1024} KB · qr: {len(qr_b64)//1024} KB")

    template = TEMPLATE.read_text(encoding="utf-8")
    data_js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    replacements = {
        "__LOGO_B64__": logo_b64,
        "__PHOTO_B64__": photo_b64,
        "__QR_B64__": qr_b64,
        "__DATA_JS__": data_js,
        "__TOTAL__": to_marathi(total),
        "__PNM_COUNT__": to_marathi(pnm_count),
        "__MS_COUNT__": to_marathi(ms_count),
        "__YEAR_SPAN__": year_span,
        "__TOTAL_INLINE__": to_marathi(total),
        "__PNM_INLINE__": to_marathi(pnm_count),
        "__MS_INLINE__": to_marathi(ms_count),
    }
    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"✓ Written {OUTPUT.name} ({len(html)//1024} KB)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
