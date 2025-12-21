# Medical Report / تقرير طبي

نظام شامل لإصدار التقارير الطبية الرسمية في نظام ERPNext للرعاية الصحية.

## المميزات / Features

✅ **DocType كامل** - Medical Report مع جميع الحقول المطلوبة
✅ **Auto Calculation** - حساب تلقائي لمدة الإجازة المرضية
✅ **Workflow System** - نظام موافقة كامل (Draft → Waiting for Approval → Approved/Rejected)
✅ **3 قوالب PDF** - قوالب جاهزة للطباعة:
   - General Medical Report (تقرير طبي عام)
   - Sick Leave Report (شهادة إجازة مرضية)
   - Insurance Report (تقرير للتأمين الصحي)
✅ **Integration** - ربط مع Patient و Patient Encounter
✅ **Bilingual Support** - دعم كامل للعربية والإنجليزية

## التثبيت / Installation

### 1. إنشاء DocType
```bash
cd /home/frappe-user/frappe-bench
bench --site [your-site] migrate
```

### 2. إعداد Workflow
```bash
cd /home/frappe-user/frappe-bench
bench --site [your-site] console
```

ثم في الـ console:
```python
from healthcare.healthcare.healthcare.doctype.medical_report.setup_workflow import setup_medical_report_workflow
setup_medical_report_workflow()
```

أو يمكنك تشغيل السكريبت مباشرة:
```bash
cd /home/frappe-user/frappe-bench/apps/healthcare/healthcare/healthcare/doctype/medical_report
python setup_workflow.py
```

### 3. تحديث الـ Print Formats
```bash
bench --site [your-site] migrate
```

## الاستخدام / Usage

### إنشاء تقرير طبي من Patient Profile:
1. افتح Patient Record
2. اضغط على زر "Create" → "Medical Report"
3. املأ البيانات المطلوبة
4. اضغط "Request Approval" لإرسال التقرير للطبيب

### إنشاء تقرير طبي من Patient Encounter:
1. افتح Patient Encounter
2. اضغط على زر "Create" → "Medical Report"
3. سيتم ملء البيانات تلقائياً من Encounter
4. أكمل باقي البيانات واضغط "Request Approval"

### Workflow:
1. **Draft** - الموظف ينشئ التقرير
2. **Request Approval** - يرسل للطبيب للمراجعة
3. **Waiting for Doctor Approval** - الطبيب يراجع
4. **Approved** - الطبيب يوافق → يمكن طباعة PDF
5. **Rejected** - الطبيب يرفض

## الحقول / Fields

### بيانات المريض:
- Patient (Link)
- Patient Name (Auto-filled)
- Gender (Auto-filled)
- Age (Auto-filled)
- File Number (Auto-filled)
- Visit / Encounter (Link)

### تفاصيل الحالة الطبية:
- Diagnosis (Text Editor) - **مطلوب**
- Signs & Symptoms (Text Editor)
- Medical Findings (Text Editor)
- Procedure / Treatment (Text Editor)

### تواريخ الإجازة:
- Sick Leave From (Date)
- Sick Leave To (Date)
- Return to Work Date (Date)
- Duration (Auto-calculated)

### جهة التقرير:
- Report Requested For (Select):
  - Work / جهة العمل
  - Health Insurance / التأمين الصحي
  - Sick Leave / إجازة مرضية
  - Travel / سفر
  - School / University / مدرسة / جامعة
  - Other / أخرى
- Organization Name (Data)

### نص التقرير:
- Report Summary (Text Editor) - **مطلوب**
- Recommendations (Text Editor)

### بيانات الطبيب:
- Doctor (Link) - **مطلوب**
- Doctor Name (Auto-filled)
- License Number (Data)
- Digital Signature (Attach Image)
- Official Stamp (Attach Image)

## قوالب الطباعة / Print Formats

### 1. Medical Report General
- تقرير طبي عام شامل
- مناسب لجميع الأغراض
- يتضمن جميع التفاصيل

### 2. Medical Report Sick Leave
- شهادة إجازة مرضية رسمية
- يركز على مدة الإجازة وتاريخ العودة
- تصميم مميز باللون الأصفر

### 3. Medical Report Insurance
- تقرير خاص بالتأمين الصحي
- يتضمن معلومات إضافية:
  - نوع الإجراء
  - مدة العلاج
  - هل يحتاج متابعة؟
- تصميم باللون الأزرق

## Auto Calculation

يتم حساب مدة الإجازة تلقائياً عند إدخال:
- Sick Leave From
- Sick Leave To

الصيغة: `(To Date - From Date) + 1` يوم

## Permissions

- **Healthcare Administrator**: يمكن إنشاء وتعديل التقارير
- **Physician**: يمكن الموافقة/الرفض والطباعة
- **System Manager**: صلاحيات كاملة

## التطوير / Development

### الملفات الرئيسية:
- `medical_report.json` - تعريف DocType
- `medical_report.py` - منطق العمل
- `medical_report.js` - واجهة المستخدم
- `setup_workflow.py` - إعداد Workflow

### Print Formats:
- `medical_report_general/` - القالب العام
- `medical_report_sick_leave/` - قالب الإجازة المرضية
- `medical_report_insurance/` - قالب التأمين

## الدعم / Support

للمساعدة أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

---

**Edwebi Urology Clinic** - نظام إدارة الرعاية الصحية المتكامل


