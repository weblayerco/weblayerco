# تطبيق نور — الجوال (Android / iOS)

نستخدم **Capacitor** لتغليف تطبيق الويب الحالي في تطبيق أصلي. نفس الكود وصياغة الواجهة
والتسجيل والمنهج كلها تعمل في الجوال — يضاف فقط مشروع Android (`android/`) ومشروع
iOS (`ios/`) للحصول على APK / IPA.

## ملف APK جاهز بدون أي تثبيت محلي

عند كل دفعة (push) إلى الفرع، يقوم **GitHub Actions** تلقائياً ببناء **APK تجريبي**
ورفعه كأرشيف يمكنك تنزيله:

1. افتح المستودع على GitHub ← تبويب **Actions**.
2. اختر آخر تشغيل لسير العمل **Android APK** (يجب أن يكون أخضر ✓).
3. اسحب الصفحة لأسفل ← **Artifacts** ← نزّل `noor-debug-apk`.
4. على هاتف Android: فُكّ الضغط، افتح ملف `.apk`، اسمح بتثبيت تطبيقات من مصدر غير معروف عند الطلب.

> APK تجريبي مُوقَّع بمفتاح debug — مناسب للاختبار والاستخدام الشخصي/العائلي.
> لنشره على Google Play تحتاج توقيعاً للإنتاج (سننفّذه لاحقاً عند الحاجة).

## البناء محلياً (لمن يملك Android Studio)

```bash
cd noor
npm install
npm run cap:sync          # يبني الويب ويُحدّث المشروع الأصلي
npm run cap:android       # يفتح Android Studio لتشغيل التطبيق على المحاكي أو الجهاز
# أو لبناء APK مباشرة:
npm run android:build     # ينتج APK في android/app/build/outputs/apk/debug/
```

المتطلبات: Node 22+، Java 21+، Android Studio (يثبّت Android SDK).

## iOS (يحتاج macOS + Xcode)

مشروع iOS لم يُضَف هنا لأن `cap add ios` يتطلّب CocoaPods وXcode (macOS فقط). على جهاز Mac:

```bash
cd noor
npm install
npx cap add ios
# إضافة إذن الميكروفون في ios/App/App/Info.plist:
#   <key>NSMicrophoneUsageDescription</key>
#   <string>نحتاج الميكروفون لتسجيل نطق الحرف وتقييمه.</string>
npm run cap:ios           # يفتح Xcode
```

## أذونات الميكروفون

- **Android**: مُعَلَنة في `android/app/src/main/AndroidManifest.xml`
  (`RECORD_AUDIO`)، وتُطلب من المستخدم في بداية التشغيل عبر `MainActivity.java`.
- **iOS**: أضف `NSMicrophoneUsageDescription` في `Info.plist` كما أعلاه.

## ربط التطبيق بالخادم (للذكاء الاصطناعي)

داخل التطبيق المعبَّأ، يستخدم محرّك التقييم نفس الواجهة. لربطه بخادم Azure
(عند نشره حسب `DEPLOY.md`):

1. عدّل `noor/capacitor.config.ts` وأضف داخل `server`:
   ```ts
   server: { androidScheme: "https" }
   ```
   ويُبنى التطبيق مع `VITE_ASSESS_URL=https://<خادمك>.onrender.com/assess`:
   ```bash
   VITE_ASSESS_URL=https://<خادمك>.onrender.com/assess npm run cap:sync
   ```
2. أعد تشغيل البناء عبر CI أو محلياً.

## ملاحظة عن المتاجر

- **Google Play**: يحتاج توقيع إنتاج (keystore) ورسم تسجيل لمرة واحدة (~25$).
- **Apple App Store**: يحتاج حساب مطوّر Apple (~99$ سنوياً).

نشر المتاجر خارج نطاق هذه الإعدادات الأولية، لكن المشروع جاهز لذلك متى أردت.
