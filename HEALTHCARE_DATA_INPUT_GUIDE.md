# دليل إدخال البيانات الثابتة لنظام Healthcare
# Healthcare Master Data Input Guide

## 📋 نظرة عامة

هذا الدليل يوضح كيفية إدخال البيانات الثابتة المطلوبة لنظام Healthcare باستخدام ملف Excel.

---

## 📁 الملفات المرفقة

1. **healthcare_master_data_template.csv** - ملف Excel يحتوي على جميع المدخلات المطلوبة

---

## 📝 تعليمات الإدخال

### 1. Medical Department (القسم الطبي) ⭐⭐⭐⭐⭐

**مطلوب:** نعم  
**الحقول الإلزامية:**
- Department Name (اسم القسم)

**الحقول الاختيارية:**
- Patient Care Type (نوع رعاية المريض): Outpatient, Inpatient, Emergency

**مثال:**
| Department Name | Patient Care Type |
|----------------|-------------------|
| Cardiology | Outpatient |
| Orthopedics | Outpatient |
| Pediatrics | Outpatient |

---

### 2. Healthcare Practitioner (مقدم الرعاية الصحية) ⭐⭐⭐⭐⭐

**مطلوب:** نعم  
**الحقول الإلزامية:**
- Practitioner Name (اسم الممارس)
- Practitioner Type (نوع الممارس): Internal أو External
- Medical Department (القسم الطبي)

**الحقول الاختيارية:**
- Designation (المنصب)
- Mobile No (رقم الجوال)
- Email ID (البريد الإلكتروني)
- OP Consulting Charge (رسوم الاستشارة الخارجية)
- Inpatient Visit Charge (رسوم زيارة المريض الداخلي)

**مثال:**
| Practitioner Name | Practitioner Type | Medical Department | Designation | Mobile No | Email ID |
|------------------|-------------------|-------------------|-------------|-----------|----------|
| Dr. Ahmed Ali | Internal | Cardiology | Consultant | 0123456789 | ahmed@hospital.com |

---

### 3. Appointment Type (نوع الموعد) ⭐⭐⭐⭐⭐

**مطلوب:** نعم  
**الحقول الإلزامية:**
- Appointment Type (نوع الموعد)
- Default Duration (المدة الافتراضية بالدقائق)
- Allow Booking For (السماح بالحجز لـ): Practitioner, Department, أو Service Unit

**الحقول الاختيارية:**
- Color (اللون): كود hex مثل #4285F4
- Price List (قائمة الأسعار)

**مثال:**
| Appointment Type | Default Duration | Allow Booking For | Color |
|-----------------|------------------|-------------------|-------|
| General Consultation | 30 | Practitioner | #4285F4 |
| Follow-up | 15 | Practitioner | #34A853 |

---

### 4. Healthcare Service Unit Type (نوع وحدة خدمة الرعاية الصحية) ⭐⭐⭐⭐

**مطلوب:** مهم  
**الحقول الإلزامية:**
- Service Unit Type (نوع وحدة الخدمة)

**الحقول الاختيارية:**
- Allow Appointments (السماح بالمواعيد): Yes/No
- Overlap Appointments (السماح بتداخل المواعيد): Yes/No
- Service Unit Capacity (سعة وحدة الخدمة)
- Is Billable (قابل للفوترة): Yes/No
- Item Code (رمز العنصر)
- Rate (المعدل)

**مثال:**
| Service Unit Type | Allow Appointments | Overlap Appointments | Capacity |
|------------------|-------------------|---------------------|----------|
| OPD Room | Yes | No | 1 |
| Ward | No | No | 10 |

---

### 5. Healthcare Service Unit (وحدة خدمة الرعاية الصحية) ⭐⭐⭐⭐

**مطلوب:** مهم  
**الحقول الإلزامية:**
- Service Unit (وحدة الخدمة)
- Service Unit Type (نوع وحدة الخدمة)
- Company (الشركة)

**الحقول الاختيارية:**
- Is Group (مجموعة): Yes/No
- Allow Appointments (السماح بالمواعيد): Yes/No
- Overlap Appointments (السماح بتداخل المواعيد): Yes/No
- Warehouse (المستودع)
- Parent Service Unit (وحدة الخدمة الرئيسية)

**مثال:**
| Service Unit | Service Unit Type | Company | Allow Appointments |
|-------------|------------------|---------|-------------------|
| OPD Room 1 | OPD Room | Your Company | Yes |
| Ward A | Ward | Your Company | No |

---

### 6. Practitioner Schedule (جدول الممارس) ⭐⭐⭐⭐

**مطلوب:** مهم  
**الحقول الإلزامية:**
- Schedule Name (اسم الجدول)
- Practitioner (الممارس)
- Day (اليوم): Sunday, Monday, Tuesday, etc.
- From Time (من الوقت): HH:MM:SS
- To Time (إلى الوقت): HH:MM:SS

**الحقول الاختيارية:**
- Allow Video Conferencing (السماح بمؤتمر الفيديو): Yes/No

**مثال:**
| Schedule Name | Practitioner | Day | From Time | To Time | Allow Video Conferencing |
|--------------|--------------|-----|-----------|---------|-------------------------|
| Dr. Ahmed - Weekdays | Dr. Ahmed Ali | Sunday | 09:00:00 | 17:00:00 | Yes |

---

### 7. Lab Test Template (قالب الفحص المخبري) ⭐⭐⭐⭐

**مطلوب:** إذا كان هناك مختبر  
**الحقول الإلزامية:**
- Lab Test Name (اسم الفحص المخبري)
- Department (القسم)
- Sample (العينة)

**الحقول الاختيارية:**
- Lab Test Group (مجموعة الفحص المخبري)
- Sample UOM (وحدة قياس العينة)
- Test Type (نوع الاختبار): Single, Compound, Descriptive, Grouped
- Is Billable (قابل للفوترة): Yes/No
- Item Code (رمز العنصر)

**مثال:**
| Lab Test Name | Department | Sample | Sample UOM | Test Type |
|--------------|------------|--------|------------|-----------|
| Complete Blood Count (CBC) | Pathology | Blood | mL | Single |
| Blood Glucose | Pathology | Blood | mL | Single |

---

### 8. Medication (الدواء) ⭐⭐⭐⭐

**مطلوب:** إذا كانت هناك وصفات  
**الحقول الإلزامية:**
- Generic Name (الاسم العام)
- Medication Class (فئة الدواء)
- Strength (القوة)
- Strength UOM (وحدة قياس القوة)
- Dosage Form (شكل الجرعة)

**الحقول الاختيارية:**
- Is Combination (مزيج): Yes/No
- Item Code (رمز العنصر)
- Default Prescription Dosage (جرعة الوصفة الافتراضية)

**مثال:**
| Generic Name | Medication Class | Strength | Strength UOM | Dosage Form |
|-------------|------------------|----------|--------------|-------------|
| Paracetamol | Analgesics | 500 | mg | Tablet |
| Amoxicillin | Antibiotics | 500 | mg | Capsule |

---

### 9. Clinical Procedure Template (قالب الإجراء السريري) ⭐⭐⭐⭐

**مطلوب:** إذا كانت هناك إجراءات  
**الحقول الإلزامية:**
- Procedure Template (قالب الإجراء)
- Medical Department (القسم الطبي)

**الحقول الاختيارية:**
- Item Code (رمز العنصر)
- Is Billable (قابل للفوترة): Yes/No
- Consume Stock (استهلاك المخزون): Yes/No
- Warehouse (المستودع)
- Estimated Duration (المدة المقدرة بالدقائق)
- Description (الوصف)

**مثال:**
| Procedure Template | Medical Department | Item Code | Estimated Duration |
|-------------------|-------------------|-----------|-------------------|
| X-Ray Chest | Radiology | XRAY-CHEST | 15 |
| ECG | Cardiology | ECG-001 | 10 |

---

### 10. Therapy Type (نوع العلاج) ⭐⭐⭐

**مطلوب:** إذا كان هناك علاج طبيعي  
**الحقول الإلزامية:**
- Therapy Type (نوع العلاج)
- Medical Department (القسم الطبي)

**الحقول الاختيارية:**
- Is Billable (قابل للفوترة): Yes/No
- Rate (المعدل)
- Default Duration (المدة الافتراضية بالدقائق)
- Item Code (رمز العنصر)
- Healthcare Service Unit (وحدة خدمة الرعاية الصحية)

**مثال:**
| Therapy Type | Medical Department | Rate | Default Duration |
|-------------|-------------------|------|------------------|
| Physiotherapy | Orthopedics | 200 | 60 |
| Occupational Therapy | Orthopedics | 150 | 45 |

---

### 11. Diagnosis (التشخيص) ⭐⭐⭐⭐

**مطلوب:** مهم  
**الحقول الإلزامية:**
- Diagnosis (التشخيص)

**الحقول الاختيارية:**
- Medical Coding (الترميز الطبي)

**مثال:**
| Diagnosis |
|-----------|
| Hypertension |
| Diabetes Mellitus Type 2 |
| Upper Respiratory Tract Infection |

---

### 12. Complaint (الشكوى) ⭐⭐⭐

**مطلوب:** اختياري  
**الحقول الإلزامية:**
- Complaint (الشكوى)

**مثال:**
| Complaint |
|-----------|
| Fever |
| Headache |
| Cough |
| Chest Pain |

---

## ✅ قائمة التحقق

قبل إرسال الملف، تأكد من:

- [ ] تم إدخال جميع الحقول الإلزامية (⭐)
- [ ] الأسماء مكتوبة بشكل صحيح وبدون أخطاء إملائية
- [ ] الأرقام في الحقول الرقمية صحيحة
- [ ] الأوقات بصيغة HH:MM:SS
- [ ] الألوان بصيغة hex (#4285F4)
- [ ] تم التحقق من صحة البيانات

---

## 📤 بعد إدخال البيانات

1. احفظ الملف بصيغة CSV
2. أرسل الملف إلى فريق IT
3. سيتم استيراد البيانات تلقائياً إلى النظام

---

## ⚠️ ملاحظات مهمة

1. **لا تحذف الصف الأول** (رؤوس الأعمدة)
2. **لا تترك الحقول الإلزامية فارغة**
3. **استخدم نفس الأسماء** المذكورة في النظام (مثل: Outpatient, Internal, etc.)
4. **للأوقات:** استخدم الصيغة 24 ساعة (09:00:00 وليس 9:00 AM)
5. **للألوان:** استخدم كود hex (مثل #4285F4)

---

## 📞 للاستفسارات

إذا كان لديك أي استفسارات، يرجى التواصل مع فريق IT.

---

**آخر تحديث:** نوفمبر 2025

