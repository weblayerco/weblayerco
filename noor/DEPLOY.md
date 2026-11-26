# نشر "نور" على رابط عام مع الذكاء الاصطناعي

الهدف: رابط واحد (HTTPS) يفتحه طفلك على الهاتف، يعمل فيه الميكروفون والتقييم الآلي.
الفكرة: خدمة **واحدة** (FastAPI) تخدم التطبيق + واجهة التقييم من نفس الرابط، لذلك
لا حاجة لاستضافة منفصلة ولا إعدادات CORS.

> أمران لا يمكن لأحدٍ فعلهما نيابةً عنك لأنهما يخصّان حسابك:
> 1) إنشاء **مفتاح Azure**، 2) ربط الاستضافة بحسابك. الخطوات أدناه دقيقة وسريعة.

---

## الخطوة ١: مفتاح Azure Speech (للتقييم بالذكاء الاصطناعي)
1. ادخل إلى <https://portal.azure.com> وأنشئ مورد **Speech** (Speech service).
2. اختر منطقة (Region) مثل `westeurope`، وأكمل الإنشاء.
3. من صفحة المورد: **Keys and Endpoint** → انسخ **KEY 1** و **Region**.

> تكلفة: هناك طبقة مجانية شهرية محدودة، وبعدها تكلفة بسيطة لكل دقيقة صوت.

## الخطوة ٢: نشر الخدمة على Render (الأسهل)
1. ادخل إلى <https://render.com> وسجّل دخولك بحساب GitHub.
2. **New → Blueprint**، واختر مستودع `weblayerco/weblayerco`.
3. سيقرأ Render ملف `render.yaml` تلقائياً وينشئ خدمة باسم `noor`.
4. في إعدادات الخدمة → **Environment**:
   - `AZURE_SPEECH_KEY` = المفتاح من الخطوة ١ (سرّي).
   - `AZURE_SPEECH_REGION` = منطقتك (مثل `westeurope`).
   - `NOOR_ENGINE` = `azure` (مضبوط مسبقاً).
5. انتظر اكتمال البناء. ستحصل على رابط مثل `https://noor-xxxx.onrender.com`.

> الطبقة المجانية في Render تُنيم الخدمة عند الخمول، فقد يتأخّر أول فتح ~دقيقة.

## الخطوة ٣: الاستخدام
- افتح الرابط على الهاتف، واسمح بالميكروفون.
- تحقّق من المحرّك: افتح `<الرابط>/health` ويجب أن يظهر `"engine":"azure"`.
- إن ظهر `"engine":"energy"` فالمفتاح غير مضبوط — راجع الخطوة ٢.

---

## بديل: Azure Container Apps (كل شيء داخل Azure)
```bash
# يتطلب Azure CLI ومسجّل دخول
az containerapp up \
  --name noor --resource-group noor-rg --location westeurope \
  --source ./noor \
  --env-vars NOOR_ENGINE=azure AZURE_SPEECH_REGION=westeurope AZURE_SPEECH_KEY=<KEY> \
  --ingress external --target-port 8000
```

## اختبار محلي بـ Docker (اختياري)
```bash
docker build -f noor/Dockerfile -t noor ./noor
docker run -p 8000:8000 \
  -e NOOR_ENGINE=azure -e AZURE_SPEECH_REGION=westeurope -e AZURE_SPEECH_KEY=<KEY> \
  noor
# ثم افتح http://localhost:8000
```

## بديل سريع بلا ذكاء (واجهة فقط)
لرابط مجاني دائم بلا خادم (تقييم محلي + تأكيد وليّ الأمر فقط) يمكن استخدام
GitHub Pages لاحقاً، لكنه **لا يدعم** التقييم بالذكاء الاصطناعي لأنه ثابت.

## الخصوصية
الصوت يُرسَل إلى Azure للتقييم فقط ولا يُخزَّن لدينا. احصل على موافقة وليّ الأمر،
وفعّل HTTPS (مؤمّن تلقائياً على Render/Azure).
