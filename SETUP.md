# تشغيل مشروع بصمة+ (Basma+) على جهاز جديد

## المتطلبات الأساسية

- **Python 3.11+** مع pip
- **Node.js 18+** مع npm
- **MySQL 8.0** (مثبّت وشغال)
- **Git**

## 1. تجهيز قاعدة البيانات

```sql
CREATE DATABASE basma_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

تأكد من أن MySQL شغال على `localhost:3306` والمستخدم `root` بدون كلمة سر (أو غيّر الإعدادات في `.env`).

## 2. إعداد الباك إند (Backend)

```bash
# ادخل مجلد backend
cd backend

# إنشاء بيئة Python افتراضية
python -m venv venv

# تفعيلها
# Windows PowerShell:
venv\Scripts\Activate.ps1
# أو Windows CMD:
venv\Scripts\activate.bat
# أو Linux/macOS:
source venv/bin/activate

# تثبيت الحزم
pip install -r requirements.txt

# نسخ ملف الإعدادات
copy .env.example .env
# أو Linux: cp .env.example .env
```

عدّل `.env` إذا احتجت (مثل تعديل كلمة سر MySQL أو البورت).

### تشغيل الترحيلات (migrations)

```bash
alembic upgrade head
```

### بذر حساب الأدمن والمحتوى (مرة واحدة فقط)

```bash
python scripts/setup_admin_content.py
```

ينشئ:
- أدمن: `admin@basma.com` / `Admin123!`
- 15 محتوى تعليمي

### تدريب نماذج ML (مرة واحدة)

```bash
python app/ml/train_models.py
```

### تشغيل السيرفر

```bash
uvicorn app.main:app --reload --port 8000
```

الباك إند يصير على: http://localhost:8000  
الـ API docs: http://localhost:8000/docs

## 3. إعداد الفرونت إند (Frontend)

```bash
# ارجع للمجلد الرئيسي
cd ..

# تثبيت الحزم
npm install

# تشغيل السيرفر التطويري
npm run dev
```

الفرونت إند يصير على: http://localhost:5173

## 4. تجربة المشروع

1. افتح http://localhost:5173
2. سجل دخول بـ `admin@basma.com` / `Admin123!`
3. راح تظهر شارة **مشرف** في الشريط الجانبي + رابط **لوحة المشرف**
4. لوحة المشرف فيها:
   - تبويب **المستخدمين**: عرض جميع المستخدمين + تعطيل
   - تبويب **المحتوى التعليمي**: إضافة/تعديل/حذف + بذر تجريبي

## 5. Docker (بديل سريع)

إذا كان Docker مثبّت:

```bash
docker compose up -d
```

يشتغل MySQL + الباك إند تلقائياً. بعدها شغّل الفرونت إند يدوي:
```bash
npm run dev
```

## ملاحظات مهمة

- **مفتاح Gemini API** موجود فعلًا في `.env` (شغال مع `gemini-2.5-flash`)
- **MySQL**: كلمة سر root فارغة افتراضياً في `.env`
- **التوكِن**: يُخزّن في `sessionStorage` (يستمر مع F5، يمسح عند إغلاق التبويبة)
- **الـ layout**: RTL عربي مع دعم English
- **عدد الاختبارات**: `cd backend && python -m pytest tests/ -v` (78 اختباراً كلها تمر)
