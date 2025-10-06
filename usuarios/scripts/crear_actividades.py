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

from usuarios.models import PerfilOperador, Actividad

# -----------------------------
# Ruta del Excel
# -----------------------------
script_dir = os.path.dirname(__file__)
excel_path = os.path.join(script_dir, "excel", "actividades_operador.xlsx")  # tu archivo

# -----------------------------
# Leer todas las hojas del Excel
# -----------------------------
try:
    xls = pd.ExcelFile(excel_path)
except FileNotFoundError:
    print(f"Archivo no encontrado: {excel_path}")
    sys.exit(1)

print("Hojas detectadas:", xls.sheet_names)

# -----------------------------
# Lista para registrar errores
# -----------------------------
errores = []

# -----------------------------
# Iterar sobre cada hoja
# -----------------------------
for hoja in xls.sheet_names:
    print(f"\nProcesando hoja: {hoja}")
    df = pd.read_excel(excel_path, sheet_name=hoja)
    df.columns = df.columns.str.strip().str.lower()  # limpiar nombres de columnas

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

            # Estado como booleano
            estado_val = row.get("estado", 0)
            estado = bool(int(estado_val)) if estado_val not in [None, ""] else False

            # Fecha en formato DD/MM/YYYY, "-" si está vacía
            fecha_raw = row.get("fecha")
            if pd.isna(fecha_raw) or str(fecha_raw).strip() == "":
                fecha = "-"
            else:
                fecha = pd.to_datetime(fecha_raw).strftime("%d/%m/%Y")

            # Observación, "-" si está vacía
            observacion_raw = row.get("observacion")
            if pd.isna(observacion_raw) or str(observacion_raw).strip() == "":
                observacion = "-"
            else:
                observacion = str(observacion_raw).strip()

            # Descripción
            descripcion = str(row.get("descripcion", hoja)).strip()  # usar nombre de hoja si no hay descripción

            # Evitar duplicados: actualizar si ya existe
            actividad, created = Actividad.objects.update_or_create(
                operador=operador,
                descripcion=descripcion,
                defaults={
                    "estado": estado,
                    "fecha": fecha,
                    "observacion": observacion
                }
            )

            if created:
                print(f"✅ Actividad creada: {descripcion} para operador CI {ci_operador}")
            else:
                print(f"♻️ Actividad actualizada: {descripcion} para operador CI {ci_operador}")

        except Exception as e:
            msg = f"Error en fila {index+1}, operador CI {ci_operador}: {e}"
            print(f"❌ {msg}")
            errores.append(msg)

# -----------------------------
# Mostrar errores al final
# -----------------------------
if errores:
    print("\nResumen de actividades NO creadas o actualizadas:")
    for e in errores:
        print(f"- {e}")
else:
    print("\nTodas las actividades se crearon o actualizaron correctamente ✅")
