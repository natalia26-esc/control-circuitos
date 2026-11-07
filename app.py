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

# Listas oficiales actualizadas (Nombre y Puesto)[cite: 7]
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

# Unidades económicas y su serie de chasis[cite: 8]
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

      # FORMULARIO SEGÚN EL TIPO DE CIRCUITO
      with st.form("form_seguimiento"):
        observaciones = st.text_area(
            "Observaciones / Percances en el trayecto",
            value=viaje_info["OBSERVACIONES / PERCANCES"],
        )

        # CASO 1: CIRCUITO DIRECTO (Solo requiere marcar llegada final)
        if tipo_c == "Directo":
          f_now, h_now = obtener_tiempo_mexico()
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

        # CASO 2: CIRCUITO ENLACE (Dividido en 3 pasos reales y separados)
        else:
          # Determinamos automáticamente en qué paso va el viaje
          llego_intermedia = (
              str(viaje_info["FECHA LLEGADA INTERMEDIA"]).strip() != ""
          )

          if not llego_intermedia:
            # PASO A: El operador apenas llegó a la escala
            st.markdown(
                f"#### 📍 Paso 1: Registrar LLEGADA a Plaza Intermedia:"
                f" {viaje_info['PLAZA INTERMEDIA']}"
            )
            f_lleg_int, h_lleg_int = obtener_tiempo_mexico()
            st.write(
                f"**Fecha y Hora de Arribo a Escala (Automática):**"
                f" {f_lleg_int} - {h_lleg_int}"
            )

            btn_llegada_escala = st.form_submit_button(
                "Guardar Llegada a Escala"
            )

            if btn_llegada_escala:
              idx = df[df["FOLIO"].astype(str) == folio_elegido].index[0]
              df.loc[idx, "FECHA LLEGADA INTERMEDIA"] = f_lleg_int
              df.loc[idx, "HORA LLEGADA INTERMEDIA"] = h_lleg_int
              df.loc[idx, "OBSERVACIONES / PERCANCES"] = observaciones
              guardar_en_gsheets(df)
              st.success(
                  f"¡Llegada a {viaje_info['PLAZA INTERMEDIA']} registrada con"
                  " éxito! (Ahora podrás marcar tu salida de la escala cuando"
                  " retomes el viaje)."
              )
              st.rerun()

          else:
            # PASO B: Ya llegó a la escala, ahora registra su SALIDA de la escala y avanza al destino final
            salio_intermedia = (
                str(viaje_info["FECHA SALIDA INTERMEDIA"]).strip() != ""
            )

            st.markdown(
                f"✅ **Llegada a Escala ya registrada:**"
                f" {viaje_info['FECHA LLEGADA INTERMEDIA']} a las"
                f" {viaje_info['HORA LLEGADA INTERMEDIA']}"
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

              btn_salida_escala = st.form_submit_button(
                  "Guardar Salida de Escala"
              )

              if btn_salida_escala:
                idx = df[df["FOLIO"].astype(str) == folio_elegido].index[0]
                df.loc[idx, "FECHA SALIDA INTERMEDIA"] = f_sal_int
                df.loc[idx, "HORA SALIDA INTERMEDIA"] = h_sal_int
                df.loc[idx, "OBSERVACIONES / PERCANCES"] = observaciones
                guardar_en_gsheets(df)
                st.success(
                    "¡Salida de escala registrada! El viaje ha continuado hacia"
                    " el destino final."
                )
                st.rerun()

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

              btn_cierre_final = st.form_submit_button(
                  "Cerrar Viaje en Destino Final"
              )

              if btn_cierre_final:
                idx = df[df["FOLIO"].astype(str) == folio_elegido].index[0]
                df.loc[idx, "FECHA LLEGADA DESTINO"] = f_lleg_fin
                df.loc[idx, "HORA LLEGADA DESTINO"] = h_lleg_fin
                df.loc[idx, "OBSERVACIONES / PERCANCES"] = observaciones
                guardar_en_gsheets(df)
                st.success(
                    f"¡El circuito en enlace {folio_elegido} ha sido cerrado"
                    " por completo y con éxito!"
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
