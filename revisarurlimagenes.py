import streamlit as st
import requests
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Validador de URLs Turaco", page_icon="📷")

st.title("📷 Validador de Imágenes y Extractor de SKU")
st.markdown("Sube un archivo con URLs para verificar cuáles son imágenes reales y extraer su SKU.")

def extraer_sku(url):
    try:
        parte_sku = url.split("/imagenes/")[1]
        sku = parte_sku.split("/")[0]
        return sku
    except:
        return "N/A"

def verificar_url(url):
    try:
        # Usamos un timeout corto para que la app no se bloquee
        r = requests.head(url, allow_redirects=True, timeout=3)
        content_type = r.headers.get('Content-Type', '')
        if r.status_code == 200 and "image" in content_type:
            return "Válida"
        else:
            return "Página de Error / No encontrada"
    except:
        return "Error de Conexión"

# --- Interfaz de Usuario ---
archivo_subido = st.file_uploader("Sube tu archivo de texto (.txt) con una URL por línea", type=["txt"])

if archivo_subido is not None:
    # Leer URLs del archivo
    contenido = archivo_subido.read().decode("utf-8")
    urls = [line.strip() for line in contenido.split("\n") if line.strip()]
    
    if st.button("Iniciar Procesamiento"):
        resultados = []
        progreso = st.progress(0)
        status_text = st.empty()

        for i, url in enumerate(urls):
            # Actualizar barra de progreso
            porcentaje = (i + 1) / len(urls)
            progreso.progress(porcentaje)
            status_text.text(f"Procesando {i+1} de {len(urls)}...")
            
            # Lógica principal
            sku = extraer_sku(url)
            estado = verificar_url(url)
            
            resultados.append({"SKU": sku, "Estado": estado, "URL": url})

        # Crear DataFrame
        df = pd.DataFrame(resultados)
        
        st.success("¡Procesamiento completado!")
        st.write("### Vista previa de los datos:")
        st.dataframe(df)

        # Crear botón de descarga para Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
        
        st.download_button(
            label="📥 Descargar resultados en Excel",
            data=output.getvalue(),
            file_name="resultado_sku_imagenes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )