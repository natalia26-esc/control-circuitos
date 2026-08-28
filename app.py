from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configuración de credenciales de Google Sheets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def conectar_gsheets():
  secrets_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(secrets_dict, scopes=scope)
  client = gspread.authorize(creds)
  return client.open_by_url(st.secrets["sheet_url"])


# Conectar y leer datos
try:
  sheet = conectar_gsheets().sheet1
  data = sheet.get_all_records()
  df = pd.DataFrame(data)
  if df.empty:
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
except Exception as e:
  st.error(
      f"Error al conectar con Google Sheets. Verifica tus Secrets o enlace: {e}"
  )
  df = pd.DataFrame()

df.fillna("", inplace=True)

# Listas oficiales actualizadas con las nuevas plazas
PLAZAS = [
    "MÉRIDA",
    "CANCÚN",
    "VILLAHERMOSA",
    "VERACRUZ",
    "TOLUCA",
    "TUXTLA",
    "COATZACOALCOS",
    "CIUDAD DEL CARMEN",
]

OPERADORES_OFICIALES = [
    "",
    "RAUL ADEMAR ESTRELLA POOT",
    "JORGE IVAN BRITO COUOH",
    "ALEXIS OMAR DZIB DZIB",
    "RIGOBERTO DZIB OXTE",
    "SANTIAGO GIOBERTI CRUZ CANO",
    "CARLOS HERNANDEZ FERNANDEZ",
    "FRANCISCO JOSE DOMINGUEZ GOMEZ",
    "JORGE FABIAN ORTIZ LOPEZ",
    "ALEJANDRO RAMIREZ HERRERA",
    "JOSE ANGEL RAMIREZ JIMENEZ",
    "DEINER EFRAIN FRIAS CARDONA",
    "JOSE MANUEL SALAZAR SALCIDO",
    "EDUARDO HERNANDEZ HERNANDEZ",
    "LEON LUIS FERNANDO CENTENO DE",
    "RODOLFO JULIAN MALDONADO AGUILAR",
    "JUSTINO VARGAS GUILLEN",
    "EBER JOSHUAN SOLIS ALVARADO",
    "RODIBERTO VIDAL RIVERA",
    "GASPAR SOLIS JAIME",
    "ROGELIO GAEL MARTIN CIME",
    "CRISTHIAN DANIEL DE JESUS EK BAUTISTA",
    "GLEINER RAMSES RODRIGUEZ CHAN",
    "IRVING ALEJANDRO CANTO CHAN",
    "JAVIER EDUARDO FRANCO DZUL",
    "JORGE BERNABE MOGUEL CORREA",
    "ARMIN GUADALUPE DZUL ROSALES",
    "OSCAR RENE GOMEZ PAT",
    "HENRY HAFID CANUL AKE",
    "JOSE SEBASTIAN KU KU",
    "RICARDO EMMANUEL LIZAMA ALBORNOZ",
    "LUIS ENRIQUE LORIA CAMPOS",
    "JARED ARZATE BUENROSTRO",
    "SERAFIN GONZALES VERTIZ",
    "EDUARDO TZAB GONZALEZ",
    "DAVID MORALES BAJE",
    "ROMERO JESUS HORACIO DE LEON",
    "RUBEN MAGAÑA RAMIREZ",
    "RAFAEL SANCHEZ MARTINEZ",
    "IVAN GARCIA SANCHEZ",
    "JOSE ANTONIO PORCAYO ALMANZAR",
    "RODRIGO MORALES BECERRIL",
    "GELASIO ALBERTO GUADARRAMA GUADARRAMA",
    "LUIS ENRIQUE CORZO CAMILO",
    "AZIEL ACERO COELLO",
    "JORGE VELAZQUEZ MEJIA",
    "ALBERTO GABRIEL ORTIZ CHACON",
    "OSCAR GONZALEZ HERNANDEZ",
    "ANGEL DAVID RIVERA CORTES",
    "FREDY VILLEGAS ALEJANDRO",
    "LUIS EDUARDO MARTINEZ MENDEZ",
    "OTILIO MENDEZ ESCOBAR",
    "CARLOS ALFREDO DIAZ COYADO",
    "LUIS ANGEL ARROYO PECH",
    "ARMIN NEFTALI CARRILLO SANCHEZ",
    "CARLOS IGNACIO CASTILLO CORDERO",
    "ALEJANDRO GUADARRAMA GONZALEZ",
    "NOE SALDIVAR FLORES",
    "MOISES FERNANDEZ ESTRADA",
]

UNIDADES_ECONOMICAS = [
    "",
    "541",
    "447",
    "527",
    "479",
    "506",
    "542",
    "371",
    "486",
    "435",
    "534",
    "539",
    "504",
    "538",
    "522",
    "480",
    "441",
    "524",
    "535",
    "230",
    "540",
    "419",
    "440",
    "453",
    "536",
    "378",
    "1250",
    "401",
    "525",
    "418",
    "510",
    "420",
    "509",
    "508",
    "408",
    "498",
    "423",
    "537",
    "482",
    "513",
    "500",
    "543",
    "470",
    "503",
    "530",
    "471",
    "466",
    "505",
    "488",
    "489",
    "429",
    "373",
    "499",
    "399",
    "386",
    "477",
    "415",
    "388",
    "517",
    "514",
    "451",
    "458",
    "472",
    "476",
    "515",
    "507",
    "412",
    "490",
    "512",
    "528",
]

st.title("Control de Circuitos entre Plazas (En Línea)")

plaza_actual = st.selectbox("Selecciona tu Plaza Actual:", PLAZAS)
st.markdown("---")

# MENÚ FIJO CON BOTONES
st.markdown("### Menú de Opciones")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

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


def obtener_tiempo_mexico():
  ahora_mexico = datetime.utcnow() - timedelta(hours=6)
  return ahora_mexico.strftime("%d/%m/%Y"), ahora_mexico.strftime("%H:%M:%S")


def guardar_en_gsheets(dataframe):
  sheet.clear()
  sheet.update(
      [dataframe.columns.values.tolist()] + dataframe.values.tolist()
  )


# 1. REGISTRAR SALIDA
if menu == "Registrar Salida":
  st.header(f"Registrar Salida desde: {plaza_actual}")

  with st.form("form_salida"):
    fecha_salida, hora_salida = obtener_tiempo_mexico()
    st.write(f"**Fecha de Salida (Automática):** {fecha_salida}")
    st.write(f"**Hora de Salida (Automática):** {hora_salida}")

    destinos_posibles = [p for p in PLAZAS if p != plaza_actual]
    destino = st.selectbox("Plaza Destino", destinos_posibles)

    circuito = f"{plaza_actual[:3]}-{destino[:3]}".upper()
    st.info(f"Circuito generado automáticamente: **{circuito}**")

    operador = st.selectbox("Operador", OPERADORES_OFICIALES)
    no_eco = st.selectbox("No. Económico", UNIDADES_ECONOMICAS)
    folio = st.text_input("Folio del Circuito (Ej: DQ00032584)")

    submitted = st.form_submit_button("Guardar Salida")

    if submitted:
      if not folio:
        st.error("Por favor completa el folio.")
      elif not operador or not no_eco:
        st.error("Por favor selecciona un operador y un número económico.")
      else:
        if (
            not df.empty
            and not df[df["FOLIO"].astype(str) == str(folio)].empty
        ):
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
          guardar_en_gsheets(df)
          st.success(
              f"¡Salida del folio {folio} registrada correctamente hacia"
              f" {destino}!"
          )
          st.rerun()

# 2. REGISTRAR LLEGADA (PENDIENTES)
elif menu == "Registrar Llegada":
  st.header(f"Registrar Llegada en: {plaza_actual}")

  if df.empty:
    pendientes = pd.DataFrame()
  else:
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
      fecha_llegada, hora_llegada = obtener_tiempo_mexico()
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

        guardar_en_gsheets(df)
        st.success(
            f"¡Llegada del folio {folio_seleccionado} registrada con éxito!"
        )
        st.rerun()

# 3. CAPTURAR LLEGADA SIN SALIDA PREVIA
elif menu == "Llegada sin Salida":
  st.header(f"Registro Directo (Sin Salida Previa) en: {plaza_actual}")

  with st.form("form_directo"):
    origen = st.selectbox(
        "Plaza de Origen", [p for p in PLAZAS if p != plaza_actual]
    )

    f_ahora, h_ahora = obtener_tiempo_mexico()
    st.markdown(
        "*Nota: La fecha y hora de salida se dejarán vacías para que el origen"
        " las complemente después.*"
    )
    st.write(f"**Fecha de Llegada (Automática):** {f_ahora}")
    st.write(f"**Hora de Llegada (Automática):** {h_ahora}")

    circuito = f"{origen[:3]}-{plaza_actual[:3]}".upper()
    st.info(f"Circuito generado: **{circuito}**")

    operador = st.selectbox("Operador", OPERADORES_OFICIALES)
    no_eco = st.selectbox("No. Económico", UNIDADES_ECONOMICAS)
    folio = st.text_input("Folio del Circuito")
    observaciones = st.text_area(
        "Comentarios / Observaciones", value="Sin Incidencias"
    )

    submitted_directo = st.form_submit_button("Guardar Registro de Llegada")

    if submitted_directo:
      if not folio:
        st.error("Por favor completa el folio.")
      elif not operador or not no_eco:
        st.error("Por favor selecciona un operador y un número económico.")
      else:
        nueva_fila = {
            "ORIGEN": origen,
            "FECHA SALIDA": "",
            "HORA SALIDA": "",
            "CIRCUITO": circuito,
            "OPERADOR": operador,
            "NO. ECO": str(no_eco),
            "FOLIO": str(folio),
            "DESTINO": plaza_actual,
            "FECHA LLEGADA DESTINO FINAL": f_ahora,
            "HORA LLEGADA DESTINO FINAL": h_ahora,
            "COMENTARIOS/OBSERVACIONES": observaciones,
        }
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        guardar_en_gsheets(df)
        st.success(
            "¡Llegada registrada con éxito! Quedará pendiente de complementar"
            " la salida en la plaza de origen."
        )
        st.rerun()

# 4. CAPTURAR SALIDA CON LLEGADA YA REGISTRADA
elif menu == "Salida con Llegada previa":
  st.header(
      f"Completar Salida (Destino ya registró llegada) - Plaza: {plaza_actual}"
  )

  if df.empty:
    pendientes_salida = pd.DataFrame()
  else:
    pendientes_salida = df[
        (df["ORIGEN"] == plaza_actual)
        & (df["FECHA SALIDA"].isna() | (df["FECHA SALIDA"] == ""))
    ]

  if pendientes_salida.empty:
    st.info(
        "No hay salidas pendientes de complementar para tu plaza (o el destino"
        " aún no registra la llegada)."
    )
  else:
    st.write(
        "Selecciona el circuito registrado por el destino para complementar"
        " tu salida:"
    )
    folios_disp = pendientes_salida["FOLIO"].astype(str).tolist()
    folio_sel = st.selectbox("Folio con Llegada Previa", folios_disp)

    info_reg = pendientes_salida[
        pendientes_salida["FOLIO"].astype(str) == folio_sel
    ].iloc[0]
    st.markdown("### Datos ya registrados por el Destino:")
    st.write(f"- **Destino:** {info_reg['DESTINO']}")
    st.write(f"- **Operador (Capturado por Destino):** {info_reg['OPERADOR']}")
    st.write(f"- **Económico (Capturado por Destino):** {info_reg['NO. ECO']}")
    st.write(
        f"- **Llegada registrada:** {info_reg['FECHA LLEGADA DESTINO FINAL']} a"
        f" las {info_reg['HORA LLEGADA DESTINO FINAL']}"
    )

    f_hoy, h_ahora = obtener_tiempo_mexico()
    st.markdown("#### Ingresa únicamente la Fecha y Hora de tu Salida:")

    f_salida_manual = st.text_input("Fecha de Salida (DD/MM/AAAA)", value=f_hoy)
    h_salida_manual = st.text_input(
        "Hora de Salida (HH:MM:SS)", value=h_ahora, key="input_hora_salida"
    )

    if st.button("Guardar Salida Completa"):
      idx = df[df["FOLIO"].astype(str) == folio_sel].index[0]
      df.loc[idx, "FECHA SALIDA"] = str(f_salida_manual).strip()
      df.loc[idx, "HORA SALIDA"] = str(h_salida_manual).strip()

      guardar_en_gsheets(df)
      st.success(f"¡Salida del folio {folio_sel} completada con éxito!")
      st.rerun()

# Visualizador rápido
with st.expander("Ver base de datos actual en Google Sheets"):
  st.dataframe(df)
