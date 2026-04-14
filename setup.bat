@echo off
REM Script de inicializacion del proyecto Django para Windows

echo.
echo Inicializando proyecto Django...
echo.

REM Crear virtual environment si no existe
if not exist "venv" (
    echo Creando virtual environment...
    python -m venv venv
)

REM Activar virtual environment
call venv\Scripts\activate.bat

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Crear archivo .env si no existe
if not exist ".env" (
    echo Creando archivo .env...
    copy .env.example .env
    echo Actualiza el archivo .env con tus valores
)

REM Hacer migraciones
echo Aplicando migraciones...
python manage.py makemigrations
python manage.py migrate

REM Crear superuser
echo Crear superuser (usuario admin)...
python manage.py createsuperuser

echo.
echo Instalacion completada!
echo.
echo Proximos pasos:
echo 1. Activar el virtual environment: venv\Scripts\activate.bat
echo 2. Configurar OAuth en Django Admin (http://localhost:8000/admin/)
echo 3. Ejecutar el servidor: python manage.py runserver
echo.
pause
