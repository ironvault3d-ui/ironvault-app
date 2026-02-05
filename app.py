import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from mega import Mega  # <--- IMPORTAMOS MEGA

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="IronVault Admin", page_icon="🛡️", layout="centered")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp {background-color: #0e1117;}
    h1 {color: #00e5ff !important; text-align: center;}
    .stButton>button {
        background-color: #00e5ff; color: black; font-weight: bold;
        width: 100%; border-radius: 10px; height: 60px; font-size: 18px;
    }
    .stSelectbox, .stTextInput {color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ IRONVAULT AUTO-BOT")
st.markdown("---")

# ==========================================
# 🗺️ MAPA DE CARPETAS (EDITAR ESTO)
# Izquierda: Lo que ves en la App.
# Derecha: EL NOMBRE EXACTO DE LA CARPETA EN MEGA.
# ==========================================
PACKS_MAP = {
    "MEGA PACK 8TB (Completo)": "Bettah Creativos - 3D Printing",
    "Pack Anime": "BT - Anime",
    "Pack Mates & Bombillas": "PACK MATES",
    "Pack Soportes": "PACK SOPORTES",
    "Pack Cortantes & Torta": "PACK REPOSTERIA",
    "Pack Universo Anime": "PACK ANIME",
    "Pack Marvel & DC": "PACK COMICS",
    "Pack Dragon Ball": "PACK DRAGON BALL"
}

# --- INPUTS ---
col1, col2 = st.columns([3, 1])
with col1:
    client_email = st.text_input("📧 Email del Cliente")
with col2:
    st.write("")

pack_label = st.selectbox("📦 Seleccionar Pack", list(PACKS_MAP.keys()))

# --- FUNCIÓN 1: ENVIAR MAIL ---
def send_email_func(to_email, pack_name):
    from_email = st.secrets["GMAIL_USER"]
    password = st.secrets["GMAIL_PASSWORD"]
    
    msg = MIMEMultipart()
    msg['From'] = f"IronVault 3D <{from_email}>"
    msg['To'] = to_email
    msg['Subject'] = f"🚀 Acceso Habilitado: {pack_name}"

    body = f"""
    <html>
      <body style="background-color: #121212; color: #e0e0e0; font-family: sans-serif; padding: 20px;">
        <h2 style="color: #00e5ff;">🛡️ IRONVAULT 3D</h2>
        <p>Hola, tu acceso al <strong>{pack_name}</strong> está listo.</p>
        <div style="background-color: #1e1e1e; padding: 15px; border-left: 4px solid #00e5ff; margin: 20px 0;">
            <h3 style="color: #00e5ff;">⚠️ PASO FINAL:</h3>
            <ol>
                <li>Mirá la imagen adjunta "Instructivo".</li>
                <li>Entrá a MEGA y <strong>aceptá nuestra solicitud</strong>.</li>
                <li>Buscá la carpeta en "Elementos Compartidos".</li>
            </ol>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))
    
    # Adjuntar Imagen
    try:
        with open("Instructivo.jpg", "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", 'attachment; filename="Instructivo.jpg"')
        msg.attach(part)
    except:
        pass # Si falla la imagen, manda el mail igual

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Error Mail: {e}")
        return False

# --- FUNCIÓN 2: COMPARTIR EN MEGA ---
def share_mega_folder(target_email, folder_name_in_mega):
    mega = Mega()
    m = mega.login(st.secrets["MEGA_EMAIL"], st.secrets["MEGA_PASSWORD"])
    
    # Buscar la carpeta
    file = m.find(folder_name_in_mega)
    
    if file:
        # Compartir (share_node usa el handle de la carpeta)
        # Nivel de acceso: 0 = Read Only (Solo lectura/bajada) -> RECOMENDADO
        # Nivel de acceso: 1 = Read/Write
        # Nivel de acceso: 2 = Full Access
        try:
            # NOTA: La librería mega.py a veces es mañosa con share_node.
            # Intentamos compartir. Si ya está compartido, puede tirar error o actualizar.
            m.share(file[0], target_email, level=0) 
            return True
        except Exception as e:
            st.error(f"❌ Error al compartir en Mega: {e}")
            return False
    else:
        st.error(f"❌ No encontré la carpeta '{folder_name_in_mega}' en tu Mega.")
        return False

# --- BOTÓN DE EJECUCIÓN ---
if st.button("🚀 AUTOMATIZAR TODO"):
    if not client_email:
        st.warning("Falta el mail")
    else:
        mega_folder_name = PACKS_MAP[pack_label]
        
        # Barra de progreso para dar sensación de poder
        my_bar = st.progress(0)
        
        # 1. Mega Share
        st.write("1️⃣ Conectando con Mega...")
        mega_ok = share_mega_folder(client_email, mega_folder_name)
        my_bar.progress(50)
        
        if mega_ok:
            st.success(f"✅ Carpeta '{mega_folder_name}' compartida en Mega.")
            
            # 2. Email Send
            st.write("2️⃣ Enviando Instructivo...")
            email_ok = send_email_func(client_email, pack_label)
            my_bar.progress(100)
            
            if email_ok:
                st.success(f"✅ Mail enviado a {client_email}")
                st.balloons()
            else:
                st.error("Falló el envío del mail.")
        else:
            st.error("Abortando envío de mail porque falló Mega.")
