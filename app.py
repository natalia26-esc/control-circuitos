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

# ---------------------------------------------------------
# FUNCIÓN PARA CARGAR DATOS FRESCOS
# ---------------------------------------------------------
def cargar_datos():
    try:
        sheet = conectar_gsheets().sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            columns = [
                "OPERADOR", "NO. ECO", "TIPO", "ORIGEN", "PLAZA INTERMEDIA",
                "DESTINO", "FECHA SALIDA ORIGEN", "HORA SALIDA ORIGEN",
                "FECHA LLEGADA INTERMEDIA", "HORA LLEGADA INTERMEDIA",
                "FECHA SALIDA INTERMEDIA", "HORA SALIDA INTERMEDIA",
                "FECHA LLEGADA DESTINO", "HORA LLEGADA DESTINO",
                "OBSERVACIONES ESCALA", "OBSERVACIONES DESTINO"
            ]
            df = pd.DataFrame(columns=columns)
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        df = pd.DataFrame()
    
    df.fillna("", inplace=True)
    return df, sheet

# Cargar datos al inicio
df, sheet = cargar_datos()

# Listas oficiales de Plazas
PLAZAS = [
    "MÉRIDA", "CANCÚN", "VILLAHERMOSA", "VERACRUZ", "TOLUCA", "TUXTLA",
    "COATZACOALCOS", "CIUDAD DEL CARMEN",
]

# Listas oficiales (Nombre y Puesto)
OPERADORES_OFICIALES = [
    "", "Jose Angel Ramirez Jimenez - OPERADOR TORTON", "Jorge Fabian Ortiz Lopez - OPERADOR SENCILLO",
    "Ruben Magaña Ramirez - OPERADOR FULL", "Rodiberto Vidal Rivera - OPERADOR FULL",
    "Francisco Jose Dominguez Gomez - OPERADOR TORTON", "Alejandro Ramirez Herrera - OPERADOR FULL",
    "Jose Antonio Porcayo - OPERADOR SENCILLO", "Jose Antonio Porcayo Almanzar - OPERADOR SENCILLO",
    "Jesus Horacio de Leon Romero - OPERADOR FULL", "Jose Manuel Salazar Salcido - OPERADOR TORTON",
    "Mario Garcia Sanchez - OPERADOR FULL", "Zair Diego Campos Mares - OPERADOR FULL",
    "Rodrigo Navarro Hernandez - OPERADOR FULL", "Carlos Martinez Hernandez - OPERADOR FULL",
    "Gabriel Poxtan Temix - OPERADOR FULL", "Alejandro Guadarrama Zamora - OPERADOR SENCILLO",
]

# Unidades económicas y su serie de chasis
UNIDADES_ECONOMICAS = [
    "", "388", "471",
    "472", "503",
    "540", "543",
    "470", "530",
    "539", "508",
    "412", "435",
    "538",
]

st.title("Control de Circuitos - Portal del Operador")

# 1. Identificación del Operador
col_id1, col_id2 = st.columns(2)
with col_id1:
  operador_actual = st.selectbox("Selecciona tu Nombre y Puesto:", OPERADORES_OFICIALES)
with col_id2:
  unidad_actual = st.selectbox("Selecciona tu Unidad y Chasis:", UNIDADES_ECONOMICAS)

st.markdown("---")

def obtener_tiempo_mexico():
  ahora_mexico = datetime.utcnow() - timedelta(hours=6)
  return ahora_mexico.strftime("%d/%m/%Y"), ahora_mexico.strftime("%H:%M:%S")

def guardar_en_gsheets(dataframe, current_sheet):
  current_sheet.clear()
  current_sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

# ---------------------------------------------------------
# VALIDACIÓN DE VIAJES PENDIENTES
# ---------------------------------------------------------
mis_pendientes = pd.DataFrame()
if operador_actual and not df.empty:
    mis_pendientes = df[
        (df["OPERADOR"] == operador_actual) & 
        ((df["FECHA LLEGADA DESTINO"] == "") | (df["FECHA LLEGADA DESTINO"].isna()))
    ]
    if not mis_pendientes.empty:
      st.warning(f"⚠️ Tienes **{len(mis_pendientes)} viaje(s) en curso** pendiente(s) de cerrar. Ve a la sección de seguimiento.")

# Botones de navegación principales
st.markdown("### Menú de Operación")
col_b1, col_b2 = st.columns(2)

if "menu_operador" not in st.session_state:
  st.session_state.menu_operador = "Iniciar Nuevo Viaje"

if col_b1.button("🚀 Iniciar Nuevo Viaje", use_container_width=True):
  st.session_state.menu_operador = "Iniciar Nuevo Viaje"
  st.rerun()
if col_b2.button("📥 Dar Seguimiento / Cerrar Pendientes", use_container_width=True):
  st.session_state.menu_operador = "Dar Seguimiento / Cerrar Pendientes"
  st.rerun()

modo = st.session_state.menu_operador
st.markdown(f"**Sección actual:** {modo}")
st.markdown("---")

# ---------------------------------------------------------
# OPCIÓN A: INICIAR NUEVO VIAJE
# ---------------------------------------------------------
if modo == "Iniciar Nuevo Viaje":
  st.header("Iniciar Nuevo Circuito")

  if not operador_actual or not unidad_actual:
    st.warning("Por favor selecciona primero tu **Nombre** y **Unidad** en la parte superior.")
  elif not mis_pendientes.empty:
      st.error("⛔ Ya tienes un viaje en curso sin cerrar. Debes concluirlo en la sección de 'Dar Seguimiento / Cerrar Pendientes' antes de iniciar uno nuevo.")
  else:
      tipo_circuito = st.radio("Selecciona el tipo de circuito:", ["Directo", "Enlace"], key="tipo_circuito_radio")
      
      f_salida, h_salida = obtener_tiempo_mexico()

      if tipo_circuito == "Directo":
        st.subheader("Ruta Directa")
        origen = st.selectbox("Origen", PLAZAS, key="origen_dir")
        destino = st.selectbox("Destino", [p for p in PLAZAS if p != origen], key="destino_dir")
        plaza_intermedia = ""
      else:
        st.subheader("Ruta con Enlace (Escala)")
        origen = st.selectbox("Origen", PLAZAS, key="origen_enl")
        plaza_intermedia = st.selectbox("Plaza Intermedia (Escala)", [p for p in PLAZAS if p != origen], key="plaza_int")
        destino = st.selectbox("Destino Final", [p for p in PLAZAS if p != origen and p != plaza_intermedia], key="destino_enl")

      st.write(f"**Fecha de Salida (Automática):** {f_salida}")
      st.write(f"**Hora de Salida (Automática):** {h_salida}")

      if st.button("Registrar Salida de Origen"):
          nueva_fila = {
              "OPERADOR": operador_actual, "NO. ECO": str(unidad_actual), "TIPO": tipo_circuito,
              "ORIGEN": origen, "PLAZA INTERMEDIA": plaza_intermedia, "DESTINO": destino,
              "FECHA SALIDA ORIGEN": f_salida, "HORA SALIDA ORIGEN": h_salida,
              "FECHA LLEGADA INTERMEDIA": "", "HORA LLEGADA INTERMEDIA": "",
              "FECHA SALIDA INTERMEDIA": "", "HORA SALIDA INTERMEDIA": "",
              "FECHA LLEGADA DESTINO": "", "HORA LLEGADA DESTINO": "",
              "OBSERVACIONES ESCALA": "", "OBSERVACIONES DESTINO": "",
          }
          df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
          guardar_en_gsheets(df, sheet)
          st.success("✅ ¡GUARDADO EXITOSO! Salida registrada.")
          st.rerun()

# ---------------------------------------------------------
# OPCIÓN B: SEGUIMIENTO Y CIERRE DE PENDIENTES
# ---------------------------------------------------------
elif modo == "Dar Seguimiento / Cerrar Pendientes":
  st.header("Mi Viaje en Ruta / Pendiente de Cerrar")

  if not operador_actual:
    st.warning("Selecciona tu nombre en la parte superior para ver tu viaje.")
  elif mis_pendientes.empty:
      st.success("✅ ¡No tienes viajes pendientes! Todos tus circuitos están cerrados.")
  else:
      viaje_info = mis_pendientes.iloc[0]
      tipo_c = viaje_info["TIPO"]
      idx_viaje = mis_pendientes.index[0]

      st.markdown("---")
      st.markdown("### Detalle de tu Viaje Actual")
      st.write(f"- **Tipo de Circuito:** {tipo_c}")
      st.write(f"- **Ruta:** {viaje_info['ORIGEN']} ➡️ " + (f"{viaje_info['PLAZA INTERMEDIA']} ➡️ " if tipo_c == "Enlace" else "") + f"{viaje_info['DESTINO']}")
      st.write(f"- **Salida de Origen:** {viaje_info['FECHA SALIDA ORIGEN']} a las {viaje_info['HORA SALIDA ORIGEN']}")

      # CASO 1: CIRCUITO DIRECTO
      if tipo_c == "Directo":
        f_now, h_now = obtener_tiempo_mexico()
        st.markdown("#### Registrar Llegada a Destino")
        st.write(f"**Fecha de Llegada (Automática):** {f_now}")
        st.write(f"**Hora de Llegada (Automática):** {h_now}")

        # Sin st.form
        obs_destino_dir = st.text_area("Observaciones / Percances en el trayecto (Destino Final)", key="obs_dir_input")

        if st.button("Cerrar Circuito Directo"):
            obs_previa = str(viaje_info.get("OBSERVACIONES DESTINO", ""))
            nueva_obs = f"{obs_previa} | {obs_destino_dir}".strip(" |") if obs_destino_dir else obs_previa

            df.loc[idx_viaje, "FECHA LLEGADA DESTINO"] = f_now
            df.loc[idx_viaje, "HORA LLEGADA DESTINO"] = h_now
            df.loc[idx_viaje, "OBSERVACIONES DESTINO"] = nueva_obs
            guardar_en_gsheets(df, sheet)
            st.success("✅ ¡GUARDADO EXITOSO! Circuito directo cerrado.")
            st.rerun()

      # CASO 2: CIRCUITO ENLACE
      else:
        llego_intermedia = str(viaje_info["FECHA LLEGADA INTERMEDIA"]).strip() != ""

        if not llego_intermedia:
          st.markdown(f"#### 📍 Paso 1: Registrar LLEGADA a Plaza Intermedia: {viaje_info['PLAZA INTERMEDIA']}")
          f_lleg_int, h_lleg_int = obtener_tiempo_mexico()
          st.write(f"**Fecha y Hora de Arribo a Escala (Automática):** {f_lleg_int} - {h_lleg_int}")

          obs_escala = st.text_area(f"Observaciones al llegar a la escala ({viaje_info['PLAZA INTERMEDIA']})", key="obs_esc_input")

          if st.button("Guardar Llegada a Escala"):
            df.loc[idx_viaje, "FECHA LLEGADA INTERMEDIA"] = f_lleg_int
            df.loc[idx_viaje, "HORA LLEGADA INTERMEDIA"] = h_lleg_int
            df.loc[idx_viaje, "OBSERVACIONES ESCALA"] = obs_escala
            guardar_en_gsheets(df, sheet)
            st.success(f"✅ ¡GUARDADO EXITOSO! Llegada a {viaje_info['PLAZA INTERMEDIA']} registrada.")
            st.rerun()

        else:
          salio_intermedia = str(viaje_info["FECHA SALIDA INTERMEDIA"]).strip() != ""

          st.markdown(f"✅ **Llegada a Escala ya registrada:** {viaje_info['FECHA LLEGADA INTERMEDIA']} a las {viaje_info['HORA LLEGADA INTERMEDIA']}")
          if viaje_info["OBSERVACIONES ESCALA"]:
            st.info(f"📝 Nota en escala: {viaje_info['OBSERVACIONES ESCALA']}")

          if not salio_intermedia:
            st.markdown(f"#### 🚀 Paso 2: Registrar SALIDA de Plaza Intermedia: {viaje_info['PLAZA INTERMEDIA']}")
            f_sal_int, h_sal_int = obtener_tiempo_mexico()
            st.write(f"**Fecha y Hora de Salida de Escala (Automática):** {f_sal_int} - {h_sal_int}")

            obs_salida_escala = st.text_area("Observaciones al reanudar la marcha desde la escala", key="obs_sal_esc_input")

            if st.button("Guardar Salida de Escala"):
              obs_previa = str(viaje_info.get("OBSERVACIONES ESCALA", ""))
              nueva_obs = f"{obs_previa} | Salida: {obs_salida_escala}" if obs_salida_escala else obs_previa
              
              df.loc[idx_viaje, "FECHA SALIDA INTERMEDIA"] = f_sal_int
              df.loc[idx_viaje, "HORA SALIDA INTERMEDIA"] = h_sal_int
              df.loc[idx_viaje, "OBSERVACIONES ESCALA"] = nueva_obs
              guardar_en_gsheets(df, sheet)
              st.success("✅ ¡GUARDADO EXITOSO! Salida de escala registrada.")
              st.rerun()

          else:
            st.markdown(f"✅ **Salida de Escala ya registrada:** {viaje_info['FECHA SALIDA INTERMEDIA']} a las {viaje_info['HORA SALIDA INTERMEDIA']}")
            st.markdown(f"#### 🏁 Paso 3: Registrar LLEGADA al Destino Final: {viaje_info['DESTINO']}")
            f_lleg_fin, h_lleg_fin = obtener_tiempo_mexico()
            st.write(f"**Fecha y Hora de Llegada a Destino Final (Automática):** {f_lleg_fin} - {h_lleg_fin}")

            obs_destino_enlace = st.text_area("Observaciones / Percances al llegar al Destino Final", key="obs_dest_enl_input")

            if st.button("Cerrar Viaje en Destino Final"):
              df.loc[idx_viaje, "FECHA LLEGADA DESTINO"] = f_lleg_fin
              df.loc[idx_viaje, "HORA LLEGADA DESTINO"] = h_lleg_fin
              df.loc[idx_viaje, "OBSERVACIONES DESTINO"] = obs_destino_enlace
              guardar_en_gsheets(df, sheet)
              st.success("✅ ¡GUARDADO EXITOSO! El circuito de enlace ha sido cerrado.")
              st.rerun()

# ---------------------------------------------------------
# DESCARGA DE DATOS
# ---------------------------------------------------------
st.markdown("---")
with st.expander("📂 Ver / Descargar Base de Datos Maestra"):
  st.dataframe(df)
  csv_data = df.to_csv(index=False).encode("utf-8")
  st.download_button(label="Descargar Base de Datos en CSV", data=csv_data, file_name="control_circuitos_maestro.csv", mime="text/csv")
