#!/usr/bin/env bash
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Archivos estáticos
python manage.py collectstatic --noinput

# 🔥 SOLO aplicar migraciones (NO crearlas)
python manage.py migrate --noinput

# Crear superusuario si no existe
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()

username = "admin"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email="patogol3535@gmail.com",
        password="jorgepatricio26"
    )
END
