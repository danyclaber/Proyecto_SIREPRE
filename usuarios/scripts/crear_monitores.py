# usuarios/scripts/crear_monitores.py
import sys
import os
import django
import pandas as pd

# -----------------------------
# Ajustar PYTHONPATH para encontrar el proyecto
# -----------------------------
sys.path.append(r"C:\Users\chris\OneDrive\Escritorio\DJANGO\SIREPRE\proyecto_sirepre")

# -----------------------------
# Configuración Django
# -----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto_sirepre.settings")
django.setup()

from django.contrib.auth.models import Group
from usuarios.models import Usuario, PerfilMonitor

# -----------------------------
# Ruta del Excel
# -----------------------------
script_dir = os.path.dirname(__file__)
excel_path = os.path.join(script_dir, "excel", "monitores.xlsx")  

# -----------------------------
# Leer Excel y limpiar nombres de columnas
# -----------------------------
try:
    df = pd.read_excel(excel_path)
except FileNotFoundError:
    print(f"Archivo no encontrado: {excel_path}")
    sys.exit(1)

df.columns = df.columns.str.strip().str.lower()  # elimina espacios y pasa a minúsculas
print("Columnas detectadas:", df.columns)

# -----------------------------
# Crear grupo si no existe
# -----------------------------
grupo_monitor, _ = Group.objects.get_or_create(name="grupo_monitores")

# -----------------------------
# Iterar sobre filas del Excel y crear usuarios y perfiles
# -----------------------------
for index, row in df.iterrows():
    try:
        # Limpiar nombres vacíos
        paterno = str(row.get('paterno', '')).strip()
        materno = str(row.get('materno', '')).strip()
        nombres = str(row.get('nombres', '')).strip()
        celular = str(row.get('celular', '')).strip()
        codigo = str(row.get('codigo', '')).strip()
        email = str(row.get('email', '')).strip()

        # Construir username único
        username = f"{paterno.lower()}.{materno.lower()}".strip(".")
        if not username:
            username = f"monitor{index}"

        # Crear usuario Monitor
        user, created = Usuario.objects.get_or_create(
            username=username,
            defaults={
                "rol": "monitor",
                "email": email,
                "is_staff": True,  # permite acceder al admin
            }
        )

        if created:
            user.set_password("Bolivia2025")  # contraseña por defecto
            user.save()

        # Crear o actualizar perfil de monitor
        if hasattr(user, "perfil_monitor"):
            perfil = user.perfil_monitor
            perfil.celular = celular
            perfil.nombres = nombres
            perfil.paterno = paterno
            perfil.materno = materno
            perfil.codigo = codigo
            perfil.save()
        else:
            perfil = PerfilMonitor(
                codigo=codigo,
                usuario=user,
                nombres=nombres,
                paterno=paterno,
                materno=materno,
                celular=celular
            )
            perfil.save()

        # Agregar usuario al grupo
        user.groups.add(grupo_monitor)

        print(f"Usuario creado/actualizado: {username}")

    except Exception as e:
        print(f"Error en fila {index}: {e}")

print("Monitores creados y actualizados con éxito ✅")
