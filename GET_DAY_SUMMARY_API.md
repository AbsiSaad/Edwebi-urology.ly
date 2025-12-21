# API: get_day_summary

## 📌 الوصف
API method للحصول على ملخص يوم معين للطبيب، يتضمن:
- عدد المواعيد المحجوزة
- عدد الأوقات المتاحة
- قائمة المواعيد المحجوزة
- قائمة الأوقات المتاحة
- مقارنة بين المحجوز والمتاح

## 🔗 Endpoint
```
GET /api/method/healthcare.api.portal_integration.get_day_summary
```

## 📥 Parameters
- `practitioner` (required): معرف الطبيب (Healthcare Practitioner name/ID)
- `date` (required): التاريخ بصيغة YYYY-MM-DD

## 📤 Response Format

### Success Response
```json
{
  "status": "success",
  "practitioner": "HLC-PRAC-2025-00002",
  "date": "2025-11-22",
  "booked_count": 19,
  "available_count": 1,
  "booked_list": [
    {
      "name": "HLC-APP-2025-00025",
      "appointment_time": "09:15:00",
      "duration": 10,
      "patient": "PAT-00001",
      "status": "Scheduled"
    },
    ...
  ],
  "available_slots": [
    "09:00:00"
  ],
  "comparison": {
    "is_working_day": true,
    "total_slots": 20,
    "booked_slots": 19,
    "available_slots": 1,
    "utilization_percentage": 95.0,
    "has_availability": true,
    "message": "1 slots available"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error message here"
}
```

## 📊 Example Usage

### cURL
```bash
curl "http://your-domain.com/api/method/healthcare.api.portal_integration.get_day_summary?practitioner=HLC-PRAC-2025-00002&date=2025-11-22"
```

### JavaScript/Fetch
```javascript
const response = await fetch(
  `/api/method/healthcare.api.portal_integration.get_day_summary?practitioner=HLC-PRAC-2025-00002&date=2025-11-22`
);
const data = await response.json();
console.log(`Booked: ${data.booked_count}, Available: ${data.available_count}`);
```

### Python
```python
import requests

url = "http://your-domain.com/api/method/healthcare.api.portal_integration.get_day_summary"
params = {
    "practitioner": "HLC-PRAC-2025-00002",
    "date": "2025-11-22"
}
response = requests.get(url, params=params)
data = response.json()
print(f"Booked: {data['booked_count']}, Available: {data['available_count']}")
```

## 🔄 n8n Workflow Example

### Node 1: HTTP Request
- Method: GET
- URL: `http://your-domain.com/api/method/healthcare.api.portal_integration.get_day_summary`
- Query Parameters:
  - `practitioner`: `{{ $json.practitioner }}`
  - `date`: `{{ $json.date }}`

### Node 2: IF Condition
- Condition: `{{ $json.comparison.has_availability }}`
- True: Send notification "Available slots exist"
- False: Send notification "No slots available"

### Node 3: Display Data
- Booked Count: `{{ $json.booked_count }}`
- Available Count: `{{ $json.available_count }}`
- Utilization: `{{ $json.comparison.utilization_percentage }}%`

## 📋 Response Fields Explanation

### Main Fields
- `practitioner`: معرف الطبيب
- `date`: التاريخ المطلوب
- `booked_count`: عدد المواعيد المحجوزة
- `available_count`: عدد الأوقات المتاحة
- `booked_list`: قائمة المواعيد المحجوزة مع التفاصيل
- `available_slots`: قائمة الأوقات المتاحة (HH:MM:SS format)

### Comparison Object
- `is_working_day`: هل هذا اليوم يوم عمل للطبيب؟
- `total_slots`: إجمالي عدد الأوقات المتاحة في الجدول
- `booked_slots`: عدد الأوقات المحجوزة
- `available_slots`: عدد الأوقات المتاحة
- `utilization_percentage`: نسبة الاستخدام (المحجوز / الإجمالي × 100)
- `has_availability`: هل يوجد أوقات متاحة؟
- `message`: رسالة توضيحية

## ⚠️ Important Notes

1. **إعادة تشغيل الخادم**: بعد إضافة API method جديد، يجب إعادة تشغيل Frappe bench:
   ```bash
   bench restart
   ```

2. **Guest Access**: API method مسموح للضيوف (`allow_guest=True`)

3. **Date Format**: يجب أن يكون التاريخ بصيغة `YYYY-MM-DD`

4. **Time Format**: الأوقات تُرجع بصيغة `HH:MM:SS`

## 🧪 Test Results

تم اختبار API بنجاح:
- Practitioner: `HLC-PRAC-2025-00002`
- Date: `2025-11-22`
- Result: `19 booked, 1 available` ✓

