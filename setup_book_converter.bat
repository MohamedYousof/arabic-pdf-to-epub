@echo off
chcp 65001 > nul
echo ===================================================
echo   تجهيز مجلد تحويل الكتب العربية لكيندل (EPUB3)
echo ===================================================
echo.

set "TARGET_DIR=%USERPROFILE%\Desktop\Book_Conversion"
echo [1/3] جاري انشاء مجلد العمل على سطح المكتب: %TARGET_DIR%
mkdir "%TARGET_DIR%" 2>nul
mkdir "%TARGET_DIR%\.agents\skills\arabic-pdf-to-epub" 2>nul

echo [2/3] جاري فحص لغة بايثون...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [تنبيه] لم يتم العثور على بايثون. يرجى تحميله وتثبيته مع تفعيل Add python.exe to PATH.
) else (
    echo [ممتاز] بايثون مثبت وجاهز للعمل!
)

echo [3/3] جاري تجهيز بيئة العمل...
echo ضع ملف كتاب الـ PDF الخاص بك داخل مجلد Book_Conversion على سطح المكتب.
echo.
echo ===================================================
echo   تم تجهيز المجلد بنجاح! افتح المجلد وضعه هناك.
echo ===================================================
pause
