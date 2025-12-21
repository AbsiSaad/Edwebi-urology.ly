# نظام التقرير الطبي - Medical Report System

## ✅ تم إنشاء النظام بنجاح!

تم إنشاء نظام شامل لإصدار التقارير الطبية الرسمية داخل نظام ERPNext للرعاية الصحية (Edwebi Urology).

---

## 📋 ما تم إنشاؤه:

### 1️⃣ DocType: Medical Report / تقرير طبي

**الموقع:** `healthcare/healthcare/healthcare/doctype/medical_report/`

**الملفات:**
- ✅ `medical_report.json` - تعريف DocType كامل مع جميع الحقول
- ✅ `medical_report.py` - منطق العمل مع Auto Calculation
- ✅ `medical_report.js` - واجهة المستخدم والأزرار
- ✅ `setup_workflow.py` - سكريبت إعداد Workflow
- ✅ `__init__.py` - ملف Python الأساسي
- ✅ `README.md` - دليل الاستخدام الكامل

**الحقول المضافة:**
- ✅ بيانات المريض (Patient, Name, Gender, Age, File Number)
- ✅ Visit/Encounter (ربط مع Patient Encounter)
- ✅ Diagnosis (التشخيص) - مطلوب
- ✅ Signs & Symptoms (الأعراض)
- ✅ Medical Findings (النتائج الطبية)
- ✅ Procedure/Treatment (الإجراء/العلاج)
- ✅ Sick Leave Dates (تواريخ الإجازة)
- ✅ Duration (المدة) - يُحسب تلقائياً
- ✅ Report Requested For (جهة التقرير)
- ✅ Organization Name (اسم الجهة)
- ✅ Report Summary (ملخص التقرير) - مطلوب
- ✅ Recommendations (التوصيات)
- ✅ Doctor Information (بيانات الطبيب)
- ✅ License Number (رقم مزاولة المهنة)
- ✅ Digital Signature (التوقيع الرقمي)
- ✅ Official Stamp (الختم الرسمي)

---

### 2️⃣ Workflow System / نظام الموافقة

**الحالات (States):**
1. **Draft** - مسودة
2. **Waiting for Doctor Approval** - في انتظار موافقة الطبيب
3. **Approved** - موافق عليه
4. **Rejected** - مرفوض

**الإجراءات (Actions):**
- Request Approval - طلب الموافقة
- Approve - الموافقة
- Reject - الرفض

**الأدوار (Roles):**
- Healthcare Administrator - يمكن إنشاء وطلب الموافقة
- Physician - يمكن الموافقة/الرفض

---

### 3️⃣ قوالب PDF للطباعة (3 قوالب)

#### أ) Medical Report General / تقرير طبي عام
**الموقع:** `healthcare/healthcare/healthcare/print_format/medical_report_general/`

- ✅ تصميم احترافي باللون الأخضر
- ✅ شعار عيادة Edwebi Urology
- ✅ جميع التفاصيل الطبية
- ✅ دعم كامل للعربية والإنجليزية
- ✅ مناسب لجميع الأغراض

#### ب) Medical Report Sick Leave / شهادة إجازة مرضية
**الموقع:** `healthcare/healthcare/healthcare/print_format/medical_report_sick_leave/`

- ✅ تصميم مميز باللون الأصفر
- ✅ يركز على الإجازة المرضية
- ✅ مدة الإجازة وتاريخ العودة
- ✅ مناسب للجهات الرسمية

#### ج) Medical Report Insurance / تقرير للتأمين الصحي
**الموقع:** `healthcare/healthcare/healthcare/print_format/medical_report_insurance/`

- ✅ تصميم باللون الأزرق
- ✅ معلومات إضافية للتأمين:
  - نوع الإجراء
  - مدة العلاج
  - هل يحتاج متابعة؟
- ✅ مناسب لشركات التأمين

---

### 4️⃣ Integration / الربط مع النظام

#### أ) Patient Profile
**الملف المعدل:** `healthcare/healthcare/healthcare/doctype/patient/patient.js`

- ✅ زر "Create Medical Report" في Patient Profile
- ✅ يفتح تقرير جديد مع بيانات المريض المملوءة تلقائياً

#### ب) Patient Encounter
**الملفات المعدلة:**
- `healthcare/healthcare/healthcare/doctype/patient_encounter/patient_encounter.json` - إضافة رابط
- `healthcare/healthcare/healthcare/doctype/patient_encounter/patient_encounter.js` - إضافة زر

- ✅ زر "Create Medical Report" في Patient Encounter
- ✅ رابط في قسم "Medical Records"
- ✅ يملأ البيانات تلقائياً من Encounter:
  - Patient
  - Diagnosis
  - Symptoms
  - Doctor
  - Report Date

---

## 🚀 خطوات التثبيت / Installation Steps

### الخطوة 1: Migrate النظام
```bash
cd /home/frappe-user/frappe-bench
bench --site [your-site-name] migrate
```

### الخطوة 2: إعداد Workflow
```bash
cd /home/frappe-user/frappe-bench
bench --site [your-site-name] console
```

ثم في الـ console:
```python
from healthcare.healthcare.healthcare.doctype.medical_report.setup_workflow import setup_medical_report_workflow
setup_medical_report_workflow()
exit()
```

أو تشغيل السكريبت مباشرة:
```bash
cd /home/frappe-user/frappe-bench
bench --site [your-site-name] console
```

ثم:
```python
exec(open('apps/healthcare/healthcare/healthcare/doctype/medical_report/setup_workflow.py').read())
```

### الخطوة 3: تحديث الـ Cache
```bash
bench --site [your-site-name] clear-cache
bench --site [your-site-name] clear-website-cache
```

---

## 📖 كيفية الاستخدام / How to Use

### طريقة 1: من Patient Profile
1. افتح Patient Record
2. اضغط على زر "Create" → "Medical Report"
3. املأ البيانات المطلوبة
4. اضغط "Request Approval" لإرسال التقرير للطبيب

### طريقة 2: من Patient Encounter
1. افتح Patient Encounter
2. اضغط على زر "Create" → "Medical Report"
3. سيتم ملء البيانات تلقائياً من Encounter
4. أكمل باقي البيانات واضغط "Request Approval"

### Workflow Process:
1. **Draft** → الموظف ينشئ التقرير
2. **Request Approval** → يرسل للطبيب
3. **Waiting for Doctor Approval** → الطبيب يراجع
4. **Approved** → يمكن طباعة PDF
5. **Rejected** → الطبيب يرفض

---

## 🎯 المميزات الرئيسية / Key Features

### ✅ Auto Calculation
- حساب تلقائي لمدة الإجازة المرضية
- الصيغة: `(To Date - From Date) + 1` يوم

### ✅ Auto Fill
- ملء تلقائي لبيانات المريض من Patient
- ملء تلقائي للتشخيص والأعراض من Encounter
- ملء تلقائي لبيانات الطبيب

### ✅ Bilingual Support
- دعم كامل للعربية والإنجليزية
- جميع الحقول والعناوين ثنائية اللغة
- قوالب PDF ثنائية اللغة

### ✅ Print Formats
- 3 قوالب جاهزة للطباعة
- اختيار تلقائي للقالب حسب نوع التقرير
- تصميم احترافي مع شعار العيادة

### ✅ Workflow Integration
- نظام موافقة كامل
- أزرار ديناميكية حسب الحالة
- إشعارات للموافقة

---

## 📁 هيكل الملفات / File Structure

```
healthcare/
├── healthcare/
│   └── healthcare/
│       ├── doctype/
│       │   └── medical_report/
│       │       ├── __init__.py
│       │       ├── medical_report.json
│       │       ├── medical_report.py
│       │       ├── medical_report.js
│       │       ├── setup_workflow.py
│       │       └── README.md
│       └── print_format/
│           ├── medical_report_general/
│           │   └── medical_report_general.json
│           ├── medical_report_sick_leave/
│           │   └── medical_report_sick_leave.json
│           └── medical_report_insurance/
│               └── medical_report_insurance.json
```

---

## 🔧 التخصيص / Customization

### تغيير شعار العيادة:
في قوالب PDF، يمكنك تغيير:
- اسم العيادة (Edwebi Urology Clinic)
- الشعار (Logo)
- الألوان (Colors)

### إضافة حقول جديدة:
1. عدل `medical_report.json`
2. أضف المنطق في `medical_report.py`
3. حدث قوالب PDF

---

## 📝 ملاحظات مهمة / Important Notes

1. **Permissions**: تأكد من إعطاء الصلاحيات المناسبة للأدوار:
   - Healthcare Administrator
   - Physician
   - System Manager

2. **Workflow States**: يجب إنشاء Workflow States قبل استخدام النظام

3. **Print Formats**: تأكد من تحديث الـ cache بعد إضافة قوالب PDF

4. **Company Logo**: يمكن إضافة شعار الشركة في Company Settings

---

## ✅ Checklist للتثبيت

- [ ] تم تشغيل `bench migrate`
- [ ] تم تشغيل `setup_workflow.py`
- [ ] تم تحديث الـ cache
- [ ] تم اختبار إنشاء تقرير من Patient
- [ ] تم اختبار إنشاء تقرير من Encounter
- [ ] تم اختبار Workflow (Draft → Approval → Approved)
- [ ] تم اختبار طباعة PDF بجميع القوالب
- [ ] تم التحقق من Auto Calculation لمدة الإجازة

---

## 🎉 تم بنجاح!

النظام جاهز للاستخدام! يمكنك الآن:
- ✅ إنشاء تقارير طبية رسمية
- ✅ إصدار إجازات مرضية
- ✅ طباعة تقارير للتأمين الصحي
- ✅ إدارة الموافقات عبر Workflow

---

**تم التطوير بواسطة:** Edwebi Urology Clinic
**التاريخ:** 2025-01-27
**الإصدار:** 1.0.0


