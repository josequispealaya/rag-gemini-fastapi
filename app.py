import streamlit as st
import requests

# Configuración básica de la página
st.set_page_config(page_title="Asistente RAG - UTN", page_icon="🤖", layout="centered")
st.title("🤖 Chatea con tus Documentos (RAG)")
st.markdown("Subí cualquier PDF en la barra lateral y hacele preguntas. El sistema buscará en el texto y Gemini armará la respuesta.")

# --- BARRA LATERAL: CARGA DE DOCUMENTOS ---
with st.sidebar:
    st.header("📄 Tus Documentos")
    st.markdown("Subí tus PDFs para que la IA los lea y pueda responder tus preguntas.")
    
    # Agregamos accept_multiple_files=True
    uploaded_files = st.file_uploader("Cargá tus PDFs (Máx 5MB c/u)", type=["pdf"], accept_multiple_files=True)
    
    # Verificamos si la lista contiene elementos
    if uploaded_files:
        if st.button("Procesar y Aprender"):
            with st.spinner(f"Ingestando {len(uploaded_files)} documento(s)..."):
                try:
                    # Estructuramos la lista de archivos para el request multipart
                    files_payload = [
                        ("files", (file.name, file.getvalue(), "application/pdf")) 
                        for file in uploaded_files
                    ]
                    
                    upload_url = "http://backend:8000/upload"
                    response = requests.post(upload_url, files=files_payload)
                                       
                    if response.status_code == 200:
                        st.success("¡Documentos procesados con éxito! Ya podés hacer preguntas cruzadas.")
                    else:
                        error_detail = response.json().get("detail", "Error desconocido")
                        st.error(f"Error al subir: {error_detail}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ No se pudo conectar con el servidor. ¿FastAPI está corriendo?")
# ------------------------------------------

# Inicializar el historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial de mensajes al recargar la página
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar la entrada del usuario
if prompt := st.chat_input("Ej: ¿De qué trata este documento, o cuáles son sus puntos clave?"):
    # Mostrar el mensaje del usuario en la interfaz
    st.chat_message("user").markdown(prompt)
    # Guardar en el historial
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Preparar la llamada a tu API local
    api_url = "http://127.0.0.1:8000/ask"
    
    with st.chat_message("assistant"):
        with st.spinner("Buscando en los apuntes y consultando a Gemini..."):
            try:
                # Hacemos la petición POST a FastAPI
                response = requests.post("http://backend:8000/ask", json={"question": prompt})
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No se recibió respuesta.")
                    context = data.get("context_used", "")
                    
                    # Mostrar la respuesta principal
                    st.markdown(answer)
                    
                    # Mostrar el contexto en un desplegable para no ensuciar la vista
                    with st.expander("🔍 Ver contexto recuperado del PDF"):
                        st.info(context)
                        
                    # Guardar la respuesta en el historial
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                
                elif response.status_code in [429, 503]:
                    # Atrapamos los errores específicos que configuramos antes
                    error_detail = response.json().get("detail", "Error temporal del servicio.")
                    st.warning(f"⚠️ {error_detail}")
                else:
                    st.error(f"Error del servidor: Código {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ No se pudo conectar con la API. ¿Asegurate de que FastAPI esté corriendo en otra terminal?")