#!/usr/bin/env bash
# Salir inmediatamente si ocurre un error
set -o errexit

# Instalar las dependencias de Python (incluyendo python-dotenv, whitenoise, etc.)
pip install -r requirements.txt

# Compilar o compilar los estilos de Tailwind 
python manage.py tailwind build

# Consolidar todos los archivos estáticos en la carpeta staticfiles/
python manage.py collectstatic --no-input

# Aplicar las migraciones de la base de datos en Clever Cloud o Render
python manage.py migrate