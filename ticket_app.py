import datetime
import pandas as pd
import streamlit as st

# Configuración de la página.
st.set_page_config(page_title="Support tickets", page_icon="🎫")
st.title("🎫 Tickets Opercionales")
st.write(
    """
    Esta aplicación permite gestionar solicitudes operacionales, incluyendo la creación,
    edición y visualización de estadísticas sobre tickets.
    """
)

# Inicializar el dataframe si no existe en la sesión.
if "df" not in st.session_state:
    # Crear un dataframe vacío con las columnas requeridas.
    st.session_state.df = pd.DataFrame(
        columns=[
            "ID",
            "Solicitud",
            "Estado",
            "Prioridad",
            "Fecha de Creación",
            "Solicitante",
            "Responsable"
        ]
    )

# Opciones para "Solicitante" y "Responsable".
personas = ["Alfredo", "Enrico", "Sebastián", "Julio", "Johanna", "Victor", "Lissette"]

# Sección para agregar una nueva solicitud.
st.header("Agregar una solicitud:")

# Formulario para añadir un nuevo ticket.
with st.form("add_ticket_form"):
    issue = st.text_area("Describa la Solicitud")
    priority = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
    requester = st.selectbox("Nombre del Solicitante", personas)
    responsible = st.selectbox("Responsable asignado", personas)
    submitted = st.form_submit_button("Crear")

if submitted:
    if not issue:
        st.error("Por favor, complete la descripción de la solicitud.")
    else:
        # Generar un nuevo ID basado en los tickets existentes.
        recent_ticket_number = (
            int(st.session_state.df["ID"].str.split("-").str[1].max())
            if not st.session_state.df.empty
            else 0
        )
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        df_new = pd.DataFrame(
            [
                {
                    "ID": f"TICKET-{recent_ticket_number + 1}",
                    "Solicitud": issue,
                    "Estado": "Abierta",
                    "Prioridad": priority,
                    "Fecha de Creación": today,
                    "Solicitante": requester,
                    "Responsable": responsible,
                }
            ]
        )

        # Actualizar el estado de la sesión y mostrar el ticket creado.
        st.session_state.df = pd.concat([df_new, st.session_state.df], ignore_index=True)
        st.success("¡Solicitud creada con éxito!")
        st.dataframe(df_new, use_container_width=True, hide_index=True)

# Sección para ver y editar solicitudes existentes.
st.header("Solicitudes existentes:")
st.write(f"Número de solicitudes: `{len(st.session_state.df)}`")

# Mostrar DataFrame editable.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Estado": st.column_config.SelectboxColumn(
            "Estado",
            help="Estado del ticket",
            options=["Abierta", "En Progreso", "Cerrada"],
            required=True,
        ),
        "Prioridad": st.column_config.SelectboxColumn(
            "Prioridad",
            help="Prioridad",
            options=["Alta", "Media", "Baja"],
            required=True,
        ),
        "Solicitante": st.column_config.SelectboxColumn(
            "Solicitante",
            help="Nombre del solicitante",
            options=personas,
            required=True,
        ),
        "Responsable": st.column_config.SelectboxColumn(
            "Responsable",
            help="Responsable asignado",
            options=personas,
            required=True,
        ),
    },
    disabled=["ID", "Fecha de Creación"],  # Columnas no editables.
)

# Actualizar el dataframe en la sesión si hay cambios.
if not edited_df.equals(st.session_state.df):
    st.session_state.df = edited_df
    st.success("Cambios guardados correctamente.")

# Aplicar colores a las filas del DataFrame.
def color_rows(row):
    if row["Estado"] == "Abierta":
        return ["background-color: #FFCDD2"] * len(row)  # Rojo claro
    elif row["Estado"] == "En Progreso":
        return ["background-color: #FFF9C4"] * len(row)  # Amarillo claro
    elif row["Estado"] == "Cerrada":
        return ["background-color: #C8E6C9"] * len(row)  # Verde claro
    return [""] * len(row)

# Mostrar tabla con estilo.
styled_df = st.session_state.df.style.apply(color_rows, axis=1)
st.write("Vista estilizada:")
st.dataframe(styled_df, use_container_width=True)

# Sección para eliminar tickets cerrados.
if not st.session_state.df.empty:
    st.header("Eliminar solicitudes cerradas:")
    for index, row in st.session_state.df.iterrows():
        if row["Estado"] == "Cerrada":
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{row['ID']}** - {row['Solicitud']}")
            with col2:
                if st.button(f"Eliminar {row['ID']}", key=f"delete_{row['ID']}"):
                    # Eliminar el ticket seleccionado.
                    st.session_state.df = st.session_state.df.drop(index).reset_index(drop=True)
                    st.success(f"Ticket {row['ID']} eliminado.")
                    st.experimental_rerun()  # Recargar la página para reflejar cambios.
