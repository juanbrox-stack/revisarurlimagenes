import streamlit as st
import requests
import pandas as pd
import io

# Configuración visual
st.set_page_config(page_title="Validador SKU Turaco", page_icon="📦")

st.title("📦 Validador de Imágenes por SKU")
st.markdown("""
Sube tu archivo Excel. El script revisará las URLs y te dirá cuáles son imágenes reales 
y cuáles redirigen a la página de error.
""")

def verificar_url(url):
    """Verifica si la URL apunta a una imagen real."""
    try:
        # Petición rápida para no descargar toda la imagen
        r = requests.head(url, allow_redirects=True, timeout=3)
        content_type = r.headers.get('Content-Type', '')
        
        # Si el status es 200 y el contenido es una imagen
        if r.status_code == 200 and "image" in content_type:
            return "Válida"
        else:
            return "Página de Error"
    except:
        return "Error de Conexión"

# --- Interfaz de Usuario ---
archivo_subido = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo_subido is not None:
    # Leer el Excel
    df = pd.read_excel(archivo_subido)
    
    st.write("Vista previa del archivo subido:")
    st.dataframe(df.head())

    # Dejamos que el usuario elija las columnas si los nombres varían
    col_sku = st.selectbox("Selecciona la columna del SKU", df.columns, index=0)
    col_url = st.selectbox("Selecciona la columna de la URL", df.columns, index=1)
    
    if st.button("🔍 Validar Imágenes"):
        resultados = []
        progreso = st.progress(0)
        total = len(df)

        # Iterar sobre las filas del DataFrame
        for i, row in df.iterrows():
            url = str(row[col_url])
            estado = verificar_url(url)
            resultados.append(estado)
            
            # Actualizar progreso
            progreso.progress((i + 1) / total)
        
        # Añadir la nueva columna al DataFrame original
        df['Estado_Imagen'] = resultados
        
        st.success("✅ ¡Validación terminada!")
        st.dataframe(df)

        # Preparar descarga del nuevo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Descargar Excel con Resultados",
            data=output.getvalue(),
            file_name="reporte_imagenes_validadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )