import datetime
import os
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuración de página web
st.set_page_config(
    page_title="Cotizador Topmotors", page_icon="🚗", layout="wide"
)

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
    },
    "Defensa trasera": {"Nivel A": 2250, "Nivel B": 3000, "Nivel C": 6500},
    "Salpicadera Izquierda": {
        "Nivel A": 2250,
        "Nivel B": 2500,
        "Nivel C": 7000,
    },
    "Salpicadera derecha": {"Nivel A": 2250, "Nivel B": 2500, "Nivel C": 7000},
    "Puerta delantera derecha": {
        "Nivel A": 2500,
        "Nivel B": 5000,
        "Nivel C": 8000,
    },
    "Puerta delantera izquierda": {
        "Nivel A": 2500,
        "Nivel B": 5000,
        "Nivel C": 8000,
    },
    "Puerta trasera derecha": {"Nivel A": 2500, "Nivel B": 5000, "Nivel C": 8000},
    "Puerta trasera izquierda": {
        "Nivel A": 2500,
        "Nivel B": 5000,
        "Nivel C": 8000,
    },
    "Cofre": {"Nivel A": 3500, "Nivel B": 5000, "Nivel C": 9000},
    "Cajuela": {"Nivel A": 3500, "Nivel B": 5000, "Nivel C": 9000},
    "Costado lateral derecho": {
        "Nivel A": 3000,
        "Nivel B": 4000,
        "Nivel C": 9000,
    },
    "Costado lateral izquierdo": {
        "Nivel A": 3000,
        "Nivel B": 4000,
        "Nivel C": 9000,
    },
    "Techo": {"Nivel A": 3500, "Nivel B": 5000, "Nivel C": 10000},
    "Estribo derecho": {"Nivel A": 2250, "Nivel B": 4500, "Nivel C": 7500},
    "Estribo izquierdo": {"Nivel A": 2250, "Nivel B": 4500, "Nivel C": 7500},
    "Tapa de gasolina": {"Nivel A": 1200, "Nivel B": 1800, "Nivel C": 2500},
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

st.title("🚗 COTIZACIÓN LAMINADO Y PINTURA TOPMOTORS")
st.markdown("---")

# Datos del Cliente
st.subheader("Datos del Cliente y Unidad")
col1, col2, col3, col4 = st.columns(4)
with col1:
  cliente = st.text_input("Cliente", "Mostrador")
with col2:
  telefono = st.text_input("Teléfono", "N/A")
with col3:
  modelo = st.text_input("Vehículo / Modelo", "N/A")
with col4:
  placa = st.text_input("Placas / Serie", "N/A")

fecha = st.text_input(
    "Fecha", datetime.date.today().strftime("%d/%m/%Y")
)

st.markdown("---")

# Pestañas Web
tab1, tab2, tab3 = st.tabs([
    "1. Laminado y Pintura por Pieza",
    "2. Baño General y Detallado",
    "3. Extras, 5 Manuales y Descuentos",
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
          ["Ninguno", "Nivel A", "Nivel B", "Nivel C"],
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
  det_cat = st.selectbox(
      "Categoría Detallado", list(DETALLADO_PRECIOS.keys())
  )

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
  for pieza, nivel_pin in pintura_selections.items():
    if nivel_pin != "Ninguno":
      if nivel_pin == "Nivel A":
        piezas_nivel_a.append(pieza)
      else:
        precio_pin = PIEZAS_PINTURA_CONFIG[pieza][nivel_pin]
        subtotal_pintura += precio_pin
        piezas_afectadas.append((f"{pieza} (Pintura)", nivel_pin, precio_pin))

  count_a = len(piezas_nivel_a)
  if count_a > 0:
    precio_promo = 2250 if count_a == 1 else (1950 if count_a == 2 else 1800)
    for pieza in piezas_nivel_a:
      subtotal_pintura += precio_promo
      piezas_afectadas.append(
          (f"{pieza} (Pintura)", f"Nivel A (Promo {count_a} pzas)", precio_promo)
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
st.subheader(f"💰 TOTAL FINAL: ${res['total']:,.2f}")


# --- GENERADOR DE PDF PARA WEB ---
def generar_pdf_web():
  filename = "Cotizacion_Topmotors.pdf"
  c = canvas.Canvas(filename, pagesize=letter)
  width, height = letter

  c.setFont("Helvetica-Bold", 14)
  c.drawString(50, height - 40, "COTIZACIÓN LAMINADO Y PINTURA TOPMOTORS")
  c.setFont("Helvetica", 10)
  c.drawString(50, height - 55, "ORDEN DE COTIZACIÓN INTEGRAL")
  c.line(50, height - 63, width - 50, height - 63)

  c.setFont("Helvetica-Bold", 10)
  c.drawString(50, height - 80, "Datos del Cliente y Unidad:")
  c.setFont("Helvetica", 9)
  c.drawString(50, height - 95, f"Cliente: {cliente}")
  c.drawString(300, height - 95, f"Teléfono: {telefono}")
  c.drawString(50, height - 108, f"Vehículo / Modelo: {modelo}")
  c.drawString(300, height - 108, f"Placas / Serie: {placa}")
  c.drawString(50, height - 121, f"Fecha: {fecha}")

  c.line(50, height - 130, width - 50, height - 130)

  y = height - 145
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
    if y < 100:
      c.showPage()
      y = height - 50
    c.drawString(60, y, pieza)
    c.drawString(260, y, nivel)
    c.drawString(420, y, f"${precio:,.2f}")
    y -= 12

  for cname, cdet, ccost in res["custom_items"]:
    if y < 100:
      c.showPage()
      y = height - 50
    c.drawString(60, y, cname)
    c.drawString(260, y, cdet)
    c.drawString(420, y, f"${ccost:,.2f}")
    y -= 12

  if res["bano_monto"] > 0:
    c.drawString(60, y, f"Baño General de Pintura ({bano_cat})")
    c.drawString(260, y, "Servicio Completo")
    c.drawString(420, y, f"${res['bano_monto']:,.2f}")
    y -= 12

  if res["det_monto"] > 0:
    c.drawString(60, y, f"Detallado Automotriz ({det_cat})")
    c.drawString(260, y, "Servicio Completo")
    c.drawString(420, y, f"${res['det_monto']:,.2f}")
    y -= 12

  if res["ops_seleccionadas"]:
    y -= 5
    for op, precio in res["ops_seleccionadas"]:
      if y < 100:
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

  y -= 20
  c.setFont("Helvetica-Bold", 12)
  c.drawString(60, y, f"TOTAL FINAL: ${res['total']:,.2f}")

  c.save()
  return filename


if st.button("📄 Generar y Descargar PDF"):
  pdf_file = generar_pdf_web()
  with open(pdf_file, "rb") as f:
    st.download_button(
        label="📥 Descargar Archivo PDF",
        data=f,
        file_name=pdf_file,
        mime="application/pdf",
    )