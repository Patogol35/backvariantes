#!/usr/bin/env bash
# fail on errors
set -o errexit

# Instala dependencias
pip install -r requirements.txt

# Recoge archivos estáticos
python manage.py collectstatic --noinput

# Aplica migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario automático si no existe
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
