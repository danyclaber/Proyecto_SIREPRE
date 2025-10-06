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

from usuarios.models import PerfilOperador, Acta

# -----------------------------
# Ruta del Excel
# -----------------------------
script_dir = os.path.dirname(__file__)
excel_path = os.path.join(script_dir, "excel", "acta_operador.xlsx")

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
# Crear o actualizar actas desde Excel
# -----------------------------
errores = []  # Lista de actas que no se pudieron crear

for index, row in df.iterrows():
    codigo_esperado = f"A{str(index+1).zfill(6)}"  # A000001, A000002...

    try:
        # Limpiar campos de texto y reemplazar vacíos por "-"
        provincia = str(row.get("provincia", "-")).strip() or "-"
        municipio = str(row.get("municipio", "-")).strip() or "-"
        localidad = str(row.get("localidad", "-")).strip() or "-"
        recinto = str(row.get("recinto", "-")).strip() or "-"
        actas_asignadas = str(row.get("actas_asignadas", "-")).strip() or "-"

        # Buscar operador por CI
        ci_operador = str(row.get("ci", "")).strip()
        operador = PerfilOperador.objects.filter(ci=ci_operador).first()
        if not operador:
            msg = f"Operador no encontrado (CI: {ci_operador})"
            print(f"⚠️ Fila {index+1}: {msg}, Acta esperada: {codigo_esperado}")
            errores.append((codigo_esperado, msg))
            continue

        # Preparar valores de mesas como texto, evitando decimales
        mesas = {}
        for i in range(1, 9):
            val = row.get(f"mesa{i}", "-")
            if pd.isna(val) or str(val).strip() == "":
                val = "-"
            else:
                # Convertir a entero si es numérico
                try:
                    val = int(val)
                except:
                    val = str(val).strip()
            mesas[f"mesa{i}"] = val

        # Verificar si ya existe un Acta para este operador
        acta, created = Acta.objects.update_or_create(
            operador=operador,
            defaults={
                "actas_asignadas": actas_asignadas,
                "provincia": provincia,
                "municipio": municipio,
                "localidad": localidad,
                "recinto": recinto,
                "mesa1": mesas["mesa1"],
                "mesa2": mesas["mesa2"],
                "mesa3": mesas["mesa3"],
                "mesa4": mesas["mesa4"],
                "mesa5": mesas["mesa5"],
                "mesa6": mesas["mesa6"],
                "mesa7": mesas["mesa7"],
                "mesa8": mesas["mesa8"],
            }
        )

        if created:
            print(f"✅ Acta creada: {acta.codigo} para operador CI {ci_operador}")
        else:
            print(f"♻️ Acta actualizada: {acta.codigo} para operador CI {ci_operador}")

    except Exception as e:
        msg = f"Error fila {index+1}: {e}"
        print(f"❌ {msg}")
        errores.append((codigo_esperado, str(e)))

# -----------------------------
# Resumen final
# -----------------------------
print("\n📌 Proceso finalizado ✅")
if errores:
    print("❌ Actas que NO se pudieron crear o actualizar:")
    for codigo, motivo in errores:
        print(f"   - {codigo}: {motivo}")
else:
    print("✅ Todas las actas fueron creadas o actualizadas correctamente.")
