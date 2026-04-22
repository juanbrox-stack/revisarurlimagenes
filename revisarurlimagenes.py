import streamlit as st
import requests
import pandas as pd
import io

st.set_page_config(page_title="Validador SKU Turaco", page_icon="📦")

st.title("📦 Validador de Imágenes por SKU")

def verificar_url(url):
    try:
        # Usamos GET en lugar de HEAD por si el servidor de Turaco 
        # bloquea peticiones HEAD (algunos firewalls lo hacen)
        r = requests.get(url, stream=True, allow_redirects=True, timeout=5)
        content_type = r.headers.get('Content-Type', '')
        
        if r.status_code == 200 and "image" in content_type:
            return "Válida"
        else:
            return "Página de Error"
    except:
        return "Error de Conexión"

archivo_subido = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo_subido is not None:
    df = pd.read_excel(archivo_subido)
    
    st.write("### Vista previa del archivo:")
    st.dataframe(df.head())

    col_sku = st.selectbox("Selecciona la columna del SKU", df.columns, index=0)
    col_url = st.selectbox("Selecciona la columna de la URL", df.columns, index=1)
    
    # Usamos un botón para iniciar y guardamos el resultado en la sesión
    if st.button("🔍 Validar Imágenes"):
        resultados = []
        progreso = st.progress(0)
        status_text = st.empty()
        total = len(df)

        for i, row in df.iterrows():
            url = str(row[col_url])
            estado = verificar_url(url)
            resultados.append(estado)
            
            # Actualizar UI
            progreso.progress((i + 1) / total)
            status_text.text(f"Procesando fila {i+1} de {total}...")
        
        # Guardamos el DataFrame procesado en la sesión de Streamlit
        df['Estado_Imagen'] = resultados
        st.session_state['df_finalizado'] = df
        st.success("✅ ¡Procesamiento completado!")

    # Si ya tenemos datos procesados en la sesión, mostramos el resultado y la descarga
    if 'df_finalizado' in st.session_state:
        df_res = st.session_state['df_finalizado']
        st.write("### Resultados:")
        st.dataframe(df_res)

        # Generar el Excel para descargar
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_res.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Descargar Excel con Resultados",
            data=output.getvalue(),
            file_name="reporte_imagenes_validadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )