# usuarios/scripts/crear_operadores.py
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
from usuarios.models import Usuario, PerfilOperador, PerfilCoordinador, PerfilMonitor, PerfilSoporte

# -----------------------------
# Ruta del Excel
# -----------------------------
script_dir = os.path.dirname(__file__)
excel_path = os.path.join(script_dir, "excel", "soportes.xlsx")  
# -----------------------------
# Leer Excel y limpiar nombres de columnas
# -----------------------------
df = pd.read_excel(excel_path)
df.columns = df.columns.str.strip().str.lower()  # limpia espacios y minúsculas
print("Columnas detectadas:", df.columns)

# -----------------------------
# Crear grupo si no existe
# -----------------------------
grupo_operador, _ = Group.objects.get_or_create(name="grupo_operadores")

# -----------------------------
# Iterar sobre filas del Excel y crear usuarios y perfiles
# -----------------------------
for index, row in df.iterrows():
    # Limpiar nombres vacíos
    paterno = row['paterno'] if pd.notna(row['paterno']) else ""
    materno = row['materno'] if pd.notna(row['materno']) else ""
    nombres = row['nombres'] if pd.notna(row['nombres']) else ""

    # Username = paterno.ci
    username = f"{paterno.lower()}.{row['ci']}".strip(".")
    
    # Crear usuario Operador
    user, created = Usuario.objects.get_or_create(
        username=username,
        defaults={
            "rol": "operador",
            "email": row.get("email", ""),
            "is_staff": True,
        }
    )

    if created:
        user.set_password(str(row['ci']))  # contraseña por defecto = CI
        user.save()

    # Buscar coordinador, monitor y soporte si existen en la BD
    coordinador = None
    monitor = None
    soporte = None

    if pd.notna(row.get("codigo_coordinador", None)):
        try:
            coordinador = PerfilCoordinador.objects.get(codigo=str(row["codigo_coordinador"]))
        except PerfilCoordinador.DoesNotExist:
            print(f"⚠️ Coordinador {row['codigo_coordinador']} no encontrado para {username}")

    if pd.notna(row.get("codigo_monitor", None)):
        try:
            monitor = PerfilMonitor.objects.get(codigo=str(row["codigo_monitor"]))
        except PerfilMonitor.DoesNotExist:
            print(f"⚠️ Monitor {row['codigo_monitor']} no encontrado para {username}")

    if pd.notna(row.get("codigo_soporte", None)):
        try:
            soporte = PerfilSoporte.objects.get(codigo=str(row["codigo_soporte"]))
        except PerfilSoporte.DoesNotExist:
            print(f"⚠️ Soporte {row['codigo_soporte']} no encontrado para {username}")

    # Crear o actualizar perfil de operador
    if hasattr(user, "perfil_operador"):
        perfil = user.perfil_operador
        perfil.nombres = nombres
        perfil.paterno = paterno
        perfil.materno = materno
        perfil.celular = str(row['celular']) if pd.notna(row['celular']) else ""
        perfil.tipo_personal = row.get("tipo_personal", "")
        perfil.coordinador = coordinador
        perfil.monitor = monitor
        perfil.soporte = soporte
        perfil.save()
    else:
        perfil = PerfilOperador(
            ci=str(row['ci']),
            usuario=user,
            nombres=nombres,
            paterno=paterno,
            materno=materno,
            celular=str(row['celular']) if pd.notna(row['celular']) else "",
            tipo_personal=row.get("tipo_personal", ""),
            coordinador=coordinador,
            monitor=monitor,
            soporte=soporte
        )
        perfil.save()

    # Agregar usuario al grupo
    user.groups.add(grupo_operador)

print("✅ Operadores creados y actualizados con éxito")
