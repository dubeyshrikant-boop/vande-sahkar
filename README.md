# 🇮🇳 वंदे सहकार · Vande Sahkar

> **सहकारातून समृद्धीकडे** · EST. 2026 · संवत् २०८३

महाराष्ट्र राज्यातील सर्व नागरी, ग्रामीण व पगारदार सहकारी पतसंस्थांसाठी अधिकृत परिपत्रकांचा एकत्रित, **पूर्णपणे मोफत** स्रोत.

🌐 **Live dashboard:** [https://USERNAME.github.io/vande-sahkar/](https://USERNAME.github.io/vande-sahkar/)
*(GitHub Pages enable केल्यानंतर USERNAME त्याजागी तुमचे GitHub username येईल.)*

📱 **WhatsApp ग्रुप जॉईन करा:** [chat.whatsapp.com/G0lxPU0bckgCGjKdS3CNlN](https://chat.whatsapp.com/G0lxPU0bckgCGjKdS3CNlN?mode=gi_t)

---

## 📋 हा उपक्रम काय आहे?

महाराष्ट्र राज्यात आज **१९,४७६ बिगर-कृषी सहकारी पतसंस्था** कार्यरत आहेत:

| प्रकार | संख्या |
|--------|--------|
| नागरी सहकारी पतसंस्था | ८,३९४ |
| ग्रामीण बिगर-कृषी पतसंस्था | ५,२४३ |
| पगारदार कर्मचारी पतसंस्था | ५,८३९ |
| **एकूण** | **१९,४७६** |

या सर्व संस्थांचे संचालक मंडळ, सेवक, सभासद आणि लेखापरीक्षक यांना **शासन व पतसंस्था नियामक मंडळ** यांची परिपत्रके वेळोवेळी आवश्यक असतात. परंतु ती अनेक संकेतस्थळांवर विखुरलेली असल्याने शोधणे कठीण जाते.

**हीच गरज लक्षात घेऊन** हा सेवा-उपक्रम तयार केला आहे — सर्व अधिकृत दस्तऐवज एका ठिकाणी, विषयानुसार वर्गीकृत, **अगदी मोफत**.

---

## 🌟 वैशिष्ट्ये

- ✅ **६० अधिकृत दस्तऐवज** दोन्ही स्रोतांकडून संकलित
- ✅ **दर आठवड्याला automatic update** — GitHub Actions कडून
- ✅ **१६ विषयांनुसार वर्गीकरण** — झटपट हवे ते सापडते
- ✅ **पूर्ण मराठी interface** — देवनागरी अंकांसह
- ✅ **WhatsApp ग्रुप integration** — समुदायात सामील व्हा
- ✅ **मोबाईल-friendly** — कुठेही, कधीही, कोणत्याही device वर
- ✅ **पूर्णपणे मोफत** — कोणताही व्यावसायिक हेतू नाही

---

## 📁 अधिकृत स्रोत

1. **पतसंस्था नियामक मंडळ, महाराष्ट्र**
   🔗 [patsansthaniyamakmandal.in](https://patsansthaniyamakmandal.in/Home/DownloadSections)
   *— पतसंस्थांचा थेट नियामक · ३९ दस्तऐवज*

2. **सहकार विभाग, महाराष्ट्र शासन**
   🔗 [mahasahakar.maharashtra.gov.in](https://mahasahakar.maharashtra.gov.in/)
   *— सहकार, पणन व वस्त्रोद्योग · २५ दस्तऐवज*

---

## 🤖 Automatic Update कसे चालते?

```
दर रविवारी पहाटे ८:३० (IST)
        ↓
GitHub Actions workflow सुरू होतो
        ↓
दोन्ही शासकीय संकेतस्थळे scrape करतो
        ↓
नवीन परिपत्रके सापडली का?
        ├─ हो  → data/circulars.json मध्ये add करा
        └─ नाही → कोणताही बदल नाही
        ↓
index.html re-build करा
        ↓
GitHub Pages वर deploy करा
        ↓
✓ Site live!
```

**Schedule:** दर रविवारी पहाटे ८:३० भारतीय वेळेला (cron: `0 3 * * 0` UTC).
**Manual trigger:** GitHub repo च्या Actions tab मधून "Run workflow" button.

---

## 📂 Folder structure

```
vande-sahkar/
├── 📄 README.md                 (हा file)
├── 📄 SETUP_GUIDE.md            (मराठीत step-by-step मार्गदर्शन)
├── 🌐 index.html                (Live dashboard)
├── 📂 assets/
│   ├── logo.jpg                 (वंदे सहकार logo)
│   ├── ca_dubey.jpg             (CA Dubey photo)
│   └── whatsapp_qr.png          (WhatsApp ग्रुप QR)
├── 📂 data/
│   ├── circulars.json           (Master dataset — auto-updated)
│   └── last_update.txt          (शेवटची update timestamp)
├── 📂 scripts/
│   ├── scrape.py                (Source 1 + 2 scraper)
│   ├── build.py                 (HTML generator)
│   └── template.html            (HTML template with placeholders)
└── 📂 .github/workflows/
    └── weekly-update.yml        (GitHub Actions cron job)
```

---

## 🚀 Setup कसे करायचे?

संपूर्ण step-by-step मार्गदर्शन मराठीत: **[SETUP_GUIDE.md](SETUP_GUIDE.md)** पहा.

संक्षेपात:

1. GitHub.com वर खाते उघडा (मोफत)
2. नवीन repository तयार करा — name: `vande-sahkar` (public)
3. या फोल्डरमधील सर्व files upload करा
4. Settings → Pages → Source: **GitHub Actions** निवडा
5. ✓ Site `https://USERNAME.github.io/vande-sahkar/` वर live होईल
6. दर आठवड्याला automatic update — काहीही करावे लागत नाही

---

## 📊 दस्तऐवज वर्गीकरण

| क्र. | विषय | प्रकार |
|------|------|--------|
| १ | 📜 कायदा व नियम | MCS Act 1960, Rules 1961 |
| २ | 🏛️ नियामक मंडळ रचना | पतसंस्था नियामक मंडळ framework |
| ३ | 📋 आदर्श उपविधी | Patsanstha + Pagardar 2025-26 |
| ४ | 📝 नोंदणी व विस्तार | Registration & branch expansion |
| ५ | 💵 कर्ज मर्यादा व नियम | Loan limits & rules |
| ६ | 🏦 विवेकपूर्ण निकष | CRR / SLR / CRAR / NPA |
| ७ | 🔍 लेखापरीक्षण व नामतालिका | Audit & empanelment |
| ८ | 📊 ऑडिट वर्गीकरण | A / B / C / D classification |
| ९ | 💰 व्याज परतावा योजना | Interest subvention schemes |
| १० | 💎 भागभांडवल व व्याज दर | Capital & interest rates |
| ११ | ⚖️ OTS, वसुली व कायदेशीर | OTS, K-101, recovery |
| १२ | 🛡️ KYC, BC व MIS | Compliance frameworks |
| १३ | 📈 अनुपालन व अहवाल | Reporting requirements |
| १४ | 💼 वेतन कपात (क-४९) | Salary deduction for employees |
| १५ | 🗳️ निवडणूक व प्रशासन | Elections & administration |
| १६ | 🔎 तपासणी व चौकशी | Inspection & inquiry (Sec 89) |

---

## 👤 उपक्रम संस्थापक

**CA श्रीकांत जगदीशप्रसाद दुबे**
सनदी लेखापाल · ICAI
सदस्य, पतसंस्था नियामक मंडळ, महाराष्ट्र राज्य
*राज्यातील एकमेव CA सदस्य या नियामक मंडळावर*
३०+ वर्षांचा सहकार लेखापरीक्षण व सल्लागार अनुभव

📞 ९४०३ ५८६ ९००
💬 [WhatsApp](https://wa.me/919403586900)
👥 [WhatsApp Group](https://chat.whatsapp.com/G0lxPU0bckgCGjKdS3CNlN?mode=gi_t)

---

## 📜 कायदेशीर सूचना

- सर्व दस्तऐवज महाराष्ट्र शासन व पतसंस्था नियामक मंडळ यांच्या **अधिकृत सार्वजनिक संकेतस्थळांवरून** घेतले आहेत.
- कोणत्याही दस्तऐवजावर कोणताही copyright दावा केला जात नाही.
- हा उपक्रम **पूर्णपणे मोफत** सेवा आहे — कोणत्याही व्यावसायिक हेतूशिवाय.
- अद्ययावत व अधिकृत प्रत मूळ शासकीय संकेतस्थळावरून तपासावी.

---

## 🤝 योगदान

जर तुम्हाला कोणतीही चूक आढळली किंवा सूचना द्यायची असेल:
- WhatsApp: [९४०३ ५८६ ९००](https://wa.me/919403586900)
- GitHub Issues: या repo वर Issue उघडा

---

**"सहकारातून समृद्धीकडे — वंदे सहकार"**
*— सहकार चळवळीच्या बळकटीकरणासाठी समर्पित*
