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


# Conectar y leer datos de la hoja maestra
try:
  sheet = conectar_gsheets().sheet1
  data = sheet.get_all_records()
  df = pd.DataFrame(data)
  if df.empty:
    columns = [
        "OPERADOR",
        "NO. ECO",
        "TIPO",
        "ORIGEN",
        "PLAZA INTERMEDIA",
        "DESTINO",
        "FOLIO",
        "FECHA SALIDA ORIGEN",
        "HORA SALIDA ORIGEN",
        "FECHA LLEGADA INTERMEDIA",
        "HORA LLEGADA INTERMEDIA",
        "FECHA SALIDA INTERMEDIA",
        "HORA SALIDA INTERMEDIA",
        "FECHA LLEGADA DESTINO",
        "HORA LLEGADA DESTINO",
        "OBSERVACIONES / PERCANCES",
    ]
    df = pd.DataFrame(columns=columns)
except Exception as e:
  st.error(
      f"Error al conectar con Google Sheets. Verifica tus Secrets o enlace: {e}"
  )
  df = pd.DataFrame()

df.fillna("", inplace=True)

# Listas oficiales actualizadas
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

st.title("Control de Circuitos - Portal del Operador")

# 1. Identificación del Operador
col_id1, col_id2 = st.columns(2)
with col_id1:
  operador_actual = st.selectbox(
      "Selecciona tu Nombre (Operador):", OPERADORES_OFICIALES
  )
with col_id2:
  unidad_actual = st.selectbox(
      "Selecciona tu Unidad (No. Económico):", UNIDADES_ECONOMICAS
  )

st.markdown("---")


def obtener_tiempo_mexico():
  ahora_mexico = datetime.utcnow() - timedelta(hours=6)
  return ahora_mexico.strftime("%d/%m/%Y"), ahora_mexico.strftime("%H:%M:%S")


def guardar_en_gsheets(dataframe):
  sheet.clear()
  sheet.update(
      [dataframe.columns.values.tolist()] + dataframe.values.tolist()
  )


# Validar si el operador tiene viajes pendientes de cerrar
if operador_actual:
  if not df.empty:
    mis_pendientes = df[
        (df["OPERADOR"] == operador_actual)
        & (
            (df["FECHA LLEGADA DESTINO"] == "")
            | (df["FECHA LLEGADA DESTINO"].isna())
        )
    ]
    if not mis_pendientes.empty:
      st.warning(
          f"⚠️ Tienes **{len(mis_pendientes)} viaje(s) pendiente(s)** de"
          " completar o cerrar. Revisa la sección de seguimiento abajo."
      )

# Botones de navegación principales
st.markdown("### Menú de Operación")
col_b1, col_b2 = st.columns(2)

if "menu_operador" not in st.session_state:
  st.session_state.menu_operador = "Iniciar Nuevo Viaje"

if col_b1.button("🚀 Iniciar Nuevo Viaje", use_container_width=True):
  st.session_state.menu_operador = "Iniciar Nuevo Viaje"
if col_b2.button(
    "📥 Dar Seguimiento / Cerrar Pendientes", use_container_width=True
):
  st.session_state.menu_operador = "Dar Seguimiento / Cerrar Pendientes"

modo = st.session_state.menu_operador
st.markdown(f"**Sección actual:** {modo}")
st.markdown("---")

# ---------------------------------------------------------
# OPCIÓN A: INICIAR NUEVO VIAJE (DIRECTO O ENLACE)
# ---------------------------------------------------------
if modo == "Iniciar Nuevo Viaje":
  st.header("Iniciar Nuevo Circuito")

  if not operador_actual or not unidad_actual:
    st.warning(
        "Por favor selecciona primero tu **Nombre** y **Unidad** en la parte"
        " superior."
    )
  else:
    tipo_circuito = st.radio(
        "Selecciona el tipo de circuito:", ["Directo", "Enlace"]
    )

    with st.form("form_nuevo_viaje"):
      f_salida, h_salida = obtener_tiempo_mexico()

      if tipo_circuito == "Directo":
        st.subheader("Ruta Directa")
        origen = st.selectbox("Origen", PLAZAS)
        destino = st.selectbox(
            "Destino", [p for p in PLAZAS if p != origen]
        )
        plaza_intermedia = ""

      else:  # Enlace / Escalas
        st.subheader("Ruta con Enlace (Escala)")
        origen = st.selectbox("Origen", PLAZAS)
        plaza_intermedia = st.selectbox(
            "Plaza Intermedia (Escala)", [p for p in PLAZAS if p != origen]
        )
        destino = st.selectbox(
            "Destino Final",
            [p for p in PLAZAS if p != origen and p != plaza_intermedia],
        )

      folio = st.text_input("Folio del Circuito (Ej: DQ00032584)")

      st.write(f"**Fecha de Salida (Automática):** {f_salida}")
      st.write(f"**Hora de Salida (Automática):** {h_salida}")

      submitted_viaje = st.form_submit_button("Registrar Salida de Origen")

      if submitted_viaje:
        if not folio:
          st.error("Por favor ingresa el folio del circuito.")
        else:
          if (
              not df.empty
              and not df[df["FOLIO"].astype(str) == str(folio)].empty
          ):
            st.error("¡El folio ya se encuentra registrado en el sistema!")
          else:
            nueva_fila = {
                "OPERADOR": operador_actual,
                "NO. ECO": str(unidad_actual),
                "TIPO": tipo_circuito,
                "ORIGEN": origen,
                "PLAZA INTERMEDIA": plaza_intermedia,
                "DESTINO": destino,
                "FOLIO": str(folio),
                "FECHA SALIDA ORIGEN": f_salida,
                "HORA SALIDA ORIGEN": h_salida,
                "FECHA LLEGADA INTERMEDIA": "",
                "HORA LLEGADA INTERMEDIA": "",
                "FECHA SALIDA INTERMEDIA": "",
                "HORA SALIDA INTERMEDIA": "",
                "FECHA LLEGADA DESTINO": "",
                "HORA LLEGADA DESTINO": "",
                "OBSERVACIONES / PERCANCES": "",
            }
            df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            guardar_en_gsheets(df)
            st.success(
                f"¡Salida del circuito registrada con éxito! Folio: {folio}"
            )
            st.rerun()

# ---------------------------------------------------------
# OPCIÓN B: SEGUIMIENTO Y CIERRE DE PENDIENTES
# ---------------------------------------------------------
elif modo == "Dar Seguimiento / Cerrar Pendientes":
  st.header("Mis Viajes en Ruta / Pendientes de Cerrar")

  if not operador_actual:
    st.warning("Selecciona tu nombre en la parte superior para ver tus viajes.")
  else:
    if df.empty:
      mis_viajes = pd.DataFrame()
    else:
      mis_viajes = df[
          (df["OPERADOR"] == operador_actual)
          & (
              (df["FECHA LLEGADA DESTINO"] == "")
              | (df["FECHA LLEGADA DESTINO"].isna())
          )
      ]

    if mis_viajes.empty:
      st.success(
          "✅ ¡No tienes viajes pendientes! Todos tus circuitos están cerrados."
      )
    else:
      folios_activos = mis_viajes["FOLIO"].astype(str).tolist()
      folio_elegido = st.selectbox(
          "Selecciona el Folio que deseas actualizar o cerrar:", folios_activos
      )

      viaje_info = mis_viajes[
          mis_viajes["FOLIO"].astype(str) == folio_elegido
      ].iloc[0]
      tipo_c = viaje_info["TIPO"]

      st.markdown("---")
      st.markdown(f"### Detalle del Viaje (Folio: {folio_elegido})")
      st.write(f"- **Tipo:** {tipo_c}")
      st.write(
          f"- **Ruta:** {viaje_info['ORIGEN']} ➡️ "
          + (
              f"{viaje_info['PLAZA INTERMEDIA']} ➡️ "
              if tipo_c == "Enlace"
              else ""
          )
          + f"{viaje_info['DESTINO']}"
      )
      st.write(
          f"- **Salida de Origen:** {viaje_info['FECHA SALIDA ORIGEN']} a las"
          f" {viaje_info['HORA SALIDA ORIGEN']}"
      )

      f_now, h_now = obtener_tiempo_mexico()

      # FORMULARIO SEGÚN EL TIPO DE CIRCUITO
      with st.form("form_seguimiento"):
        observaciones = st.text_area(
            "Observaciones / Percances en el trayecto",
            value=viaje_info["OBSERVACIONES / PERCANCES"],
        )

        # CASO 1: CIRCUITO DIRECTO (Solo requiere marcar llegada final)
        if tipo_c == "Directo":
          st.markdown("#### Registrar Llegada a Destino")
          st.write(f"**Fecha de Llegada (Automática):** {f_now}")
          st.write(f"**Hora de Llegada (Automática):** {h_now}")

          cerrar_directo = st.form_submit_button("Cerrar Circuito Directo")

          if cerrar_directo:
            idx = df[df["FOLIO"].astype(str) == folio_elegido].index[0]
            df.loc[idx, "FECHA LLEGADA DESTINO"] = f_now
            df.loc[idx, "HORA LLEGADA DESTINO"] = h_now
            df.loc[idx, "OBSERVACIONES / PERCANCES"] = observaciones
            guardar_en_gsheets(df)
            st.success(
                f"¡Circuito {folio_elegido} cerrado y guardado con éxito!"
            )
            st.rerun()

        # CASO 2: CIRCUITO ENLACE (Tiene etapas intermedias)
        else:
          etapa_actual = st.radio(
              "¿Qué etapa deseas registrar?",
              [
                  "1. Registrar paso por Plaza Intermedia (Escala)",
                  "2. Registrar Llegada a Destino Final (Cerrar Viaje)",
              ],
          )

          if "1." in etapa_actual:
            st.markdown(
                f"#### Registro en Plaza Intermedia:"
                f" {viaje_info['PLAZA INTERMEDIA']}"
            )
            registrar_escala = st.form_submit_button(
                "Guardar Llegada y Salida de Escala"
            )

            if registrar_escala:
              idx = df[df["FOLIO"].astype(str) == folio_elegido].index[0]
              df.loc[idx, "FECHA LLEGADA INTERMEDIA"] = f_now
              df.loc[idx, "HORA LLEGADA INTERMEDIA"] = h_now
              df.loc[idx, "FECHA SALIDA INTERMEDIA"] = f_now
              df.loc[idx, "HORA SALIDA INTERMEDIA"] = h_now
              df.loc[idx, "OBSERVACIONES / PERCANCES"] = observaciones
              guardar_en_gsheets(df)
              st.success(
                  f"¡Paso por plaza intermedia registrado para el folio"
                  f" {folio_elegido}!"
              )
              st.rerun()
          else:
            st.markdown(
                f"#### Cierre de Viaje en Destino Final:"
                f" {viaje_info['DESTINO']}"
            )
            cerrar_enlace = st.form_submit_button("Cerrar Circuito por Enlace")

            if cerrar_enlace:
              idx = df[df["FOLIO"].astype(str) == folio_elegido].index[0]
              df.loc[idx, "FECHA LLEGADA DESTINO"] = f_now
              df.loc[idx, "HORA LLEGADA DESTINO"] = h_now
              df.loc[idx, "OBSERVACIONES / PERCANCES"] = observaciones
              guardar_en_gsheets(df)
              st.success(
                  f"¡El circuito en enlace {folio_elegido} ha sido cerrado"
                  " exitosamente!"
              )
              st.rerun()

# ---------------------------------------------------------
# DESCARGA DE DATOS (GOOGLE SHEETS MAESTRA)
# ---------------------------------------------------------
st.markdown("---")
with st.expander("📂 Ver / Descargar Base de Datos Maestra"):
  st.dataframe(df)
  csv_data = df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="Descargar Base de Datos en CSV",
      data=csv_data,
      file_name="control_circuitos_maestro.csv",
      mime="text/csv",
  )
