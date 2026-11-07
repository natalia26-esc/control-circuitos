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
        "FECHA SALIDA ORIGEN",
        "HORA SALIDA ORIGEN",
        "FECHA LLEGADA INTERMEDIA",
        "HORA LLEGADA INTERMEDIA",
        "FECHA SALIDA INTERMEDIA",
        "HORA SALIDA INTERMEDIA",
        "FECHA LLEGADA DESTINO",
        "HORA LLEGADA DESTINO",
        "OBSERVACIONES ESCALA",
        "OBSERVACIONES DESTINO",
    ]
    df = pd.DataFrame(columns=columns)
except Exception as e:
  st.error(
      f"Error al conectar con Google Sheets. Verifica tus Secrets o enlace: {e}"
  )
  df = pd.DataFrame()

df.fillna("", inplace=True)

# Listas oficiales de Plazas
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

# Listas oficiales (Nombre y Puesto)
OPERADORES_OFICIALES = [
    "",
    "Jose Angel Ramirez Jimenez - OPERADOR TORTON",
    "Jorge Fabian Ortiz Lopez - OPERADOR SENCILLO",
    "Ruben Magaña Ramirez - OPERADOR FULL",
    "Rodiberto Vidal Rivera - OPERADOR FULL",
    "Francisco Jose Dominguez Gomez - OPERADOR TORTON",
    "Alejandro Ramirez Herrera - OPERADOR FULL",
    "Jose Antonio Porcayo - OPERADOR SENCILLO",
    "Jose Antonio Porcayo Almanzar - OPERADOR SENCILLO",
    "Jesus Horacio de Leon Romero - OPERADOR FULL",
    "Jose Manuel Salazar Salcido - OPERADOR TORTON",
    "Mario Garcia Sanchez - OPERADOR FULL",
    "Zair Diego Campos Mares - OPERADOR FULL",
    "Rodrigo Navarro Hernandez - OPERADOR FULL",
    "Carlos Martinez Hernandez - OPERADOR FULL",
    "Gabriel Poxtan Temix - OPERADOR FULL",
    "Alejandro Guadarrama Zamora - OPERADOR SENCILLO",
]

# Unidades económicas y su serie de chasis
UNIDADES_ECONOMICAS = [
    "",
    "388 (Chasis: 3WKAD40X8JF872041)",
    "471 (Chasis: 3WKYD40X9LF511290)",
    "472 (Chasis: 3WKYD40X0LF511291)",
    "503 (Chasis: 3WKZDP0XXLF516052)",
    "540 (Chasis: 3WKYD40X3TF500818)",
    "543 (Chasis: 3WKYD40X6TF502708)",
    "470 (Chasis: 3WKZD40X1LF513555)",
    "530 (Chasis: 3WKYDP0X1SF554750)",
    "539 (Chasis: 3BK5LJ9X6TF403172)",
    "508 (Chasis: 3HAEVMMR6PL162411)",
    "412 (Chasis: 3BKHKN9X6KF316880)",
    "435 (Chasis: 3BKHKN9X2KF317783)",
    "538 (Chasis: 3BKHKN9X4TF403171)",
]

st.title("Control de Circuitos - Portal del Operador")

# 1. Identificación del Operador
col_id1, col_id2 = st.columns(2)
with col_id1:
  operador_actual = st.selectbox(
      "Selecciona tu Nombre y Puesto:", OPERADORES_OFICIALES
  )
with col_id2:
  unidad_actual = st.selectbox(
      "Selecciona tu Unidad y Chasis:", UNIDADES_ECONOMICAS
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
          f"⚠️ Tienes **{len(mis_pendientes)} viaje(s) en curso** pendiente(s)"
          " de cerrar. Ve a la sección de seguimiento."
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
    viaje_abierto = (
        False
        if df.empty
        else not df[
            (df["OPERADOR"] == operador_actual)
            & (
                (df["FECHA LLEGADA DESTINO"] == "")
                | (df["FECHA LLEGADA DESTINO"].isna())
            )
        ].empty
    )

    if viaje_abierto:
      st.error(
          "⛔ Ya tienes un viaje en curso sin cerrar. Debes concluirlo en la"
          " sección de 'Dar Seguimiento / Cerrar Pendientes' antes de iniciar"
          " uno nuevo."
      )
    else:
      # SACAMOS EL TIPO DE CIRCUITO FUERA DEL FORM PARA QUE ACTUALICE EN TIEMPO REAL
      tipo_circuito = st.radio(
          "Selecciona el tipo de circuito:", ["Directo", "Enlace"]
      )
      
      with st.form("form_inicio", clear_on_submit=True):
        f_salida, h_salida = obtener_tiempo_mexico()

        if tipo_circuito == "Directo":
          st.subheader("Ruta Directa")
          origen = st.selectbox("Origen", PLAZAS)
          destino = st.selectbox(
              "Destino", [p for p in PLAZAS if p != origen]
          )
          plaza_intermedia = ""
        else:
          st.subheader("Ruta con Enlace (Escala)")
          origen = st.selectbox("Origen", PLAZAS)
          plaza_intermedia = st.selectbox(
              "Plaza Intermedia (Escala)",
              [p for p in PLAZAS if p != origen]
          )
          destino = st.selectbox(
              "Destino Final",
              [p for p in PLAZAS if p != origen and p != plaza_intermedia]
          )

        st.write(f"**Fecha de Salida (Automática):** {f_salida}")
        st.write(f"**Hora de Salida (Automática):** {h_salida}")

        if st.form_submit_button("Registrar Salida de Origen"):
          nueva_fila = {
              "OPERADOR": operador_actual,
              "NO. ECO": str(unidad_actual),
              "TIPO": tipo_circuito,
              "ORIGEN": origen,
              "PLAZA INTERMEDIA": plaza_intermedia,
              "DESTINO": destino,
              "FECHA SALIDA ORIGEN": f_salida,
              "HORA SALIDA ORIGEN": h_salida,
              "FECHA LLEGADA INTERMEDIA": "",
              "HORA LLEGADA INTERMEDIA": "",
              "FECHA SALIDA INTERMEDIA": "",
              "HORA SALIDA INTERMEDIA": "",
              "FECHA LLEGADA DESTINO": "",
              "HORA LLEGADA DESTINO": "",
              "OBSERVACIONES ESCALA": "",
              "OBSERVACIONES DESTINO": "",
          }
          df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
          guardar_en_gsheets(df)
          st.success(
              "✅ ¡GUARDADO EXITOSO! Salida del circuito registrada"
              " correctamente en la base de datos."
          )

# ---------------------------------------------------------
# OPCIÓN B: SEGUIMIENTO Y CIERRE DE PENDIENTES
# ---------------------------------------------------------
elif modo == "Dar Seguimiento / Cerrar Pendientes":
  st.header("Mi Viaje en Ruta / Pendiente de Cerrar")

  if not operador_actual:
    st.warning("Selecciona tu nombre en la parte superior para ver tu viaje.")
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
      viaje_info = mis_viajes.iloc[0]
      tipo_c = viaje_info["TIPO"]
      idx_viaje = mis_viajes.index[0]

      st.markdown("---")
      st.markdown("### Detalle de tu Viaje Actual")
      st.write(f"- **Tipo de Circuito:** {tipo_c}")
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

      # CASO 1: CIRCUITO DIRECTO
      if tipo_c == "Directo":
        f_now, h_now = obtener_tiempo_mexico()
        st.markdown("#### Registrar Llegada a Destino")
        st.write(f"**Fecha de Llegada (Automática):** {f_now}")
        st.write(f"**Hora de Llegada (Automática):** {h_now}")

        with st.form("form_cierre_directo", clear_on_submit=True):
            obs_destino_dir = st.text_area(
                "Observaciones / Percances en el trayecto (Destino Final)",
                value="" 
            )

            if st.form_submit_button("Cerrar Circuito Directo"):
                obs_previa = str(viaje_info.get("OBSERVACIONES DESTINO", ""))
                nueva_obs = f"{obs_previa} | {obs_destino_dir}".strip(" |") if obs_destino_dir else obs_previa

                df.loc[idx_viaje, "FECHA LLEGADA DESTINO"] = f_now
                df.loc[idx_viaje, "HORA LLEGADA DESTINO"] = h_now
                df.loc[idx_viaje, "OBSERVACIONES DESTINO"] = nueva_obs
                guardar_en_gsheets(df)
                st.success(
                    "✅ ¡GUARDADO EXITOSO! Circuito directo cerrado y guardado"
                    " correctamente."
                )

      # CASO 2: CIRCUITO ENLACE
      else:
        llego_intermedia = (
            str(viaje_info["FECHA LLEGADA INTERMEDIA"]).strip() != ""
        )

        if not llego_intermedia:
          st.markdown(
              f"#### 📍 Paso 1: Registrar LLEGADA a Plaza Intermedia:"
              f" {viaje_info['PLAZA INTERMEDIA']}"
          )
          f_lleg_int, h_lleg_int = obtener_tiempo_mexico()
          st.write(
              f"**Fecha y Hora de Arribo a Escala (Automática):**"
              f" {f_lleg_int} - {h_lleg_int}"
          )

          with st.form("form_llegada_escala", clear_on_submit=True):
              obs_escala = st.text_area(
                  f"Observaciones al llegar a la escala ({viaje_info['PLAZA INTERMEDIA']})",
                  value="" 
              )

              if st.form_submit_button("Guardar Llegada a Escala"):
                df.loc[idx_viaje, "FECHA LLEGADA INTERMEDIA"] = f_lleg_int
                df.loc[idx_viaje, "HORA LLEGADA INTERMEDIA"] = h_lleg_int
                df.loc[idx_viaje, "OBSERVACIONES ESCALA"] = obs_escala
                guardar_en_gsheets(df)
                st.success(
                    f"✅ ¡GUARDADO EXITOSO! Llegada a"
                    f" {viaje_info['PLAZA INTERMEDIA']} registrada."
                )

        else:
          salio_intermedia = (
              str(viaje_info["FECHA SALIDA INTERMEDIA"]).strip() != ""
          )

          st.markdown(
              f"✅ **Llegada a Escala ya registrada:**"
              f" {viaje_info['FECHA LLEGADA INTERMEDIA']} a las"
              f" {viaje_info['HORA LLEGADA INTERMEDIA']}"
          )
          if viaje_info["OBSERVACIONES ESCALA"]:
            st.info(
                f"📝 Nota en escala: {viaje_info['OBSERVACIONES ESCALA']}"
            )

          if not salio_intermedia:
            st.markdown(
                f"#### 🚀 Paso 2: Registrar SALIDA de Plaza Intermedia:"
                f" {viaje_info['PLAZA INTERMEDIA']}"
            )
            f_sal_int, h_sal_int = obtener_tiempo_mexico()
            st.write(
                f"**Fecha y Hora de Salida de Escala (Automática):**"
                f" {f_sal_int} - {h_sal_int}"
            )

            with st.form("form_salida_escala", clear_on_submit=True):
                obs_salida_escala = st.text_area(
                    "Observaciones al reanudar la marcha desde la escala",
                    value="" 
                )

                if st.form_submit_button("Guardar Salida de Escala"):
                  obs_previa = str(viaje_info.get("OBSERVACIONES ESCALA", ""))
                  nueva_obs = f"{obs_previa} | Salida: {obs_salida_escala}" if obs_salida_escala else obs_previa
                  
                  df.loc[idx_viaje, "FECHA SALIDA INTERMEDIA"] = f_sal_int
                  df.loc[idx_viaje, "HORA SALIDA INTERMEDIA"] = h_sal_int
                  df.loc[idx_viaje, "OBSERVACIONES ESCALA"] = nueva_obs
                  guardar_en_gsheets(df)
                  st.success("✅ ¡GUARDADO EXITOSO! Salida de escala registrada.")

          else:
            st.markdown(
                f"✅ **Salida de Escala ya registrada:**"
                f" {viaje_info['FECHA SALIDA INTERMEDIA']} a las"
                f" {viaje_info['HORA SALIDA INTERMEDIA']}"
            )
            st.markdown(
                f"#### 🏁 Paso 3: Registrar LLEGADA al Destino Final:"
                f" {viaje_info['DESTINO']}"
            )
            f_lleg_fin, h_lleg_fin = obtener_tiempo_mexico()
            st.write(
                f"**Fecha y Hora de Llegada a Destino Final (Automática):**"
                f" {f_lleg_fin} - {h_lleg_fin}"
            )

            with st.form("form_cierre_enlace", clear_on_submit=True):
                obs_destino_enlace = st.text_area(
                    "Observaciones / Percances al llegar al Destino Final",
                    value="" 
                )

                if st.form_submit_button("Cerrar Viaje en Destino Final"):
                  df.loc[idx_viaje, "FECHA LLEGADA DESTINO"] = f_lleg_fin
                  df.loc[idx_viaje, "HORA LLEGADA DESTINO"] = h_lleg_fin
                  df.loc[idx_viaje, "OBSERVACIONES DESTINO"] = obs_destino_enlace
                  guardar_en_gsheets(df)
                  st.success(
                      "✅ ¡GUARDADO EXITOSO! El circuito de enlace ha sido"
                      " cerrado por completo."
                  )

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
