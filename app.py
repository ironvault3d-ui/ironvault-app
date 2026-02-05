import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="IronVault Admin", page_icon="🛡️", layout="centered")

# --- ESTILOS VISUALES (HACKEANDO CSS) ---
st.markdown("""
    <style>
    .stApp {background-color: #0e1117;}
    h1 {color: #00e5ff !important;}
    .stButton>button {
        background-color: #00e5ff;
        color: black;
        font-weight: bold;
        width: 100%;
        border-radius: 10px;
        height: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO Y TÍTULO ---
st.title("🛡️ IRONVAULT DISPATCHER")
st.markdown("---")

# --- ENTRADAS DE DATOS ---
client_email = st.text_input("📧 Email del Cliente", placeholder="cliente@gmail.com")
pack_selected = st.selectbox("📦 Pack Comprado", 
                             ["MEGA PACK 8TB (Completo)", "Pack Mates", "Pack Soportes", "Pack Marvel", "Pack Anime" , "Pack Marvel"])

# --- LÓGICA DE ENVÍO ---
def send_email(to_email, pack_name):
    # Credenciales (Vienen de los Secretos de Streamlit)
    from_email = st.secrets["GMAIL_USER"]
    password = st.secrets["GMAIL_PASSWORD"]

    # Configurar el mensaje
    msg = MIMEMultipart()
    msg['From'] = "IronVault 3D <" + from_email + ">"
    msg['To'] = to_email
    msg['Subject'] = f"🚀 Acceso Habilitado: {pack_name} - IronVault 3D"

    # Cuerpo del mail (HTML para que quede lindo)
    body = f"""
    <html>
      <body style="background-color: #1a1a1a; color: white; font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #00e5ff;">¡Bienvenido a la Bóveda! 🛡️</h2>
        <p>Hola,</p>
        <p>Tu acceso al <strong>{pack_name}</strong> ya está reservado.</p>
        <hr style="border: 1px solid #333;">
        <h3 style="color: #00e5ff;">⚠️ PASOS OBLIGATORIOS (LEER ADJUNTO):</h3>
        <p>Para descargar los archivos sin errores, seguí la <strong>GUÍA VISUAL</strong> que te adjuntamos en este correo.</p>
        <ol>
            <li>Mirá la imagen adjunta "Instructivo.jpg".</li>
            <li>Andá a MEGA y aceptá nuestra solicitud de amistad/colaboración.</li>
            <li>Buscá la carpeta en "Elementos Compartidos".</li>
        </ol>
        <p>Cualquier duda, respondé este correo.</p>
        <p><em>Equipo IronVault 3D</em></p>
      </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    # ADJUNTAR LA IMAGEN (Instructivo)
    filename = "Instructivo.png" 
    try:
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        msg.attach(part)
    except Exception as e:
        st.error(f"Error al adjuntar imagen: {e}")
        return False

    # CONEXIÓN CON GMAIL
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Falló el envío: {e}")
        return False

# --- BOTÓN DE ACCIÓN ---
if st.button("🚀 ACTIVAR ACCESO AHORA"):
    if not client_email:
        st.warning("⚠️ ¡Poné el mail del cliente, cabeza!")
    else:
        with st.spinner("Conectando con el satélite... 🛰️"):
            success = send_email(client_email, pack_selected)
            if success:
                st.success(f"✅ ¡LISTO! Mail enviado a {client_email}")
                st.balloons()
            else:
                st.error("❌ Hubo un error. Revisá la contraseña o el mail.")

st.markdown("---")
st.caption("IronVault Systems v1.0 - By Beto")