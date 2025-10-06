import sys
import os
import django
import pandas as pd

# -----------------------------
# Configuración Django
# -----------------------------
sys.path.append(r"C:\Users\chris\OneDrive\Escritorio\DJANGO\SIREPRE\proyecto_sirepre")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto_sirepre.settings")
django.setup()

from usuarios.models import PerfilOperador, DetalleAdicional

# -----------------------------
# Ruta del Excel
# -----------------------------
script_dir = os.path.dirname(__file__)
excel_path = os.path.join(script_dir, "excel", "detalles_adicionales_operador.xlsx")

# -----------------------------
# Leer Excel
# -----------------------------
try:
    df = pd.read_excel(excel_path)
except FileNotFoundError:
    print(f"Archivo no encontrado: {excel_path}")
    sys.exit(1)

df.columns = df.columns.str.strip().str.lower()

errores = []

for index, row in df.iterrows():
    try:
        ci_operador = str(row.get("ci", "")).strip()
        operador = PerfilOperador.objects.filter(ci=ci_operador).first()
        if not operador:
            errores.append(f"Operador no encontrado CI: {ci_operador}")
            continue

        # Función para limpiar valores
        def clean_val(val):
            if pd.isna(val) or str(val).strip() == "":
                return "-"
            try:
                # Si es float sin decimales, convertir a int
                if isinstance(val, float) and val.is_integer():
                    return str(int(val))
                return str(val).strip()
            except:
                return str(val).strip()

        usuario_apk = clean_val(row.get("usuario_apk"))
        transmitido = clean_val(row.get("transmitido"))
        no_transmitido = clean_val(row.get("no_transmitido"))

        # Crear o actualizar
        detalle, created = DetalleAdicional.objects.update_or_create(
            operador=operador,
            defaults={
                "usuario_apk": usuario_apk,
                "transmitido": transmitido,
                "no_transmitido": no_transmitido,
            }
        )

        if created:
            print(f"✅ Detalle creado para operador CI {ci_operador}")
        else:
            print(f"♻️ Detalle actualizado para operador CI {ci_operador}")

    except Exception as e:
        errores.append(f"Fila {index+1}, CI {ci_operador}: {e}")

# -----------------------------
# Mostrar errores
# -----------------------------
if errores:
    print("Errores:")
    for e in errores:
        print(f"- {e}")
else:
    print("Todos los detalles creados o actualizados correctamente ✅")
