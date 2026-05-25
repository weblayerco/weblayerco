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

## كيف يعمل المحرّك

- **EnergyAssessor** (افتراضي عند غياب المراجع): يكتشف "لا يوجد صوت" فقط.
- **ReferenceDtwAssessor**: يستخرج بصمة MFCC من محاولة الطفل ويقارنها عبر DTW
  بمراجع الحرف الهدف ومراجع الحروف المتشابهة (ط مقابل ت/د/ض…). ينجح فقط إذا
  كانت المحاولة أقرب إلى الحرف الهدف بهامش واضح.

> **حدود الدقة:** مقارنة MFCC+DTW أساس كلاسيكي جيّد لكنه ليس بقوة نموذج مُدرَّب
> على كلام أطفال مُعنون. الواجهة (`Assessor`) مصمّمة للاستبدال، فيمكن لاحقاً وضع
> نموذج صوتي/GOP مكان `ReferenceDtwAssessor` دون تغيير الـ API.

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
