import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import datetime

st.set_page_config(
    page_title="Monitoreo RMCAB Bogotá",
    page_icon="🌐",
    layout="wide"
)

np.random.seed(42)

estaciones_rmcab = {
    "Guaymaral": {"lat": 4.7830, "lon": -74.0440, "base": 32, "tipo": "Rural/Periurbana"},
    "Usaquén": {"lat": 4.7103, "lon": -74.0306, "base": 38, "tipo": "Urbana Residencial"},
    "Suba": {"lat": 4.7410, "lon": -74.0850, "base": 52, "tipo": "Urbana Residencial"},
    "Bolivia": {"lat": 4.7180, "lon": -74.1150, "base": 48, "tipo": "Rural/Periurbana"},
    "Colina": {"lat": 4.7320, "lon": -74.0650, "base": 42, "tipo": "Urbana Residencial"},
    "Las Ferias": {"lat": 4.6903, "lon": -74.0822, "base": 58, "tipo": "Urbana Tráfico"},
    "Engativá": {"lat": 4.7010, "lon": -74.1200, "base": 62, "tipo": "Urbana Residencial"},
    "Parque Simón Bolívar": {"lat": 4.6580, "lon": -74.0840, "base": 41, "tipo": "Urbana Residencial"},
    "Móvil 7ma": {"lat": 4.6640, "lon": -74.0550, "base": 56, "tipo": "Urbana Tráfico"},
    "Móvil Fontibón": {"lat": 4.6750, "lon": -74.1380, "base": 72, "tipo": "Urbana Industrial"},
    "Fontibón": {"lat": 4.6700, "lon": -74.1440, "base": 78, "tipo": "Urbana Industrial"},
    "MinAmbiente": {"lat": 4.6097, "lon": -74.0689, "base": 45, "tipo": "Urbana Centro"},
    "Centro": {"lat": 4.6020, "lon": -74.0820, "base": 64, "tipo": "Urbana Centro"},
    "Puente Aranda": {"lat": 4.6317, "lon": -74.1175, "base": 88, "tipo": "Urbana Industrial"},
    "Kennedy": {"lat": 4.6250, "lon": -74.1611, "base": 96, "tipo": "Urbana Tráfico"},
    "Bosa": {"lat": 4.6100, "lon": -74.1900, "base": 104, "tipo": "Urbana Industrial"},
    "Carvajal - Sevillana": {"lat": 4.5978, "lon": -74.1331, "base": 118, "tipo": "Urbana Industrial"},
    "Jazmín": {"lat": 4.6180, "lon": -74.1120, "base": 82, "tipo": "Urbana Residencial"},
    "Tunal": {"lat": 4.5761, "lon": -74.1302, "base": 68, "tipo": "Urbana Tráfico"},
    "San Cristóbal": {"lat": 4.5720, "lon": -74.0830, "base": 38, "tipo": "Rural/Periurbana"},
    "Ciudad Bolívar": {"lat": 4.5606, "lon": -74.1614, "base": 82, "tipo": "Urbana Industrial"},
    "Usme": {"lat": 4.4717, "lon": -74.1122, "base": 33, "tipo": "Rural/Periurbana"}
}

registros = []
for nombre, info in estaciones_rmcab.items():
    aqi_val = max(10, int(np.random.normal(info["base"], 6)))
    registros.append({
        "Estación": nombre,
        "Tipo": info["tipo"],
        "Latitud": info["lat"],
        "Longitud": info["lon"],
        "AQI": aqi_val,
        "PM2.5": round(aqi_val * 0.85, 1),
        "PM10": round(aqi_val * 1.25, 1)
    })

df_actual = pd.DataFrame(registros)

def obtener_color(aqi):
    if aqi <= 50: return "#27ae60"
    elif aqi <= 100: return "#f39c12"
    elif aqi <= 150: return "#e67e22"
    else: return "#e74c3c"

def obtener_estado(aqi):
    if aqi <= 50: return "Favorable (Verde)"
    elif aqi <= 100: return "Moderado (Amarillo)"
    elif aqi <= 150: return "Dañino para Grupos Sensibles (Naranja)"
    else: return "Dañino a la Salud (Rojo)"

def obtener_recomendacion(aqi):
    if aqi <= 50: return "Calidad de aire óptima. Actividades al aire libre sin restricciones."
    elif aqi <= 100: return "Calidad aceptable. Personas extremadamente sensibles deben moderar esfuerzos prolongados."
    elif aqi <= 150: return "Riesgo para niños, adultos mayores y personas con afecciones respiratorias. Reducir ejercicio intenso."
    else: return "Alerta general: Evite por completo la actividad física al aire libre y uso de transportes abiertos."

st.title("🌐 Panel de Monitoreo RMCAB Bogotá - Interactivo")
st.markdown("Explore las estaciones, consulte sus reportes detallados y controle la visualización térmica.")

st.sidebar.header("Filtros y Opciones")
dropdown_variable = st.sidebar.selectbox("Contaminante:", options=["AQI", "PM2.5", "PM10"])

tipos_zona = ["Todas"] + list(df_actual["Tipo"].unique())
dropdown_tipo = st.sidebar.selectbox("Tipo de Zona:", options=tipos_zona)

mostrar_calor = st.sidebar.toggle("🔥 Mostrar Mapa de Calor", value=True)

df_f = df_actual if dropdown_tipo == "Todas" else df_actual[df_actual["Tipo"] == dropdown_tipo]

promedio = round(df_f[dropdown_variable].mean(), 1) if not df_f.empty else 0
max_reg = df_f.loc[df_f[dropdown_variable].idxmax()] if not df_f.empty else None
criticas = len(df_f[df_f["AQI"] > 100])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Promedio General", value=f"{promedio} {dropdown_variable}")
with col2:
    estacion_max_nombre = max_reg['Estación'] if max_reg is not None else 'N/A'
    valor_max = max_reg[dropdown_variable] if max_reg is not None else 0
    st.metric(label="Punto más crítico", value=estacion_max_nombre, delta=str(valor_max), delta_color="inverse")
with col3:
    st.metric(label="Estaciones Críticas (>100 AQI)", value=criticas, delta_color="inverse")

if not df_f.empty:
    max_aqi = df_f["AQI"].max()
    estacion_max = df_f.loc[df_f["AQI"].idxmax()]["Estación"]
    color_alerta = obtener_color(max_aqi)
    rec_texto = obtener_recomendacion(max_aqi)
    
    st.markdown(f"""
    <div style="background-color: #fdfefe; border: 1px solid #e0e0e0; border-left: 5px solid {color_alerta}; padding: 12px 15px; margin-bottom: 15px; border-radius: 6px; font-family: Arial; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <div style="font-size: 13px; font-weight: bold; color: #2c3e50; margin-bottom: 3px;">
            🛡️ Protocolo Sanitario Activo (Pico actual en: <span style="color: {color_alerta};">{estacion_max}</span> - AQI {max_aqi})
        </div>
        <div style="font-size: 12px; color: #555; line-height: 1.4;">
            {rec_texto}
        </div>
    </div>
    """, unsafe_allow_html=True)

mapa = folium.Map(location=[4.63, -74.11], zoom_start=11, tiles="CartoDB positron")

if mostrar_calor and not df_f.empty:
    from folium.plugins import HeatMap
    datos_calor = df_f[["Latitud", "Longitud", dropdown_variable]].values.tolist()
    HeatMap(datos_calor, radius=30, blur=20, min_opacity=0.4).add_to(mapa)

for _, r in df_f.iterrows():
    color_estacion = obtener_color(r["AQI"])
    estado_texto = obtener_estado(r["AQI"])
    recomendacion_estacion = obtener_recomendacion(r["AQI"])
    
    popup_html = f"""
    <div style="font-family: Arial; font-size: 12px; width: 230px; line-height: 1.5; padding: 4px;">
        <b style="color: #2c3e50; font-size: 14px; border-bottom: 2px solid {color_estacion}; display: block; padding-bottom: 3px;">{r['Estación']}</b>
        <span style="background: #ecf0f1; padding: 2px 6px; border-radius: 4px; font-size: 10.5px; display: inline-block; margin-top: 5px;">Tipo: {r['Tipo']}</span><br>
        <div style="margin-top: 8px; background: #f9f9f9; padding: 6px; border-radius: 4px; border: 1px solid #eee;">
            <b>Estado:</b> <span style="color: {color_estacion}; font-weight: bold;">{estado_texto}</span><br>
            <b>AQI General:</b> {r['AQI']}<br>
            <b>PM2.5:</b> {r['PM2.5']} µg/m³<br>
            <b>PM10:</b> {r['PM10']} µg/m³
        </div>
        <div style="margin-top: 6px; font-size: 11px; color: #444;">
            <b>Recomendación operativa:</b><br>
            <i>{recomendacion_estacion}</i>
        </div>
    </div>
    """
    
    folium.CircleMarker(
        location=[r["Latitud"], r["Longitud"]],
        radius=10,
        color="#2c3e50",
        weight=1,
        fill=True,
        fill_color=color_estacion,
        fill_opacity=0.9,
        popup=folium.Popup(popup_html, max_width=260),
        tooltip=f"{r['Estación']} ({dropdown_variable}: {r[dropdown_variable]})"
    ).add_to(mapa)

leyenda_html = """
<div style="
    position: fixed; 
    bottom: 30px; right: 30px; width: 190px; 
    background-color: white; z-index: 9999; font-size: 11px; 
    padding: 10px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    font-family: Arial, sans-serif;">
  <p style="margin: 0 0 5px 0; font-weight: bold; text-align: center;">Índice AQI (Riesgo)</p>
  <i style="background: #27ae60; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> Favorable (0-50)<br>
  <i style="background: #f39c12; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> Moderado (51-100)<br>
  <i style="background: #e67e22; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> Sensibles (101-150)<br>
  <i style="background: #e74c3c; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> Dañino (>150)
</div>
"""
mapa.get_root().html.add_child(folium.Element(leyenda_html))

st_folium(mapa, width="100%", height=500)

st.markdown("---")
col_f1, col_f2 = st.columns([2, 1])

with col_f1:
    tiempo_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"<span style='color: #7f8c8d; font-size: 12px;'>🟢 Red RMCAB Activa ({len(df_f)} estaciones filtradas) | Última sincronización: {tiempo_actual}</span>", unsafe_allow_html=True)

with col_f2:
    csv_data = df_f.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar CSV",
        data=csv_data,
        file_name=f"reporte_rmcab_{dropdown_tipo.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )
