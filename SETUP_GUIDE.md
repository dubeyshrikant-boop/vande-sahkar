# 🚀 वंदे सहकार — Setup मार्गदर्शन

> GitHub वर deploy करण्याची संपूर्ण step-by-step मार्गदर्शिका.
> **तांत्रिक ज्ञान आवश्यक नाही** — फक्त mouse-click करायचे आहे.

---

## ⏱️ संपूर्ण process: फक्त १५-२० मिनिटे

| टप्पा | वेळ |
|------|-----|
| १. GitHub खाते उघडणे | ५ मिनिटे |
| २. Repository तयार करणे | २ मिनिटे |
| ३. Files upload करणे | ५ मिनिटे |
| ४. GitHub Pages enable करणे | २ मिनिटे |
| ५. Site live होणे | ३-५ मिनिटे (automatic) |

---

## 📋 टप्पा १: GitHub खाते उघडणे

> *जर तुमचे आधीच GitHub खाते असेल, तर हा टप्पा वगळा.*

### स्टेप १.१: GitHub.com वर जा

ब्राउझरमध्ये **[github.com](https://github.com)** उघडा.

### स्टेप १.२: "Sign up" वर क्लिक करा

वरच्या उजव्या कोपऱ्यात **"Sign up"** button आहे.

### स्टेप १.३: माहिती भरा

- **Email:** तुमचा email address
- **Password:** मजबूत password (किमान ८ अक्षरे)
- **Username:** तुम्हाला आवडेल असे username
  - उदा: `cashrikantdubey`, `vandesahkar`, `cadubey-mh`
  - *टीप: हे username तुमच्या site च्या URL मध्ये येईल, म्हणून simple ठेवा*

### स्टेप १.४: Email verify करा

GitHub कडून email येईल — त्यातील link वर क्लिक करा.

### स्टेप १.५: Free plan निवडा

"Continue for free" वर क्लिक करा.

✅ **खाते तयार झाले!**

---

## 📂 टप्पा २: Repository तयार करणे

### स्टेप २.१: नवीन Repo साठी क्लिक करा

GitHub homepage वर वरच्या उजव्या कोपऱ्यात **"+" icon** आहे → त्यावर क्लिक करा → **"New repository"** निवडा.

किंवा थेट या link वर जा: **[github.com/new](https://github.com/new)**

### स्टेप २.२: Repository माहिती भरा

| Field | काय भरायचे |
|-------|------------|
| **Repository name** | `vande-sahkar` *(हेच name ठेवा)* |
| **Description** *(optional)* | `वंदे सहकार — महाराष्ट्र सहकारी परिपत्रक भांडार` |
| **Public / Private** | **Public** निवडा *(GitHub Pages साठी आवश्यक)* |
| **Add a README file** | ❌ हे **uncheck** ठेवा |
| **Add .gitignore** | ❌ हे **uncheck** ठेवा |
| **Choose a license** | ❌ हे **uncheck** ठेवा |

### स्टेप २.३: "Create repository" क्लिक करा

खालचा हिरवा **"Create repository"** button क्लिक करा.

✅ **Repository तयार झाली!**

---

## 📤 टप्पा ३: सर्व Files upload करणे

### स्टेप ३.१: Upload screen उघडा

नवीन repository page वर तुम्हाला असे काहीतरी दिसेल:

> "Quick setup — if you've done this kind of thing before"

खाली scroll करून **"uploading an existing file"** या निळ्या link वर क्लिक करा.

किंवा या URL वर थेट जा *(USERNAME त्याजागी तुमचे username टाका)*:
```
https://github.com/USERNAME/vande-sahkar/upload/main
```

### स्टेप ३.२: सर्व files drag-and-drop करा

तुमच्या computer वरील `vande-sahkar` फोल्डर उघडा. आत खालील files/folders आहेत:

```
vande-sahkar/
├── README.md
├── SETUP_GUIDE.md
├── index.html
├── assets/      (3 files)
├── data/        (2 files)
├── scripts/     (3 files)
└── .github/     (workflow file)
```

**सर्व निवडा** (Ctrl+A किंवा Cmd+A) आणि **browser window मध्ये drag करा**.

> *टीप: GitHub web upload ने एका वेळी संपूर्ण folder upload होते. जर upload नाही झाले तर "GitHub Desktop" app वापरा — खाली पर्याय देत आहे.*

### स्टेप ३.३: Commit करा

खाली scroll करा → **"Commit changes"** section मध्ये:
- **Commit message:** `Initial commit — Vande Sahkar v3.0`
- खालचा हिरवा **"Commit changes"** button क्लिक करा

✅ **सर्व files upload झाल्या!**

---

### 🔄 पर्यायी: GitHub Desktop वापरून (recommended for large folders)

जर web upload मध्ये त्रास येत असेल, तर **GitHub Desktop** हे app वापरा:

1. **[desktop.github.com](https://desktop.github.com)** वरून app download करा
2. Install करून आपल्या GitHub खात्याने sign in करा
3. **"Clone a repository"** → आपली `vande-sahkar` repo निवडा → local folder निवडा
4. `vande-sahkar` folder मधील सर्व files त्या local folder मध्ये copy करा
5. GitHub Desktop मध्ये बदल दिसतील — खाली **commit message** लिहा (`Initial commit`)
6. **"Commit to main"** → मग **"Push origin"** क्लिक करा

✅ Done!

---

## 🌐 टप्पा ४: GitHub Pages enable करणे

### स्टेप ४.१: Repository Settings उघडा

आपल्या `vande-sahkar` repository मध्ये जा → वरच्या tabs मधून **"Settings"** क्लिक करा.

### स्टेप ४.२: Pages section उघडा

डाव्या sidebar मध्ये **"Pages"** क्लिक करा.

### स्टेप ४.३: Source निवडा

**"Build and deployment"** section मध्ये:
- **Source:** dropdown मधून **"GitHub Actions"** निवडा *(हा सर्वात important step आहे)*

### स्टेप ४.४: Workflow सुरू होईल

GitHub आता automatic आपला `weekly-update.yml` workflow ओळखेल आणि चालवेल.

---

## ⚡ टप्पा ५: Workflow manual चालवा

### स्टेप ५.१: Actions tab उघडा

Repository वरच्या tabs मधून **"Actions"** क्लिक करा.

### स्टेप ५.२: Workflow निवडा

डाव्या sidebar मध्ये **"साप्ताहिक परिपत्रक update"** workflow दिसेल → क्लिक करा.

### स्टेप ५.३: "Run workflow" क्लिक करा

उजवीकडे **"Run workflow"** dropdown → हिरवा **"Run workflow"** button क्लिक करा.

### स्टेप ५.४: २-३ मिनिटे वाट पहा

Workflow चालू आहे — पिवळा गोल दिसेल. तो हिरवा ✓ झाला म्हणजे success.

✅ **Site आता live आहे!**

---

## 🎉 तुमची site live झाली!

URL: `https://USERNAME.github.io/vande-sahkar/`

*(USERNAME त्याजागी तुमचे GitHub username)*

उदा: जर तुमचे username `cashrikantdubey` असेल, तर:
```
https://cashrikantdubey.github.io/vande-sahkar/
```

---

## 🔄 दर आठवड्याला automatic update

आता काहीही करावे लागत नाही:

- **दर रविवारी पहाटे ८:३० (IST)** — workflow automatic चालतो
- दोन्ही शासकीय संकेतस्थळे scrape करतो
- नवीन परिपत्रके सापडली तर add करतो
- Site पुन्हा deploy करतो
- तुम्हाला email मध्ये notification येऊ शकते

---

## 📱 WhatsApp वर share कसे करायचे?

खालील message copy करा आणि WhatsApp वर पाठवा *(USERNAME बदला)*:

```
🙏 सहकारी पतसंस्थांसाठी मोफत भांडार

महाराष्ट्रातील सर्व सहकारी पतसंस्थांसाठी अधिकृत
परिपत्रके, GR, अधिनियम, आदर्श उपविधी एका ठिकाणी
— पूर्णपणे मोफत.

👉 https://USERNAME.github.io/vande-sahkar/

— CA श्रीकांत दुबे
सदस्य, पतसंस्था नियामक मंडळ
📞 ९४०३ ५८६ ९००
```

---

## 🆘 अडचण आली तर?

### प्रश्न: "Site 404 दिसते"

**उत्तर:** ३-५ मिनिटे वाट पहा. पहिल्या deployment ला थोडा वेळ लागतो. नंतरही दिसले नाही तर:
- Settings → Pages → Source: **"GitHub Actions"** निवडले आहे का तपासा
- Actions tab मध्ये workflow हिरवा ✓ झाला आहे का पहा

### प्रश्न: "Workflow fail होतो आहे"

**उत्तर:** Actions tab मध्ये जाऊन latest run वर क्लिक करा → error log पहा. सहसा कारणे:
- Permissions चुकीचे — Settings → Actions → General → Workflow permissions: **"Read and write"** निवडा
- Source सरकारी website temporarily down असेल — पुढच्या weekly run मध्ये retry होईल

### प्रश्न: "मला custom domain पाहिजे (उदा: sahkarbhandar.in)"

**उत्तर:** डोमेन खरेदी करा (GoDaddy / Namecheap), मग:
- Repository Settings → Pages → Custom domain → `sahkarbhandar.in` टाका
- तुमच्या डोमेन provider कडे `CNAME` record set करा (USERNAME.github.io)
- SSL automatic enable होईल (HTTPS)

### प्रश्न: "नवीन परिपत्रक मला manual add करायचे आहे"

**उत्तर:** `data/circulars.json` file वर GitHub web interface वर थेट edit करा (pencil icon). नवीन entry add करून commit करा. Workflow आपोआप index.html re-build करेल.

---

## 📞 अधिक मदत हवी असल्यास

CA श्रीकांत दुबे
📞 ९४०३ ५८६ ९००
💬 WhatsApp: [wa.me/919403586900](https://wa.me/919403586900)
👥 [WhatsApp Group](https://chat.whatsapp.com/G0lxPU0bckgCGjKdS3CNlN?mode=gi_t)

---

**"सहकारातून समृद्धीकडे"** · वंदे सहकार · EST. 2026
