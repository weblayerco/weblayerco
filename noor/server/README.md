# خدمة تقييم النطق · Noor assessment backend

خدمة FastAPI تقيّم نطق الطفل للحرف وتُرجِع نتيجة تطابق `ServerAssessor` في الواجهة.

## العقد / API

`POST /assess` — multipart form-data:
- `audio`: ملف WAV (الواجهة تحوّل تسجيل المتصفح إلى PCM16 أحادي 16kHz، فلا حاجة إلى ffmpeg)
- `letter`: مُعرّف الحرف (مطابق لـ `src/data/curriculum.ts`، مثل `ta2` للطاء)
- `harakah`: `fatha` | `damma` | `kasra`

الاستجابة:
```json
{ "pass": true, "score": 0.62, "heard": "ta2", "message": "أحسنت، نطقٌ صحيح للحرف.", "engine": "dtw-reference" }
```

`GET /health` → `{ "status": "ok", "engine": "..." }`

## المحرّكات واختيارها

يُختار المحرّك عبر متغيّر البيئة `NOOR_ENGINE` (افتراضي `auto`):

| `NOOR_ENGINE` | المحرّك | ملاحظات |
| --- | --- | --- |
| `azure` | **AzureAssessor** | تقييم سحابي بالذكاء الاصطناعي (الأدقّ) — يحتاج مفتاح |
| `dtw` | **ReferenceDtwAssessor** | مقارنة MFCC+DTW مع مراجع صوتية محلية |
| `energy` | **EnergyAssessor** | يكتشف "لا يوجد صوت" فقط (احتياطي) |
| `auto` | تلقائي | Azure إن وُجد مفتاح، وإلا DTW إن وُجدت مراجع، وإلا energy |

- **AzureAssessor**: يرسل صوت الطفل والنصّ المرجعي (الحرف بالحركة) إلى
  Azure Pronunciation Assessment عبر REST، ويأخذ درجة الدقّة لكل فونيم، فينجح
  إذا تجاوزت العتبة (`NOOR_PASS_THRESHOLD`، افتراضي 80).
- **ReferenceDtwAssessor**: يستخرج بصمة MFCC ويقارنها عبر DTW بمراجع الحرف الهدف
  والحروف المتشابهة (ط مقابل ت/د/ض…). ينجح فقط إذا كان أقرب للهدف بهامش واضح.

### تفعيل التقييم السحابي (Azure)

1. أنشئ مورد **Speech** في Azure واحصل على المفتاح والمنطقة (Region).
2. شغّل الخادم بهذه المتغيّرات:
   ```bash
   export AZURE_SPEECH_KEY="<المفتاح>"
   export AZURE_SPEECH_REGION="westeurope"   # منطقة موردك
   export NOOR_ENGINE=azure
   export NOOR_AZURE_LOCALE=ar-SA            # أو ar-EG ...
   export NOOR_PASS_THRESHOLD=80             # عتبة النجاح 0..100
   uvicorn app.main:app --port 8000
   ```
3. تحقّق: `GET /health` يجب أن يُظهر `"engine": "azure"`.

> **التكلفة/الخصوصية:** كل طلب تقييم يُحاسَب عليه Azure، والصوت يُرسَل إلى الخدمة —
> احصل على موافقة وليّ الأمر ولا تُخزّن التسجيلات. راجع تسعير Azure Speech.

> **حدود الدقة:** عند غياب Azure، تبقى مقارنة MFCC+DTW أساساً جيّداً لكنه أضعف من
> نموذج سحابي/مُدرَّب. الواجهة (`Assessor`) مصمّمة للاستبدال دون تغيير الـ API.

## التشغيل

```bash
cd noor/server
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest            # تشغيل الاختبارات
```

ثم في الواجهة اضبط `VITE_ASSESS_URL=http://localhost:8000/assess`.

## إضافة المراجع الصوتية

1. سجّل قارئاً ينطق كل حرف بكل حركة، واحفظ الملفات باسم `{letter}__{harakah}__{idx}.wav`
   (مثل `ta2__fatha__1.wav`) في مجلد `raw_audio/`.
2. ولّد المراجع:
   ```bash
   python -m scripts.build_references --in ./raw_audio --out ./references
   ```
3. أعد تشغيل الخادم — سيتحوّل تلقائياً إلى محرّك `dtw-reference`.

## الخطوة التالية الموصى بها

أثبت الجدوى على ٤–٥ حروف صعبة فقط (ط ض ص ق ع) بمراجع حقيقية وقياس دقّة التمييز
قبل التوسّع، ثم فكّر في نموذج مُدرَّب إذا لزم رفع الدقّة.
