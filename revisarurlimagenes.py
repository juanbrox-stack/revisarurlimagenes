import streamlit as st
import requests
import pandas as pd
import io

st.set_page_config(page_title="Validador SKU Turaco", page_icon="📦")

st.title("📦 Validador de Errores de Imagen")
st.markdown("Este script generará un Excel **solo con los SKUs cuyas imágenes fallan**.")

def verificar_url(url):
    try:
        # Usamos GET con stream=True para ser más precisos con el servidor
        r = requests.get(url, stream=True, allow_redirects=True, timeout=5)
        content_type = r.headers.get('Content-Type', '')
        
        if r.status_code == 200 and "image" in content_type:
            return "Válida"
        else:
            return "Página de Error"
    except Exception:
        return "Error de Conexión"

archivo_subido = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo_subido is not None:
    df = pd.read_excel(archivo_subido)
    
    st.write("### Vista previa de la subida:")
    st.dataframe(df.head())

    col_sku = st.selectbox("Selecciona la columna del SKU", df.columns, index=0)
    col_url = st.selectbox("Selecciona la columna de la URL", df.columns, index=1)
    
    if st.button("🔍 Buscar errores"):
        resultados = []
        progreso = st.progress(0)
        status_text = st.empty()
        total = len(df)

        for i, row in df.iterrows():
            url = str(row[col_url])
            estado = verificar_url(url)
            resultados.append(estado)
            
            # Actualización visual del progreso
            progreso.progress((i + 1) / total)
            status_text.text(f"Analizando {i+1} de {total}...")
        
        # Añadimos los resultados al DataFrame
        df['Estado_Imagen'] = resultados
        
        # --- FILTRO CRÍTICO ---
        # Filtramos para quedarnos SOLO con lo que NO es "Válida"
        df_errores = df[df['Estado_Imagen'] != "Válida"].copy()
        
        # Guardamos el resultado filtrado en la sesión
        st.session_state['df_errores'] = df_errores
        st.success(f"✅ Análisis finalizado. Se han encontrado {len(df_errores)} errores.")

    # Mostrar resultados y botón de descarga si existen errores
    if 'df_errores' in st.session_state:
        df_final = st.session_state['df_errores']
        
        if not df_final.empty:
            st.write("### Lista de URLs con Error:")
            st.dataframe(df_final)

            # Generar Excel en memoria
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Descargar Excel de ERRORES",
                data=output.getvalue(),
                file_name="errores_imagenes_turaco.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.balloons()
            st.success("¡Increíble! No se han encontrado errores en las imágenes.")