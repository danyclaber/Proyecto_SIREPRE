# usuarios/scripts/crear_coordinadores.py
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
from usuarios.models import Usuario, PerfilCoordinador

# -----------------------------
# Ruta del Excel
# -----------------------------
script_dir = os.path.dirname(__file__)
excel_path = os.path.join(script_dir, "excel", "coordinadores.xlsx")  

# -----------------------------
# Leer Excel y limpiar nombres de columnas
# -----------------------------
try:
    df = pd.read_excel(excel_path)
except FileNotFoundError:
    print(f"Archivo no encontrado: {excel_path}")
    sys.exit(1)

df.columns = df.columns.str.strip().str.lower()
print("Columnas detectadas:", df.columns)

# -----------------------------
# Crear grupo si no existe
# -----------------------------
grupo_coordinador, _ = Group.objects.get_or_create(name="grupo_coordinadores")

# -----------------------------
# Iterar sobre filas del Excel y crear usuarios y perfiles
# -----------------------------
for index, row in df.iterrows():
    try:
        # Limpiar datos
        paterno = str(row.get('paterno', '')).strip()
        materno = str(row.get('materno', '')).strip()
        nombres = str(row.get('nombres', '')).strip()
        celular = str(row.get('celular', '')).strip()
        codigo = str(row.get('codigo', '')).strip()
        email = str(row.get('email', '')).strip()

        # Construir username único
        username = f"{paterno.lower()}.{materno.lower()}".strip(".")
        if not username:
            username = f"coordinador{index}"

        # Crear usuario Coordinador
        user, created = Usuario.objects.get_or_create(
            username=username,
            defaults={
                "rol": "coordinador",
                "email": email,
                "is_staff": True,
            }
        )

        if created:
            user.set_password("Bolivia2025")
            user.save()

        # Crear o actualizar perfil de coordinador
        if hasattr(user, "perfil_coordinador"):
            perfil = user.perfil_coordinador
            perfil.nombres = nombres
            perfil.paterno = paterno
            perfil.materno = materno
            perfil.celular = celular
            perfil.codigo = codigo
            perfil.save()
        else:
            perfil = PerfilCoordinador(
                codigo=codigo,
                usuario=user,
                nombres=nombres,
                paterno=paterno,
                materno=materno,
                celular=celular
            )
            perfil.save()

        # Agregar usuario al grupo
        user.groups.add(grupo_coordinador)

        print(f"Usuario creado/actualizado: {username}")

    except Exception as e:
        print(f"Error en fila {index}: {e}")

print("Coordinadores creados y agregados al grupo con éxito ✅")
