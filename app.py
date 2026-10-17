import datetime
import os
import sqlite3
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuración de página web
st.set_page_config(
    page_title="Top Motors - Cotizador", page_icon="🚗", layout="wide"
)

# --- BASE DE DATOS Y CONTROL DE FOLIOS ---
DB_FILE = "topmotors.db"


def inicializar_bd():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones (
            folio TEXT PRIMARY KEY,
            fecha TEXT,
            cliente TEXT,
            telefono TEXT,
            modelo TEXT,
            placa TEXT,
            total REAL,
            detalles TEXT
        )
    """)
  conn.commit()
  conn.close()


inicializar_bd()


def obtener_siguiente_folio():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT folio FROM cotizaciones WHERE folio LIKE ? ORDER BY folio DESC"
      " LIMIT 1",
      (f"TM-{datetime.date.today().year}-%",),
  )
  row = cursor.fetchone()
  conn.close()

  if row:
    try:
      ultimo_num = int(row[0].split("-")[-1])
      siguiente = ultimo_num + 1
    except:
      siguiente = 1
  else:
    siguiente = 1

  return f"TM-{datetime.date.today().year}-{siguiente:04d}"


def guardar_cotizacion_bd(
    folio, fecha, cliente, telefono, modelo, placa, total, detalles
):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR REPLACE INTO cotizaciones VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
      (folio, fecha, cliente, telefono, modelo, placa, total, detalles),
  )
  conn.commit()
  conn.close()


# Tarifas de Laminado
LAMINADO_NIVELES = {
    "Ninguno": 0,
    "Nivel A": 500,
    "Nivel B": 800,
    "Nivel C": 1500,
    "Nivel D": 2500,
    "Nivel E": 3500,
}

# Tarifas de Pintura por pieza
PIEZAS_PINTURA_CONFIG = {
    "Defensa delantera": {
        "Nivel A": 2250,
        "Nivel B": 3000,
        "Nivel C": 6500,
        "Tricapa": 3500,
    },
    "Defensa trasera": {
        "Nivel A": 2250,
        "Nivel B": 3000,
        "Nivel C": 6500,
        "Tricapa": 3500,
    },
    "Salpicadera Izquierda": {
        "Nivel A": 2250,
        "Nivel B": 2500,
        "Nivel C": 7000,
        "Tricapa": 3500,
    },
    "Salpicadera derecha": {
        "Nivel A": 2250,
        "Nivel B": 2500,
        "Nivel C": 7000,
        "Tricapa": 3500,
    },
    "Puerta delantera derecha": {
        "Nivel A": 2250,
        "Nivel B": 5000,
        "Nivel C": 8000,
        "Tricapa": 3500,
    },
    "Puerta delantera izquierda": {
        "Nivel A": 2250,
        "Nivel B": 5000,
        "Nivel C": 8000,
        "Tricapa": 3500,
    },
    "Puerta trasera derecha": {
        "Nivel A": 2250,
        "Nivel B": 5000,
        "Nivel C": 8000,
        "Tricapa": 3500,
    },
    "Puerta trasera izquierda": {
        "Nivel A": 2250,
        "Nivel B": 5000,
        "Nivel C": 8000,
        "Tricapa": 3500,
    },
    "Cofre": {
        "Nivel A": 2250,
        "Nivel B": 5000,
        "Nivel C": 9000,
        "Tricapa": 3500,
    },
    "Cajuela": {
        "Nivel A": 2250,
        "Nivel B": 5000,
        "Nivel C": 9000,
        "Tricapa": 3500,
    },
    "Costado lateral derecho": {
        "Nivel A": 2250,
        "Nivel B": 4000,
        "Nivel C": 9000,
        "Tricapa": 3500,
    },
    "Costado lateral izquierdo": {
        "Nivel A": 2250,
        "Nivel B": 4000,
        "Nivel C": 9000,
        "Tricapa": 3500,
    },
    "Techo": {
        "Nivel A": 2250,
        "Nivel B": 5000,
        "Nivel C": 10000,
        "Tricapa": 3500,
    },
    "Estribo derecho": {
        "Nivel A": 2250,
        "Nivel B": 4500,
        "Nivel C": 7500,
        "Tricapa": 3500,
    },
    "Estribo izquierdo": {
        "Nivel A": 2250,
        "Nivel B": 4500,
        "Nivel C": 7500,
        "Tricapa": 3500,
    },
    "Tapa de gasolina": {
        "Nivel A": 2250,
        "Nivel B": 1800,
        "Nivel C": 2500,
        "Tricapa": 3500,
    },
}

BANO_GENERAL_PRECIOS = {
    "Compacto": 25000,
    "Sedán mediano": 39000,
    "SUV compacta": 35000,
    "SUV mediana": 38000,
    "SUV grande": 45000,
    "Pick Up cabina sencilla": 38000,
    "Pick Up doble cabina": 45000,
    "Vehículo premium": 50000,
}

DETALLADO_PRECIOS = {
    "Auto Chico": 2500,
    "Auto Mediano": 3000,
    "Auto Grande": 3500,
    "Auto XL": 4000,
}

OPERACIONES_PRECIOS = {
    "Desarmado y armado defensa": 500,
    "Desarmado puerta": 700,
    "Desarmado cofre": 500,
    "Desarmado cajuela": 500,
    "Reparación de plástico (Promedio)": 1400,
    "Reparación de soportes (Promedio)": 1000,
    "Soldadura plástica (Promedio)": 1050,
    "Pulido profesional": 1600,
    "Detallado exterior": 2500,
    "Pulido y encerado completo": 2000,
    "Restauración de faros (par)": 900,
    "Detallado de Interiores": 1200,
}

INCREMENTO_VEHICULO = {
    "Compacto / Sedan": 0.0,
    "Sedán grande": 0.1,
    "SUV compacta": 0.15,
    "SUV mediana": 0.2,
    "SUV grande": 0.25,
    "Pick Up mediana": 0.25,
    "Pick Up grande": 0.35,
    "Vehículo premium": 0.3,
}

INCREMENTO_PINTURA = {
    "Sólido": 0.0,
    "Metálico": 0.1,
    "Perlado": 0.15,
    "Tricapa": 0.2,
    "Mate": 0.25,
}

DESCUENTOS = {
    "Sin descuento": 0.0,
    "5%": 0.05,
    "10%": 0.10,
    "13.33%": 0.1333,
    "15%": 0.15,
    "20%": 0.20,
}

st.title("Top Motors - Cotizador Profesional")
st.markdown("---")

# Controles en la barra lateral
st.sidebar.markdown("### Configuración de Tarifas y Promociones")
promocion_activa = st.sidebar.toggle(
    "Activar Promoción de Paquete (Nivel A)", value=True
)
promocion_tricapa = st.sidebar.toggle(
    "Activar Promoción Pintura Tricapa (3+ pzas, 15% desc)", value=True
)
modo_flotilla = st.sidebar.toggle(
    "Activar Precio de Flotilla ($2,000 por pieza Nivel A)", value=False
)

# Datos del Cliente
st.subheader("Datos del Cliente y Unidad")
col1, col2, col3, col4 = st.columns(4)
with col1:
  cliente = st.text_input("Cliente", "Top Motors")
with col2:
  telefono = st.text_input("Teléfono", "N/A")
with col3:
  modelo = st.text_input("Vehículo / Modelo", "N/A")
with col4:
  placa = st.text_input("Placas / Serie", "N/A")

fecha = st.text_input("Fecha", datetime.date.today().strftime("%d/%m/%Y"))

st.markdown("---")

# Pestañas Web (Incluyendo Historial)
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Laminado y Pintura por Pieza",
    "2. Baño General y Detallado",
    "3. Extras, 5 Manuales y Descuentos",
    "4. Historial de Cotizaciones",
])

laminado_selections = {}
pintura_selections = {}

with tab1:
  st.markdown("### Seleccione el nivel por pieza")
  for pieza in PIEZAS_PINTURA_CONFIG.keys():
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
      st.write(f"**{pieza}**")
    with c2:
      laminado_selections[pieza] = st.selectbox(
          f"Laminado - {pieza}",
          list(LAMINADO_NIVELES.keys()),
          key=f"lam_{pieza}",
      )
    with c3:
      pintura_selections[pieza] = st.selectbox(
          f"Pintura - {pieza}",
          ["Ninguno", "Nivel A", "Nivel B", "Nivel C", "Tricapa"],
          key=f"pin_{pieza}",
      )

with tab2:
  st.markdown("### Servicios Especiales")
  chk_bano = st.checkbox("Incluir Baño General de Pintura completo")
  bano_cat = st.selectbox(
      "Categoría Baño General", list(BANO_GENERAL_PRECIOS.keys())
  )

  st.markdown("---")
  chk_det = st.checkbox("Incluir Detallado Automotriz")
  det_cat = st.selectbox("Categoría Detallado", list(DETALLADO_PRECIOS.keys()))

with tab3:
  st.markdown("### Ajustes y Extras")
  col_a, col_b, col_c = st.columns(3)
  with col_a:
    tipo_v = st.selectbox("Tipo de Vehículo", list(INCREMENTO_VEHICULO.keys()))
  with col_b:
    tipo_p = st.selectbox("Tipo de Pintura", list(INCREMENTO_PINTURA.keys()))
  with col_c:
    desc_str = st.selectbox("Descuento", list(DESCUENTOS.keys()))

  st.markdown("### 5 Trabajos o Piezas Manuales")
  custom_entries = []
  for i in range(5):
    cm1, cm2 = st.columns([3, 1])
    with cm1:
      cname = st.text_input(f"Trabajo {i+1} (Nombre)", key=f"cname_{i}")
    with cm2:
      ccost = st.number_input(
          f"Costo {i+1} ($)", min_value=0.0, step=50.0, key=f"ccost_{i}"
      )
    custom_entries.append((cname, ccost))

  st.markdown("### Operaciones Adicionales")
  ops_selections = {}
  for op, precio in OPERACIONES_PRECIOS.items():
    ops_selections[op] = st.checkbox(f"{op} (${precio})")

  refacciones = st.number_input(
      "Costo Refacciones / Extras Libres ($)", min_value=0.0, step=50.0
  )

with tab4:
  st.markdown("### Historial de Cotizaciones Emitidas")
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT folio, fecha, cliente, modelo, total FROM cotizaciones ORDER BY"
      " folio DESC"
  )
  registros = cursor.fetchall()
  conn.close()

  if registros:
    busqueda = st.text_input("🔍 Buscar por Cliente, Modelo o Folio")
    for reg in registros:
      folio_r, fecha_r, cli_r, mod_r, tot_r = reg
      if (
          not busqueda
          or busqueda.lower() in folio_r.lower()
          or busqueda.lower() in cli_r.lower()
          or busqueda.lower() in mod_r.lower()
      ):
        with st.expander(
            f"Folio: {folio_r} | Cliente: {cli_r} | Total: ${tot_r:,.2f}"
        ):
          st.write(
              f"**Fecha:** {fecha_r} | **Vehículo:** {mod_r} | **Total:**"
              f" ${tot_r:,.2f}"
          )
  else:
    st.info(
        "Aún no hay cotizaciones guardadas. Genera una para verla aquí."
    )


# --- LÓGICA DE CÁLCULO ---
def realizar_calculos():
  subtotal_laminado = 0
  subtotal_pintura = 0
  piezas_afectadas = []

  for pieza, nivel_lam in laminado_selections.items():
    if nivel_lam != "Ninguno":
      precio_lam = LAMINADO_NIVELES[nivel_lam]
      subtotal_laminado += precio_lam
      piezas_afectadas.append((f"{pieza} (Laminado)", nivel_lam, precio_lam))

  piezas_nivel_a = []
  piezas_tricapa = []

  for pieza, nivel_pin in pintura_selections.items():
    if nivel_pin != "Ninguno":
      if nivel_pin == "Nivel A":
        piezas_nivel_a.append(pieza)
      elif nivel_pin == "Tricapa":
        piezas_tricapa.append(pieza)
      else:
        precio_pin = PIEZAS_PINTURA_CONFIG[pieza][nivel_pin]
        subtotal_pintura += precio_pin
        piezas_afectadas.append((f"{pieza} (Pintura)", nivel_pin, precio_pin))

  count_a = len(piezas_nivel_a)
  if count_a > 0:
    if modo_flotilla:
      precio_final_a = 2000.0
      etiqueta_nivel = "Nivel A (Flotilla $2,000)"
      for pieza in piezas_nivel_a:
        subtotal_pintura += precio_final_a
        piezas_afectadas.append(
            (f"{pieza} (Pintura)", etiqueta_nivel, precio_final_a)
        )
    else:
      if promocion_activa:
        precio_promo = (
            2250 if count_a == 1 else (1950 if count_a == 2 else 1800)
        )
        etiqueta_nivel = f"Nivel A (Promo {count_a} pzas)"
      else:
        etiqueta_nivel = "Nivel A"

      for pieza in piezas_nivel_a:
        p_final = precio_promo if promocion_activa else 2250.0
        subtotal_pintura += p_final
        piezas_afectadas.append((f"{pieza} (Pintura)", etiqueta_nivel, p_final))

  count_tri = len(piezas_tricapa)
  if count_tri > 0:
    if promocion_tricapa and count_tri >= 3:
      precio_final_tri = 2975.0
      etiqueta_tri = "Tricapa (Promo 3+ pzas: $2,975)"
    else:
      precio_final_tri = 3500.0
      etiqueta_tri = "Tricapa"

    for pieza in piezas_tricapa:
      subtotal_pintura += precio_final_tri
      piezas_afectadas.append(
          (f"{pieza} (Pintura)", etiqueta_tri, precio_final_tri)
      )

  inc_v = INCREMENTO_VEHICULO[tipo_v]
  ajuste_vehiculo = (subtotal_laminado + subtotal_pintura) * inc_v

  inc_p = INCREMENTO_PINTURA[tipo_p]
  ajuste_pintura = subtotal_pintura * inc_p

  bano_monto = BANO_GENERAL_PRECIOS[bano_cat] if chk_bano else 0
  det_monto = DETALLADO_PRECIOS[det_cat] if chk_det else 0

  custom_items = []
  for cname, ccost in custom_entries:
    if cname.strip() and ccost > 0:
      custom_items.append((cname, "Manual", ccost))

  subtotal_ops = 0
  ops_seleccionadas = []
  for op, selected in ops_selections.items():
    if selected:
      p_op = OPERACIONES_PRECIOS[op]
      subtotal_ops += p_op
      ops_seleccionadas.append((op, p_op))

  custom_total = sum(item[2] for item in custom_items)

  subtotal_bruto = (
      subtotal_laminado
      + subtotal_pintura
      + ajuste_vehiculo
      + ajuste_pintura
      + bano_monto
      + det_monto
      + subtotal_ops
      + custom_total
      + refacciones
  )

  porcentaje_desc = DESCUENTOS[desc_str]
  monto_descuento = subtotal_bruto * porcentaje_desc
  total = subtotal_bruto - monto_descuento

  return locals()


res = realizar_calculos()

st.markdown("---")
st.subheader("📋 Vista Previa del Resumen de Cotización")
col_prev1, col_prev2 = st.columns(2)
with col_prev1:
  st.write(f"**Cliente:** {cliente}")
  st.write(f"**Vehículo:** {modelo}")
with col_prev2:
  st.write(f"**Fecha:** {fecha}")
  st.write(f"**Total Final:** ${res['total']:,.2f}")

st.markdown("---")
st.subheader(f"💰 TOTAL FINAL: ${res['total']:,.2f}")


# --- GENERADOR DE PDF PARA WEB ---
def generar_pdf_web(folio_actual):
  filename = f"Cotizacion_{folio_actual}.pdf"
  c = canvas.Canvas(filename, pagesize=letter)
  width, height = letter

  if os.path.exists("logo.png"):
    c.drawImage(
        "logo.png",
        50,
        height - 65,
        width=130,
        height=40,
        preserveAspectRatio=True,
        mask="auto",
    )

  c.setFont("Helvetica-Bold", 8)
  c.drawString(
      190, height - 38, "Camino Real de Colima #45, Col. las Pomas, Tlaquepaque, Jal."
  )
  c.drawString(190, height - 50, "Tel: 33 3225 5557  /  33 3631 0784")
  c.setFont("Helvetica", 8)
  c.drawString(
      190, height - 62, "HORARIO: L-V 8:30 AM - 6 PM / S 8:30 AM - 2 PM"
  )
  c.drawString(190, height - 74, "FB: Top Motors Gdl    IG: @top_motors_gdl")

  c.line(50, height - 82, width - 50, height - 82)

  c.setFont("Helvetica-Bold", 11)
  c.drawString(50, height - 100, f"FOLIO: {folio_actual}")
  c.setFont("Helvetica", 9)
  c.drawString(400, height - 100, f"Fecha: {fecha}")

  c.setFont("Helvetica-Bold", 10)
  c.drawString(50, height - 118, "Datos del Cliente y Unidad:")
  c.setFont("Helvetica", 9)
  c.drawString(50, height - 131, f"Cliente: {cliente}")
  c.drawString(300, height - 131, f"Teléfono: {telefono}")
  c.drawString(50, height - 144, f"Vehículo / Modelo: {modelo}")
  c.drawString(300, height - 144, f"Placas / Serie: {placa}")

  c.line(50, height - 152, width - 50, height - 152)

  y = height - 168
  c.setFont("Helvetica-Bold", 10)
  c.drawString(50, y, "Desglose de Servicios y Piezas:")
  y -= 15
  c.setFont("Helvetica-Bold", 9)
  c.drawString(60, y, "Concepto / Pieza")
  c.drawString(260, y, "Nivel / Detalle")
  c.drawString(420, y, "Subtotal")
  y -= 12

  c.setFont("Helvetica", 9)
  for pieza, nivel, precio in res["piezas_afectadas"]:
    if y < 130:
      c.showPage()
      y = height - 50
    c.drawString(60, y, pieza)
    c.drawString(260, y, nivel)
    c.drawString(420, y, f"${precio:,.2f}")
    y -= 12

  for cname, cdet, ccost in res["custom_items"]:
    if y < 130:
      c.showPage()
      y = height - 50
    c.drawString(60, y, cname)
    c.drawString(260, y, cdet)
    c.drawString(420, y, f"${ccost:,.2f}")
    y -= 12

  if res["bano_monto"] > 0:
    if y < 130:
      c.showPage()
      y = height - 50
    c.drawString(60, y, f"Baño General de Pintura ({bano_cat})")
    c.drawString(260, y, "Servicio Completo")
    c.drawString(420, y, f"${res['bano_monto']:,.2f}")
    y -= 12

  if res["det_monto"] > 0:
    if y < 130:
      c.showPage()
      y = height - 50
    c.drawString(60, y, f"Detallado Automotriz ({det_cat})")
    c.drawString(260, y, "Servicio Completo")
    c.drawString(420, y, f"${res['det_monto']:,.2f}")
    y -= 12

  if res["ops_seleccionadas"]:
    y -= 5
    for op, precio in res["ops_seleccionadas"]:
      if y < 130:
        c.showPage()
        y = height - 50
      c.drawString(60, y, op)
      c.drawString(260, y, "Operación Adicional")
      c.drawString(420, y, f"${precio:,.2f}")
      y -= 12

  y -= 10
  c.line(50, y, width - 50, y)
  y -= 18

  c.setFont("Helvetica-Bold", 10)
  c.drawString(50, y, "Resumen Financiero:")
  y -= 15
  c.setFont("Helvetica", 9)

  if res["subtotal_laminado"] > 0 or res["subtotal_pintura"] > 0:
    c.drawString(
        60,
        y,
        f"Subtotal Laminado/Pintura Piezas:"
        f" ${res['subtotal_laminado']+res['subtotal_pintura']:,.2f}",
    )
    y -= 12

  c.drawString(60, y, f"Operaciones Adicionales: ${res['subtotal_ops']:,.2f}")
  y -= 12
  c.drawString(60, y, f"Refacciones / Extras: ${refacciones:,.2f}")
  y -= 12
  c.drawString(
      60,
      y,
      f"Descuento Aplicado ({desc_str}): -${res['monto_descuento']:,.2f}",
  )

  y -= 22
  c.setFont("Helvetica-Bold", 12)
  c.drawString(60, y, f"TOTAL FINAL: ${res['total']:,.2f}")

  c.setFont("Helvetica", 7)
  c.drawString(
      50,
      38,
      "*APLICA RESTRICCIONES  *PROMOCIÓN VÁLIDA EN SEPTIEMBRE 2026"
      "  *TARJETAS PARTICIPANTES",
  )
  c.drawString(
      50,
      28,
      "*TODOS NUESTROS SERVICIOS CUENTAN CON 90 DÍAS DE GARANTÍA  *NO APLICA"
      " CON OTRAS PROMOCIONES",
  )

  c.save()
  return filename


if st.button("📄 Generar Cotización y Folio"):
  nuevo_folio = obtener_siguiente_folio()
  guardar_cotizacion_bd(
      nuevo_folio,
      fecha,
      cliente,
      telefono,
      modelo,
      placa,
      res["total"],
      "Detalle guardado",
  )
  st.success(
      f"¡Cotización generada y guardada con éxito! Folio asignado: {nuevo_folio}"
  )

  pdf_file = generar_pdf_web(nuevo_folio)
  with open(pdf_file, "rb") as f:
    st.download_button(
        label="📥 Descargar Archivo PDF con Folio",
        data=f,
        file_name=pdf_file,
        mime="application/pdf",
    )