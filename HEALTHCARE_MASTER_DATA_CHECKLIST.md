# قائمة المدخلات الثابتة المطلوبة في نظام Healthcare
# Healthcare Master Data Checklist

هذه قائمة شاملة بجميع المدخلات الثابتة (Masters/Setup) التي يجب إعدادها قبل البدء في استخدام نظام Healthcare.

---

## 📋 جدول المحتويات

1. [الإعدادات الأساسية](#الإعدادات-الأساسية)
2. [إدارة المرضى](#إدارة-المرضى)
3. [إدارة الممارسين](#إدارة-الممارسين)
4. [المواعيد](#المواعيد)
5. [المختبر](#المختبر)
6. [الإجراءات السريرية](#الإجراءات-السريرية)
7. [الأدوية والوصفات](#الأدوية-والوصفات)
8. [العلاج وإعادة التأهيل](#العلاج-وإعادة-التأهيل)
9. [المريض الداخلي](#المريض-الداخلي)
10. [التمريض](#التمريض)
11. [التشخيص والترميز](#التشخيص-والترميز)
12. [الخدمات والوحدات](#الخدمات-والوحدات)

---

## 🔧 الإعدادات الأساسية

### 1. Healthcare Settings (إعدادات الرعاية الصحية)
**الموقع:** Healthcare > Settings > Healthcare Settings  
**الأولوية:** ⭐⭐⭐⭐⭐ (إلزامي)  
**الوصف:** الإعدادات العامة للنظام

**الحقول المطلوبة:**
- Patient Name By (طريقة تسمية المريض)
- Link Customer to Patient (ربط العميل بالمريض)
- Collect Registration Fee (تحصيل رسوم التسجيل)
- Registration Fee (رسوم التسجيل)
- Default Intent (النية الافتراضية)
- Default Priority (الأولوية الافتراضية)
- Income Account (حساب الإيرادات)
- Receivable Account (حساب الذمم المدينة)
- OP Consulting Charge Item (عنصر رسوم الاستشارة الخارجية)
- Inpatient Visit Charge Item (عنصر رسوم زيارة المريض الداخلي)

---

## 👥 إدارة المرضى

### 2. Patient Care Type (نوع رعاية المريض)
**الموقع:** Healthcare > Masters > Patient Care Type  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** أنواع رعاية المرضى (Outpatient, Inpatient, Emergency, etc.)

**مثال:**
- Outpatient (مريض خارجي)
- Inpatient (مريض داخلي)
- Emergency (طوارئ)
- Day Care (رعاية يومية)

### 3. Patient Relation (علاقة المريض)
**الموقع:** Healthcare > Masters > Patient Relation  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** علاقات المرضى (Father, Mother, Spouse, etc.)

**مثال:**
- Father (أب)
- Mother (أم)
- Spouse (زوج/زوجة)
- Son (ابن)
- Daughter (ابنة)

---

## 👨‍⚕️ إدارة الممارسين

### 4. Healthcare Practitioner (مقدم الرعاية الصحية)
**الموقع:** Healthcare > Masters > Healthcare Practitioner  
**الأولوية:** ⭐⭐⭐⭐⭐ (إلزامي)  
**الوصف:** بيانات الأطباء والممارسين الصحيين

**الحقول المطلوبة:**
- Practitioner Name (اسم الممارس)
- Practitioner Type (نوع الممارس: Internal/External)
- Medical Department (القسم الطبي)
- Designation (المنصب)
- Mobile No (رقم الجوال)
- Email ID (البريد الإلكتروني)
- OP Consulting Charge (رسوم الاستشارة الخارجية)
- Inpatient Visit Charge (رسوم زيارة المريض الداخلي)

### 5. Medical Department (القسم الطبي)
**الموقع:** Healthcare > Masters > Medical Department  
**الأولوية:** ⭐⭐⭐⭐⭐ (إلزامي)  
**الوصف:** الأقسام الطبية في المستشفى

**مثال:**
- Cardiology (أمراض القلب)
- Orthopedics (العظام)
- Pediatrics (طب الأطفال)
- General Medicine (الطب العام)
- Surgery (الجراحة)

### 6. Practitioner Schedule (جدول الممارس)
**الموقع:** Healthcare > Masters > Practitioner Schedule  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** جداول عمل الممارسين

**الحقول المطلوبة:**
- Schedule Name (اسم الجدول)
- Time Slots (الأوقات)
- Allow Video Conferencing (السماح بمؤتمر الفيديو)

---

## 📅 المواعيد

### 7. Appointment Type (نوع الموعد)
**الموقع:** Healthcare > Masters > Appointment Type  
**الأولوية:** ⭐⭐⭐⭐⭐ (إلزامي)  
**الوصف:** أنواع المواعيد (Consultation, Follow-up, etc.)

**الحقول المطلوبة:**
- Appointment Type (نوع الموعد)
- Default Duration (المدة الافتراضية بالدقائق)
- Allow Booking For (السماح بالحجز لـ: Practitioner/Department/Service Unit)
- Color (اللون)
- Price List (قائمة الأسعار)
- Appointment Type Service Items (عناصر خدمة نوع الموعد)

**مثال:**
- General Consultation (استشارة عامة) - 30 دقيقة
- Follow-up (متابعة) - 15 دقيقة
- Emergency (طوارئ) - 60 دقيقة

### 8. Healthcare Service Unit Type (نوع وحدة خدمة الرعاية الصحية)
**الموقع:** Healthcare > Masters > Healthcare Service Unit Type  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** أنواع وحدات الخدمة (OPD, IPD, Emergency, etc.)

**الحقول المطلوبة:**
- Service Unit Type (نوع وحدة الخدمة)
- Allow Appointments (السماح بالمواعيد)
- Overlap Appointments (السماح بتداخل المواعيد)
- Service Unit Capacity (سعة وحدة الخدمة)

### 9. Healthcare Service Unit (وحدة خدمة الرعاية الصحية)
**الموقع:** Healthcare > Masters > Healthcare Service Unit  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** وحدات الخدمة الفعلية (OPD Room 1, Ward A, etc.)

**الحقول المطلوبة:**
- Service Unit (وحدة الخدمة)
- Service Unit Type (نوع وحدة الخدمة)
- Company (الشركة)
- Warehouse (المستودع) - إذا كان هناك استهلاك مخزون
- Allow Appointments (السماح بالمواعيد)
- Overlap Appointments (السماح بتداخل المواعيد)

---

## 🧪 المختبر

### 10. Lab Test Template (قالب الفحص المخبري)
**الموقع:** Healthcare > Masters > Lab Test Template  
**الأولوية:** ⭐⭐⭐⭐⭐ (إلزامي للمختبر)  
**الوصف:** قوالب الفحوصات المخبرية

**الحقول المطلوبة:**
- Lab Test Name (اسم الفحص المخبري)
- Lab Test Group (مجموعة الفحص المخبري)
- Department (القسم)
- Sample (العينة)
- Sample UOM (وحدة قياس العينة)
- Normal Test Items (عناصر الاختبار العادي)
- Descriptive Test Items (عناصر الاختبار الوصفي)
- Organism Test Items (عناصر اختبار الكائن الحي)
- Sensitivity Test Items (عناصر اختبار الحساسية)

**أنواع القوالب:**
- Single (مفرد)
- Compound (مركب)
- Descriptive (وصفي)
- Grouped (مجموعة)
- No Result (بدون نتيجة)

### 11. Lab Test Group Template (قالب مجموعة الفحص المخبري)
**الموقع:** Healthcare > Masters > Lab Test Group Template  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** مجموعات الفحوصات المخبرية

### 12. Lab Test UOM (وحدة قياس الفحص المخبري)
**الموقع:** Healthcare > Masters > Lab Test UOM  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** وحدات القياس للفحوصات المخبرية

**مثال:**
- mg/dL
- mmol/L
- g/L
- %

### 13. Lab Test Sample (عينة الفحص المخبري)
**الموقع:** Healthcare > Masters > Lab Test Sample  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** أنواع العينات

**مثال:**
- Blood (دم)
- Urine (بول)
- Stool (براز)
- Sputum (بلغم)

### 14. Sample Type (نوع العينة)
**الموقع:** Healthcare > Masters > Sample Type  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** أنواع العينات للجمع

### 15. Normal Test Template (قالب الاختبار العادي)
**الموقع:** Healthcare > Masters > Normal Test Template  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** قوالب الاختبارات العادية

### 16. Descriptive Test Template (قالب الاختبار الوصفي)
**الموقع:** Healthcare > Masters > Descriptive Test Template  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** قوالب الاختبارات الوصفية

### 17. Antibiotic (المضاد الحيوي)
**الموقع:** Healthcare > Masters > Antibiotic  
**الأولوية:** ⭐⭐⭐ (لاختبارات الحساسية)  
**الوصف:** المضادات الحيوية لاختبارات الحساسية

**مثال:**
- Amoxicillin
- Ciprofloxacin
- Azithromycin

### 18. Sensitivity (الحساسية)
**الموقع:** Healthcare > Masters > Sensitivity  
**الأولوية:** ⭐⭐⭐ (لاختبارات الحساسية)  
**الوصف:** مستويات الحساسية

**مثال:**
- Sensitive (حساس)
- Resistant (مقاوم)
- Intermediate (متوسط)

---

## 🏥 الإجراءات السريرية

### 19. Clinical Procedure Template (قالب الإجراء السريري)
**الموقع:** Healthcare > Masters > Clinical Procedure Template  
**الأولوية:** ⭐⭐⭐⭐ (مهم للإجراءات)  
**الوصف:** قوالب الإجراءات السريرية

**الحقول المطلوبة:**
- Procedure Template (قالب الإجراء)
- Item Code (رمز العنصر)
- Medical Department (القسم الطبي)
- Consume Stock (استهلاك المخزون)
- Warehouse (المستودع)
- Items (العناصر الاستهلاكية)
- Estimated Duration (المدة المقدرة)

**مثال:**
- X-Ray Chest (أشعة الصدر)
- ECG (تخطيط القلب)
- Ultrasound (الموجات فوق الصوتية)

---

## 💊 الأدوية والوصفات

### 20. Medication (الدواء)
**الموقع:** Healthcare > Masters > Medication  
**الأولوية:** ⭐⭐⭐⭐⭐ (إلزامي للوصفات)  
**الوصف:** قاعدة بيانات الأدوية

**الحقول المطلوبة:**
- Generic Name (الاسم العام)
- Medication Class (فئة الدواء)
- Strength (القوة)
- Strength UOM (وحدة قياس القوة)
- Dosage Form (شكل الجرعة)
- Default Prescription Dosage (جرعة الوصفة الافتراضية)
- Default Prescription Duration (مدة الوصفة الافتراضية)
- Item Code (رمز العنصر)

### 21. Medication Class (فئة الدواء)
**الموقع:** Healthcare > Masters > Medication Class  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** فئات الأدوية

**مثال:**
- Antibiotics (مضادات حيوية)
- Analgesics (مسكنات)
- Antihypertensives (خافضات ضغط)
- Antidiabetics (أدوية السكري)

### 22. Dosage Form (شكل الجرعة)
**الموقع:** Healthcare > Masters > Dosage Form  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** أشكال الجرعات

**مثال:**
- Tablet (أقراص)
- Capsule (كبسولات)
- Syrup (شراب)
- Injection (حقن)
- Ointment (مرهم)

### 23. Prescription Dosage (وصفة الجرعة)
**الموقع:** Healthcare > Masters > Prescription Dosage  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** جرعات الوصفات

**مثال:**
- 1-0-1 (مرة صباحاً ومساءً)
- 0-0-1 (مرة مساءً)
- 1-1-1 (ثلاث مرات يومياً)
- SOS (عند الحاجة)

### 24. Prescription Duration (مدة الوصفة الطبية)
**الموقع:** Healthcare > Masters > Prescription Duration  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** مدة الوصفات

**مثال:**
- 3 Days (3 أيام)
- 5 Days (5 أيام)
- 1 Week (أسبوع واحد)
- 2 Weeks (أسبوعان)
- 1 Month (شهر واحد)

### 25. Dosage Strength (قوة الجرعة)
**الموقع:** Healthcare > Masters > Dosage Strength  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** قوى الجرعات

---

## 🏋️ العلاج وإعادة التأهيل

### 26. Therapy Type (نوع العلاج)
**الموقع:** Healthcare > Masters > Therapy Type  
**الأولوية:** ⭐⭐⭐ (للعلاج الطبيعي)  
**الوصف:** أنواع العلاج الطبيعي

**الحقول المطلوبة:**
- Therapy Type (نوع العلاج)
- Is Billable (قابل للفوترة)
- Rate (المعدل)
- Default Duration (المدة الافتراضية بالدقائق)
- Exercises (التمارين)
- Medical Department (القسم الطبي)
- Healthcare Service Unit (وحدة خدمة الرعاية الصحية)

**مثال:**
- Physiotherapy (العلاج الطبيعي)
- Occupational Therapy (العلاج الوظيفي)
- Speech Therapy (علاج النطق)

### 27. Therapy Plan Template (قالب خطة العلاج)
**الموقع:** Healthcare > Masters > Therapy Plan Template  
**الأولوية:** ⭐⭐⭐ (للعلاج الطبيعي)  
**الوصف:** قوالب خطط العلاج

**الحقول المطلوبة:**
- Plan Name (اسم الخطة)
- Therapy Types (أنواع العلاج)
- Total Sessions (إجمالي الجلسات)
- Rate (المعدل)
- Amount (المبلغ)

### 28. Exercise Type (نوع التمرين)
**الموقع:** Healthcare > Masters > Exercise Type  
**الأولوية:** ⭐⭐⭐ (للعلاج الطبيعي)  
**الوصف:** أنواع التمارين

### 29. Exercise (التمرين)
**الموقع:** Healthcare > Masters > Exercise  
**الأولوية:** ⭐⭐⭐ (للعلاج الطبيعي)  
**الوصف:** التمارين الفردية

### 30. Exercise Difficulty Level (مستوى صعوبة التمرين)
**الموقع:** Healthcare > Masters > Exercise Difficulty Level  
**الأولوية:** ⭐⭐ (اختياري)  
**الوصف:** مستويات صعوبة التمارين

### 31. Treatment Plan Template (قالب خطة العلاج)
**الموقع:** Healthcare > Masters > Treatment Plan Template  
**الأولوية:** ⭐⭐⭐ (للخطط العلاجية)  
**الوصف:** قوالب خطط العلاج الشاملة

**الحقول المطلوبة:**
- Template Name (اسم القالب)
- Medical Department (القسم الطبي)
- Description (الوصف)
- Goal (الهدف)
- Practitioners (الممارسون)
- Plan Conditions (شروط الخطة)
- Items (العناصر: Medications, Lab Tests, Procedures)
- Medications (الأدوية)

### 32. Patient Assessment Template (نموذج تقييم المريض)
**الموقع:** Healthcare > Masters > Patient Assessment Template  
**الأولوية:** ⭐⭐⭐ (للتقييمات)  
**الوصف:** قوالب تقييم المرضى

---

## 🏥 المريض الداخلي

### 33. Healthcare Service Unit Type (للمريض الداخلي)
**الموقع:** Healthcare > Masters > Healthcare Service Unit Type  
**الأولوية:** ⭐⭐⭐ (للمريض الداخلي)  
**الوصف:** أنواع وحدات الخدمة للمرضى الداخليين

**مثال:**
- Ward (جناح)
- ICU (العناية المركزة)
- Operation Theater (غرفة العمليات)

---

## 👩‍⚕️ التمريض

### 34. Nursing Checklist Template (قالب قائمة التمريض)
**الموقع:** Healthcare > Masters > Nursing Checklist Template  
**الأولوية:** ⭐⭐⭐ (للتمريض)  
**الوصف:** قوالب قوائم التمريض

**الحقول المطلوبة:**
- Checklist Template (قالب القائمة)
- Tasks (المهام)

### 35. Healthcare Activity (نشاط الرعاية الصحية)
**الموقع:** Healthcare > Masters > Healthcare Activity  
**الأولوية:** ⭐⭐⭐ (للتمريض)  
**الوصف:** أنشطة الرعاية الصحية

---

## 🔬 التشخيص والترميز

### 36. Diagnosis (التشخيص)
**الموقع:** Healthcare > Masters > Diagnosis  
**الأولوية:** ⭐⭐⭐⭐ (مهم)  
**الوصف:** قاعدة بيانات التشخيصات

**الحقول المطلوبة:**
- Diagnosis (التشخيص)
- Medical Coding (الترميز الطبي)

### 37. Complaint (الشكوى)
**الموقع:** Healthcare > Masters > Complaint  
**الأولوية:** ⭐⭐⭐ (اختياري)  
**الوصف:** الشكاوى الشائعة

**مثال:**
- Fever (حمى)
- Headache (صداع)
- Cough (سعال)
- Pain (ألم)

### 38. Code System (نظام الرمز)
**الموقع:** Healthcare > Masters > Code System  
**الأولوية:** ⭐⭐⭐ (للترميز الطبي)  
**الوصف:** أنظمة الترميز الطبي

**مثال:**
- ICD-10 (التصنيف الدولي للأمراض)
- SNOMED CT
- LOINC

### 39. Code Value (قيمة الرمز)
**الموقع:** Healthcare > Masters > Code Value  
**الأولوية:** ⭐⭐⭐ (للترميز الطبي)  
**الوصف:** قيم الرموز الطبية

### 40. Code Value Set (مجموعة قيم الرمز)
**الموقع:** Healthcare > Masters > Code Value Set  
**الأولوية:** ⭐⭐ (اختياري)  
**الوصف:** مجموعات قيم الرموز

---

## 📋 الخدمات والوحدات

### 41. Service Request Category (فئة طلب الخدمة)
**الموقع:** Healthcare > Masters > Service Request Category  
**الأولوية:** ⭐⭐⭐ (لطلبات الخدمة)  
**الوصف:** فئات طلبات الخدمة

### 42. Service Request Reason (سبب طلب الخدمة)
**الموقع:** Healthcare > Masters > Service Request Reason  
**الأولوية:** ⭐⭐⭐ (لطلبات الخدمة)  
**الوصف:** أسباب طلبات الخدمة

### 43. Body Part (جزء الجسم)
**الموقع:** Healthcare > Masters > Body Part  
**الأولوية:** ⭐⭐ (اختياري)  
**الوصف:** أجزاء الجسم

**مثال:**
- Head (رأس)
- Chest (صدر)
- Abdomen (بطن)
- Leg (ساق)

---

## 📝 إعدادات إضافية

### 44. Patient History Settings (إعدادات تاريخ المريض)
**الموقع:** Healthcare > Settings > Patient History Settings  
**الأولوية:** ⭐⭐⭐ (مهم)  
**الوصف:** إعدادات عرض تاريخ المريض

### 45. Patient History Standard Document Type (نوع المستند القياسي لتاريخ المريض)
**الموقع:** Healthcare > Settings > Patient History Standard Document Type  
**الأولوية:** ⭐⭐ (اختياري)  
**الوصف:** أنواع المستندات القياسية في تاريخ المريض

### 46. Patient History Custom Document Type (نوع المستند المخصص لتاريخ المريض)
**الموقع:** Healthcare > Settings > Patient History Custom Document Type  
**الأولوية:** ⭐⭐ (اختياري)  
**الوصف:** أنواع المستندات المخصصة في تاريخ المريض

### 47. Clinical Note Type (نوع الملاحظة السريرية)
**الموقع:** Healthcare > Masters > Clinical Note Type  
**الأولوية:** ⭐⭐ (اختياري)  
**الوصف:** أنواع الملاحظات السريرية

### 48. Fee Validity (صلاحية الرسوم)
**الموقع:** Healthcare > Masters > Fee Validity  
**الأولوية:** ⭐⭐⭐ (للمواعيد المجانية)  
**الوصف:** صلاحيات الرسوم للمواعيد المجانية

---

## ✅ قائمة التحقق السريعة (Quick Checklist)

### إلزامي (⭐⭐⭐⭐⭐):
- [ ] Healthcare Settings
- [ ] Healthcare Practitioner
- [ ] Medical Department
- [ ] Appointment Type
- [ ] Healthcare Service Unit Type
- [ ] Healthcare Service Unit

### مهم جداً (⭐⭐⭐⭐):
- [ ] Practitioner Schedule
- [ ] Lab Test Template (إذا كان هناك مختبر)
- [ ] Clinical Procedure Template (إذا كانت هناك إجراءات)
- [ ] Medication (إذا كانت هناك وصفات)
- [ ] Medication Class
- [ ] Dosage Form
- [ ] Prescription Dosage
- [ ] Prescription Duration
- [ ] Diagnosis

### مهم (⭐⭐⭐):
- [ ] Patient Care Type
- [ ] Lab Test Group Template
- [ ] Sample Type
- [ ] Therapy Type (إذا كان هناك علاج طبيعي)
- [ ] Therapy Plan Template
- [ ] Treatment Plan Template
- [ ] Nursing Checklist Template
- [ ] Code System
- [ ] Code Value

### اختياري (⭐⭐):
- [ ] Patient Relation
- [ ] Complaint
- [ ] Body Part
- [ ] Exercise Type
- [ ] Service Request Category
- [ ] Service Request Reason

---

## 📌 ملاحظات مهمة

1. **ترتيب الإعداد:** ابدأ بالإعدادات الأساسية ثم الممارسين ثم المواعيد ثم المختبر والأدوية.

2. **البيانات المطلوبة من ERPNext:**
   - Company (الشركة)
   - Warehouse (المستودع) - إذا كان هناك استهلاك مخزون
   - Item (العنصر) - للأدوية والإجراءات
   - Price List (قائمة الأسعار)
   - Account (الحساب) - للإيرادات والذمم المدينة

3. **الربط مع ERPNext:**
   - يجب ربط Patient مع Customer
   - يجب ربط Medication مع Item
   - يجب ربط Clinical Procedure Template مع Item
   - يجب ربط Lab Test Template مع Item (إذا كان هناك فوترة)

4. **الإعدادات الموصى بها:**
   - قم بإعداد Healthcare Settings أولاً
   - ثم أضف Medical Departments
   - ثم أضف Healthcare Practitioners
   - ثم أضف Appointment Types
   - ثم أضف Service Units

---

## 🔗 روابط مفيدة

- [Healthcare Documentation](https://docs.erpnext.com/docs/user/manual/en/healthcare)
- [Healthcare Setup Guide](https://docs.erpnext.com/docs/user/manual/en/healthcare/setup)

---

**آخر تحديث:** نوفمبر 2025

