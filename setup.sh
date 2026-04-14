#!/bin/bash

# Script de inicializacion del proyecto Django

set -e

echo "Inicializando proyecto Django..."

# Crear virtual environment si no existe
if [ ! -d "venv" ]; then
    echo "Creando virtual environment..."
    python3 -m venv venv
fi

# Activar virtual environment
source venv/bin/activate

# Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "Creando archivo .env..."
    cp .env.example .env
    echo "Actualiza el archivo .env con tus valores"
fi

# Hacer migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Crear superuser
echo "Crear superuser (usuario admin)..."
python manage.py createsuperuser

echo ""
echo "Instalacion completada!"
echo ""
echo "Proximos pasos:"
echo "1. Activar el virtual environment: source venv/bin/activate"
echo "2. Configurar OAuth en Django Admin (http://localhost:8000/admin/)"
echo "3. Ejecutar el servidor: python manage.py runserver"
echo ""
