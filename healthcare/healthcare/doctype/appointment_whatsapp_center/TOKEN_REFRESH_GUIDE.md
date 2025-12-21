# دليل تحديث رمز الوصول في WhatsApp

## المشكلة
إذا ظهرت رسالة خطأ تقول "انتهت صلاحية رمز الوصول" (Access token expired)، فأنت بحاجة إلى تحديث الرمز.

## الحل السريع

### الخطوة 1: الحصول على رمز جديد
1. اذهب إلى [Meta for Developers](https://developers.facebook.com/apps)
2. اختر التطبيق الخاص بك
3. اذهب إلى **WhatsApp > API Setup**
4. انسخ **Temporary access token** أو أنشئ **Permanent token**

### الخطوة 2: تحديث الرمز في Frappe
1. في Frappe، اذهب إلى **WhatsApp Settings**
2. الصق الرمز الجديد في حقل **Token**
3. تأكد من تفعيل **Enabled**
4. احفظ

### الخطوة 3: إنشاء رمز دائم (اختياري)
للحصول على رمز دائم لا ينتهي:

1. في Meta for Developers، اذهب إلى **Tools > Graph API Explorer**
2. اختر التطبيق الخاص بك
3. اختر الصلاحيات المطلوبة:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
4. انقر على **Generate Access Token**
5. انسخ الرمز وضعه في Frappe

## ملاحظات مهمة
- الرموز المؤقتة تنتهي صلاحيتها بعد 24 ساعة
- الرموز الدائمة لا تنتهي صلاحيتها إلا إذا قمت بإلغائها
- احتفظ بالرمز في مكان آمن

## التحقق من صحة الرمز
بعد تحديث الرمز، يمكنك التحقق من صحته من خلال:
1. محاولة إرسال رسالة تجريبية من **Appointment WhatsApp Center**
2. أو من **WhatsApp Message** doctype

