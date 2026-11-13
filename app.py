"""GOOD AYNI NOVA — AYNI-ANALOG. Prototipo educativo, no validador científico."""
import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AYNI-ANALOG | GOOD AYNI NOVA", page_icon="🌕", layout="wide")
st.markdown("""<style> .stApp{background:#08172b;color:#f3f8ff} h1,h2,h3{color:#eaf7ff} [data-testid='stMetricValue']{color:#46dfdb} .block-container{padding-top:2rem} </style>""",unsafe_allow_html=True)

STOCK = pd.DataFrame([
    {"nombre":"Andes de Cajamarca (ejemplo)","cuerpo":"Tierra","pendiente":22,"rugosidad":62,"accesibilidad":74,"origen":"SIMULADO"},
    {"nombre":"Puna altoandina (ejemplo)","cuerpo":"Tierra","pendiente":12,"rugosidad":46,"accesibilidad":38,"origen":"SIMULADO"},
    {"nombre":"Terreno volcánico (ejemplo)","cuerpo":"Tierra","pendiente":29,"rugosidad":84,"accesibilidad":31,"origen":"SIMULADO"},
    {"nombre":"Terreno lunar accidentado (ejemplo)","cuerpo":"Luna","pendiente":26,"rugosidad":78,"accesibilidad":35,"origen":"SIMULADO"},
    {"nombre":"Terreno marciano rocoso (ejemplo)","cuerpo":"Marte","pendiente":16,"rugosidad":58,"accesibilidad":48,"origen":"SIMULADO"},
])
ATTR = ["pendiente", "rugosidad", "accesibilidad"]

st.title("🌍🌕 GOOD AYNI NOVA · AYNI-ANALOG")
st.markdown("**From the Andes to the Moon · Dos mundos, una misión**  ")
st.caption("I.E. Dos de Mayo · Cajamarca, Perú · Asesora: Prof. Irene Salomé Romero Tucto")
st.warning("**Prototipo educativo:** la base inicial contiene datos SIMULADOS. Los resultados no certifican equivalencia con terrenos de la Luna o Marte, ni sustituyen evaluaciones científicas o de seguridad.")

with st.expander("📥 ¿Cómo incorporar datos propios? · Formato CSV"):
    st.write("Cargue un archivo CSV con las columnas: `nombre,cuerpo,pendiente,rugosidad,accesibilidad,origen`. Valores de las tres métricas: **0 a 100** (índices normalizados definidos por el equipo, NO grados ni metros). `cuerpo` debe ser Tierra, Luna o Marte. `origen` indica procedencia; documente en un informe aparte instrumento, fuente, resolución y fecha de cada medición.")
    st.download_button("Descargar plantilla CSV", STOCK.to_csv(index=False).encode("utf-8-sig"), "AYNI_ANALOG_plantilla.csv", "text/csv")
    uploaded = st.file_uploader("Importar datos en CSV",type=["csv"])

frame=STOCK.copy()
if uploaded is not None:
    try:
        candidate=pd.read_csv(uploaded,encoding="utf-8-sig")
        needed={"nombre","cuerpo","pendiente","rugosidad","accesibilidad","origen"}
        missing=needed-set(candidate.columns)
        if missing: raise ValueError("Faltan columnas: "+", ".join(sorted(missing)))
        candidate=candidate[list(needed)].copy()
        for col in ATTR:
            candidate[col]=pd.to_numeric(candidate[col],errors="raise")
            if candidate[col].isna().any() or not candidate[col].between(0,100).all():
                raise ValueError(f"{col}: valores obligatorios entre 0 y 100")
        candidate["cuerpo"]=candidate["cuerpo"].astype(str).str.strip().str.capitalize()
        if not candidate["cuerpo"].isin(["Tierra","Luna","Marte"]).all():
            raise ValueError("cuerpo solo admite Tierra, Luna o Marte")
        if candidate["nombre"].isna().any() or candidate["nombre"].duplicated().any():
            raise ValueError("Cada lugar debe tener un nombre único y no vacío")
        frame=candidate
        st.success(f"CSV importado: {len(frame)} ubicaciones. Revise que las cifras tengan fuentes y metodología comparables.")
    except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as exc:
        st.error(f"No se pudo importar: {exc}. Se mantienen los datos demostrativos.")

left,right=st.columns([1,2],gap="large")
with left:
    st.subheader("⚙️ Configuración")
    earth=frame[frame.cuerpo=="Tierra"]
    planet=frame[frame.cuerpo.isin(["Luna","Marte"])]
    if earth.empty or planet.empty:
        st.error("Se requiere al menos un lugar de Tierra y uno de Luna o Marte.")
        st.stop()
    e_name=st.selectbox("Lugar terrestre",earth.nombre.tolist())
    p_name=st.selectbox("Escenario lunar o marciano",planet.nombre.tolist())
    st.markdown("**Pesos de análisis** (se normalizan)")
    weights={"pendiente":st.slider("Pendiente",0,100,40),"rugosidad":st.slider("Rugosidad",0,100,40),"accesibilidad":st.slider("Accesibilidad",0,100,20)}
    total=sum(weights.values())
    st.caption("Cero en todos los pesos produce un índice 0 (sin comparación).")
with right:
    a=earth[earth.nombre==e_name].iloc[0]
    b=planet[planet.nombre==p_name].iloc[0]
    # Función didáctica. No utilizar con unidades físicas sin normalización explícita.
    sim={k:max(0.0,100.0-2.0*abs(float(a[k])-float(b[k]))) for k in ATTR}
    score=sum(sim[k]*weights[k] for k in ATTR)/total if total else 0
    st.metric("Índice didáctico de similitud",f"{score:.1f} / 100",help="Índice descriptivo basado en métricas normalizadas simuladas o cargadas por el usuario. No es probabilidad ni certificación de analogía.")
    st.subheader("Comparación explicable")
    for label,key in [("Pendiente","pendiente"),("Rugosidad","rugosidad"),("Accesibilidad","accesibilidad")]:
        st.write(f"**{label}:** similitud {sim[key]:.1f}/100 · peso normalizado {weights[key]/total*100 if total else 0:.0f}%")
        st.progress(int(round(sim[key])))
    values=pd.DataFrame({"Característica":ATTR,"Tierra":[a[k] for k in ATTR],"Luna o Marte":[b[k] for k in ATTR]})
    st.bar_chart(values.set_index("Característica"), stack=False)
    st.write("**Propuesta de ensayo:**", "Evaluar movilidad de un rover escolar en un recorrido de prueba con obstáculos y pendientes." if b.cuerpo=="Luna" else "Comparar rutas de un vehículo escolar sobre superficies rocosas y medir tiempo de recorrido.")
    st.info("**Límites de la analogía:** gravedad, atmósfera, radiación, polvo y extremos térmicos difieren sustancialmente. La 'accesibilidad' terrestre y planetaria no es una propiedad físicamente equivalente; aquí se incluye solo como criterio operativo ilustrativo.")
    report=pd.DataFrame([
        {"campo":"proyecto","valor":"GOOD AYNI NOVA - AYNI-ANALOG"},
        {"campo":"tipo_de_indice","valor":"EDUCATIVO NO VALIDADO"},
        {"campo":"sitio_terrestre","valor":e_name},
        {"campo":"objetivo","valor":p_name},
        {"campo":"origen_tierra","valor":a.origen},
        {"campo":"origen_objetivo","valor":b.origen},
        {"campo":"puntaje","valor":round(score,2)},
        *[{"campo":"similitud_"+k,"valor":round(sim[k],2)} for k in ATTR],
        *[{"campo":"peso_"+k,"valor":round(weights[k]/total*100,1) if total else 0} for k in ATTR],
    ])
    st.download_button("📤 Exportar resultado CSV", report.to_csv(index=False).encode("utf-8-sig"),"GOOD_AYNI_NOVA_resultado.csv","text/csv",use_container_width=True)

st.divider()
st.subheader("📚 Fuentes y siguiente etapa")
st.markdown("""La aplicación **no descarga datos NASA automáticamente**. Para evolucionar del modo didáctico a una investigación reproducible, se requiere: (1) obtener modelos de elevación apropiados; (2) calcular pendiente y rugosidad con definiciones y resoluciones compatibles; (3) justificar cómo se representa la accesibilidad; (4) citar los archivos originales; y (5) validar el análisis con especialistas.

- [NASA Earthdata](https://www.earthdata.nasa.gov/)
- [Moon Trek](https://trek.nasa.gov/moon/)
- [Mars Trek](https://trek.nasa.gov/mars/)
- [NASA POWER](https://power.larc.nasa.gov/)

*Proyecto escolar independiente. No implica patrocinio ni validación de NASA.*""")
