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

from usuarios.models import PerfilOperador, ObservacionAdicional

# -----------------------------
# Ruta del Excel
# -----------------------------
script_dir = os.path.dirname(__file__)
excel_path = os.path.join(script_dir, "excel", "observaciones_adicionales_operador.xlsx")  # tu archivo

# -----------------------------
# Leer Excel
# -----------------------------
try:
    df = pd.read_excel(excel_path)
except FileNotFoundError:
    print(f"Archivo no encontrado: {excel_path}")
    sys.exit(1)

df.columns = df.columns.str.strip().str.lower()
print("Columnas detectadas:", df.columns)

# -----------------------------
# Lista de errores
# -----------------------------
errores = []

# -----------------------------
# Iterar sobre cada fila
# -----------------------------
for index, row in df.iterrows():
    try:
        # Obtener operador por CI
        ci_operador = str(row.get("ci", "")).strip()
        operador = PerfilOperador.objects.filter(ci=ci_operador).first()
        if not operador:
            msg = f"Operador no encontrado en fila {index+1}, CI: {ci_operador}"
            print(f"❌ {msg}")
            errores.append(msg)
            continue

        # Observación
        observacion = str(row.get("observacion", "-")).strip()
        if not observacion:
            observacion = "-"

        # Fecha
        fecha_raw = row.get("fecha", "-")
        if pd.isna(fecha_raw) or str(fecha_raw).strip() == "":
            fecha = "-"
        else:
            try:
                fecha = pd.to_datetime(fecha_raw).strftime("%d/%m/%Y")
            except:
                fecha = str(fecha_raw).strip()

        # Evitar duplicados: si ya existe la misma observación exacta para el operador, actualizar fecha
        obs_obj, created = ObservacionAdicional.objects.update_or_create(
            operador=operador,
            observacion=observacion,
            defaults={"fecha": fecha}
        )

        if created:
            print(f"✅ Observación creada para operador CI {ci_operador}: {observacion}")
        else:
            print(f"♻️ Observación actualizada para operador CI {ci_operador}: {observacion}")

    except Exception as e:
        msg = f"Error en fila {index+1}, operador CI {ci_operador}: {e}"
        print(f"❌ {msg}")
        errores.append(msg)

# -----------------------------
# Resumen final
# -----------------------------
print("\n📌 Proceso finalizado ✅")
if errores:
    print("❌ Observaciones que NO se pudieron crear o actualizar:")
    for e in errores:
        print(f"- {e}")
else:
    print("✅ Todas las observaciones fueron creadas o actualizadas correctamente.")
