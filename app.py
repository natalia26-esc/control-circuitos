from datetime import datetime
import pandas as pd
import streamlit as st

EXCEL_FILE = "control_circuitos.xlsx"

# Listas oficiales
PLAZAS = ["MÉRIDA", "CANCÚN", "VILLAHERMOSA", "VERACRUZ", "TOLUCA", "TUXTLA"]
OPERADORES = ["EBER SOLIS", "JUAN PEREZ", "CARLOS GOMEZ", "JOSÉ RAMÍREZ", "MANUEL LÓPEZ"]


def init_excel():
  try:
    df = pd.read_excel(EXCEL_FILE)
  except FileNotFoundError:
    columns = [
        "ORIGEN",
        "FECHA SALIDA",
        "HORA SALIDA",
        "CIRCUITO",
        "OPERADOR",
        "NO. ECO",
        "FOLIO",
        "DESTINO",
        "FECHA LLEGADA DESTINO FINAL",
        "HORA LLEGADA DESTINO FINAL",
        "COMENTARIOS/OBSERVACIONES",
    ]
    df = pd.DataFrame(columns=columns)
    df.to_excel(EXCEL_FILE, index=False)


init_excel()

st.title("Control de Circuitos entre Plazas")

# Selección de Plaza actual fija
plaza_actual = st.selectbox("Selecciona tu Plaza Actual:", PLAZAS)

st.markdown("---")

# MENÚ FIJO CON BOTONES (En lugar de desplegable lateral)
st.markdown("### Menú de Opciones")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

# Usamos session_state para mantener la pestaña seleccionada
if "menu_activo" not in st.session_state:
  st.session_state.menu_activo = "Registrar Salida"

if col_m1.button("Registrar Salida", use_container_width=True):
  st.session_state.menu_activo = "Registrar Salida"
if col_m2.button("Registrar Llegada", use_container_width=True):
  st.session_state.menu_activo = "Registrar Llegada"
if col_m3.button("Llegada sin Salida", use_container_width=True):
  st.session_state.menu_activo = "Llegada sin Salida"
if col_m4.button("Salida con Llegada previa", use_container_width=True):
  st.session_state.menu_activo = "Salida con Llegada previa"

menu = st.session_state.menu_activo
st.markdown(f"**Modo actual:** {menu}")
st.markdown("---")

# ---------------------------------------------------------
# 1. REGISTRAR SALIDA
# ---------------------------------------------------------
if menu == "Registrar Salida":
  st.header(f"Registrar Salida desde: {plaza_actual}")

  with st.form("form_salida"):
    now = datetime.now()
    fecha_salida = now.strftime("%d/%m/%Y")
    hora_salida = now.strftime("%H:%M:%S")

    st.write(f"**Fecha de Salida (Automática):** {fecha_salida}")
    st.write(f"**Hora de Salida (Automática):** {hora_salida}")

    # Destinos posibles (excluyendo la propia plaza)
    destinos_posibles = [p for p in PLAZAS if p != plaza_actual]
    destino = st.selectbox("Plaza Destino", destinos_posibles)

    # Circuito automático basado en Origen y Destino
    circuito = f"{plaza_actual[:3]}-{destino[:3]}".upper()
    st.info(f"Circuito generado automáticamente: **{circuito}**")

    operador = st.selectbox("Operador", OPERADORES)
    no_eco = st.text_input("No. Económico (Ej: 535)")
    folio = st.text_input("Folio del Circuito (Ej: DQ00032584)")

    submitted = st.form_submit_button("Guardar Salida")

    if submitted:
      if not folio or not no_eco:
        st.error("Por favor completa el folio y el número económico.")
      else:
        df = pd.read_excel(EXCEL_FILE, dtype=str)
        df.fillna("", inplace=True)

        if not df[df["FOLIO"].astype(str) == str(folio)].empty:
          st.error("¡El folio ya se encuentra registrado!")
        else:
          nueva_fila = {
              "ORIGEN": plaza_actual,
              "FECHA SALIDA": fecha_salida,
              "HORA SALIDA": hora_salida,
              "CIRCUITO": circuito,
              "OPERADOR": operador,
              "NO. ECO": str(no_eco),
              "FOLIO": str(folio),
              "DESTINO": destino,
              "FECHA LLEGADA DESTINO FINAL": "",
              "HORA LLEGADA DESTINO FINAL": "",
              "COMENTARIOS/OBSERVACIONES": "",
          }
          df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
          df.to_excel(EXCEL_FILE, index=False)
          st.success(
              f"¡Salida del folio {folio} registrada correctamente hacia"
              f" {destino}!"
          )
          st.rerun()

# ---------------------------------------------------------
# 2. REGISTRAR LLEGADA (PENDIENTES)
# ---------------------------------------------------------
elif menu == "Registrar Llegada":
  st.header(f"Registrar Llegada en: {plaza_actual}")
  df = pd.read_excel(EXCEL_FILE, dtype=str)
  df.fillna("", inplace=True)

  pendientes = df[
      (df["DESTINO"] == plaza_actual)
      & (
          df["FECHA LLEGADA DESTINO FINAL"].isna()
          | (df["FECHA LLEGADA DESTINO FINAL"] == "")
      )
  ]

  if pendientes.empty:
    st.info("No hay circuitos pendientes de llegada para tu plaza.")
  else:
    st.write("Selecciona el circuito que acaba de llegar:")
    folios_disponibles = pendientes["FOLIO"].astype(str).tolist()
    folio_seleccionado = st.selectbox("Folio Pendiente", folios_disponibles)

    circuito_info = pendientes[
        pendientes["FOLIO"].astype(str) == folio_seleccionado
    ].iloc[0]
    st.markdown("### Datos del Viaje:")
    st.write(f"- **Origen:** {circuito_info['ORIGEN']}")
    st.write(f"- **Circuito:** {circuito_info['CIRCUITO']}")
    st.write(f"- **Operador:** {circuito_info['OPERADOR']}")
    st.write(f"- **Económico:** {circuito_info['NO. ECO']}")

    with st.form("form_llegada"):
      now = datetime.now()
      fecha_llegada = now.strftime("%d/%m/%Y")
      hora_llegada = now.strftime("%H:%M:%S")

      st.write(f"**Fecha de Llegada (Automática):** {fecha_llegada}")
      st.write(f"**Hora de Llegada (Automática):** {hora_llegada}")
      observaciones = st.text_area(
          "Comentarios / Observaciones", value="Sin Incidencias"
      )

      submitted_llegada = st.form_submit_button("Guardar Llegada")

      if submitted_llegada:
        idx = df[df["FOLIO"].astype(str) == folio_seleccionado].index[0]
        df.loc[idx, "FECHA LLEGADA DESTINO FINAL"] = str(fecha_llegada)
        df.loc[idx, "HORA LLEGADA DESTINO FINAL"] = str(hora_llegada)
        df.loc[idx, "COMENTARIOS/OBSERVACIONES"] = str(observaciones)

        df.to_excel(EXCEL_FILE, index=False)
        st.success(
            f"¡Llegada del folio {folio_seleccionado} registrada con éxito!"
        )
        st.rerun()

# ---------------------------------------------------------
# 3. CAPTURAR LLEGADA SIN SALIDA PREVIA
# ---------------------------------------------------------
elif menu == "Llegada sin Salida":
  st.header(f"Registro Directo (Sin Salida Previa) en: {plaza_actual}")

  with st.form("form_directo"):
    origen = st.selectbox(
        "Plaza de Origen", [p for p in PLAZAS if p != plaza_actual]
    )
    now = datetime.now()
    
    # Automáticas para salida y llegada en este módulo
    f_salida = now.strftime("%d/%m/%Y")
    h_salida = now.strftime("%H:%M:%S")
    f_llegada = now.strftime("%d/%m/%Y")
    h_llegada = now.strftime("%H:%M:%S")

    st.write(f"**Fecha/Hora Salida (Automática):** {f_salida} {h_salida}")
    st.write(f"**Fecha/Hora Llegada (Automática):** {f_llegada} {h_llegada}")

    circuito = f"{origen[:3]}-{plaza_actual[:3]}".upper()
    st.info(f"Circuito generado: **{circuito}**")

    operador = st.selectbox("Operador", OPERADORES)
    no_eco = st.text_input("No. Económico")
    folio = st.text_input("Folio del Circuito")
    observaciones = st.text_area(
        "Comentarios / Observaciones", value="Sin Incidencias"
    )

    submitted_directo = st.form_submit_button("Guardar Registro Completo")

    if submitted_directo:
      df = pd.read_excel(EXCEL_FILE, dtype=str)
      df.fillna("", inplace=True)

      nueva_fila = {
          "ORIGEN": origen,
          "FECHA SALIDA": f_salida,
          "HORA SALIDA": h_salida,
          "CIRCUITO": circuito,
          "OPERADOR": operador,
          "NO. ECO": str(no_eco),
          "FOLIO": str(folio),
          "DESTINO": plaza_actual,
          "FECHA LLEGADA DESTINO FINAL": f_llegada,
          "HORA LLEGADA DESTINO FINAL": h_llegada,
          "COMENTARIOS/OBSERVACIONES": observaciones,
      }
      df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
      df.to_excel(EXCEL_FILE, index=False)
      st.success("¡Registro completo guardado en una sola línea en el Excel!")
      st.rerun()

# ---------------------------------------------------------
# 4. CAPTURAR SALIDA CON LLEGADA YA REGISTRADA
# ---------------------------------------------------------
elif menu == "Salida con Llegada previa":
  st.header(f"Completar Salida (Destino ya registró llegada) - Plaza: {plaza_actual}")
  df = pd.read_excel(EXCEL_FILE, dtype=str)
  df.fillna("", inplace=True)

  # Buscar registros donde el ORIGEN sea la plaza actual pero la FECHA SALIDA esté vacía o no registrada
  # (O registros creados inicialmente por destino donde origen deba complementar)
  pendientes_salida = df[
      (df["ORIGEN"] == plaza_actual)
      & (
          df["FECHA SALIDA"].isna()
          | (df["FECHA SALIDA"] == "")
      )
  ]

  if pendientes_salida.empty:
    st.info("No hay salidas pendientes de completar para tu plaza.")
  else:
    st.write("Selecciona el circuito registrado por el destino para complementar tu salida:")
    folios_disp = pendientes_salida["FOLIO"].astype(str).tolist()
    folio_sel = st.selectbox("Folio con Llegada Previa", folios_disp)

    info_reg = pendientes_salida[
        pendientes_salida["FOLIO"].astype(str) == folio_sel
    ].iloc[0]
    st.markdown("### Datos registrados por el Destino:")
    st.write(f"- **Destino:** {info_reg['DESTINO']}")
    st.write(f"- **Llegada registrada:** {info_reg['FECHA LLEGADA DESTINO FINAL']} a las {info_reg['HORA LLEGADA DESTINO FINAL']}")

    with st.form("form_completar_salida"):
      now = datetime.now()
      f_salida_auto = now.strftime("%d/%m/%Y")
      h_salida_auto = now.strftime("%H:%M:%S")

      st.write(f"**Fecha de Salida (Automática):** {f_salida_auto}")
      st.write(f"**Hora de Salida (Automática):** {h_salida_auto}")

      operador = st.selectbox("Operador", OPERADORES)
      no_eco = st.text_input("No. Económico")

      submitted_completo = st.form_submit_button("Guardar Salida")

      if submitted_completo:
        idx = df[df["FOLIO"].astype(str) == folio_sel].index[0]
        df.loc[idx, "FECHA SALIDA"] = f_salida_auto
        df.loc[idx, "HORA SALIDA"] = h_salida_auto
        df.loc[idx, "OPERADOR"] = operador
        df.loc[idx, "NO. ECO"] = str(no_eco)

        df.to_excel(EXCEL_FILE, index=False)
        st.success(f"¡Salida del folio {folio_sel} completada con éxito!")
        st.rerun()

# Visualizador rápido
with st.expander("Ver base de datos actual en Excel"):
  try:
    df_view = pd.read_excel(EXCEL_FILE)
    st.dataframe(df_view)
  except:
    st.write("Aún no hay datos.")