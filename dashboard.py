###App elaborada con fines didáctico en el framework de python
###streamlit url:https://streamlit.io/
###en su versíón Free
###Su página de componentes y ejemplos: https://streamlit.io/components
###Librerias necesarias para el funcionamiento adecuado de la app
###estan respaldadas en el arcivo de instalación requirements.txt
import json
import pandas as pd
import streamlit as st
import plotly.express as px

###Variables de configuración
EXCEL = "ejemplo_analisis_datos.xlsx"
GEOJSON = "br_states.geojson"
TITULO = "Exportaciones Brasileñas de los 4 Principales Productos Agro"
SUBTITULO = "Soja - Milho - Café en granos - Algodón  |  Análisis ejecutivo 2025-2026"

ROJO = "#C8102E"
VERDE = "#009739"
AMARILLO = "#FFDF00"
AZUL = "#1F3A93"
COLORES = [ROJO, VERDE, AZUL, AMARILLO]

###Confiruración general del dashboard
st.set_page_config(page_title=TITULO, page_icon="🌱", layout="wide")


###Carga de todos los datos establecidos para llenar los controles del dashboard
@st.cache_data(show_spinner="Cargando información...")
def cargar_datos():
    prod = pd.read_excel(EXCEL, sheet_name="productos", dtype={"NCM": str})
    prod["NCM"] = prod["NCM"].str.zfill(8)

    paises = pd.read_excel(EXCEL, sheet_name="paises", dtype=str)
    paises["CO_PAIS"] = paises["CO_PAIS"].str.zfill(3)

    estados = pd.read_excel(EXCEL, sheet_name="estados", dtype=str)
    estados["SG_UF"] = estados["SG_UF"].str.strip()

    base = pd.read_excel(EXCEL, sheet_name="Base", usecols="A:I")
    base["CO_PAIS"] = base["CO_PAIS"].astype(str).str.zfill(3)
    base["CO_NCM"] = base["CO_NCM"].astype(str).str.zfill(8)
    base["CO_ANO"] = base["CO_ANO"].astype(int)
    base["CO_MES"] = base["CO_MES"].astype(int)
    base["SG_UF_NCM"] = base["SG_UF_NCM"].astype(str).str.strip()
    for c in ["QT_ESTAT", "KG_LIQUIDO", "VL_FOB"]:
        base[c] = pd.to_numeric(base[c], errors="coerce").fillna(0)

    base = base.merge(
        paises[["CO_PAIS", "NO_PAIS_ESP"]], on="CO_PAIS", how="left"
    ).rename(columns={"NO_PAIS_ESP": "Pais"})
    base["Pais"] = base["Pais"].fillna("Sin dato")

    base = base.merge(
        estados[["SG_UF", "NO_UF", "NO_REGIAO"]],
        left_on="SG_UF_NCM",
        right_on="SG_UF",
        how="left",
    ).rename(columns={"NO_UF": "Estado", "NO_REGIAO": "Region"})
    base["Estado"] = base["Estado"].fillna("Sin dato")
    base["Region"] = base["Region"].fillna("Sin dato")
    return base


###Formatea los números a los decimales e unidades de mil latino
def formato_num(x):
    return f"{x:,.0f}".replace(",", ".")


###Formatea los datos de las KPIs en largura, número de decimales entre otros
def formato_fob(x):
    if x >= 1e9:
        return f"US$ {x/1e9:,.2f} mil millones".replace(",", "X").replace(".", ",").replace("X", ".")
    if x >= 1e6:
        return f"US$ {x/1e6:,.1f} millones".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"US$ {x:,.0f}".replace(",", ".")

###Función que cargo las fuentes de datos al dashboard
df = cargar_datos()

st.title(f"🌱 {TITULO}")
st.caption(SUBTITULO)

###Filtros interactivos 
###Submenú desplegrable con sus respectivas variables
with st.sidebar:
    st.header("Filtros interactivos")
    productos_sel = st.multiselect(
        "Producto", sorted(df["Producto"].unique()), default=sorted(df["Producto"].unique())
    )
    anios_sel = st.multiselect(
        "Año", sorted(df["CO_ANO"].unique()), default=sorted(df["CO_ANO"].unique())
    )
    paises_disp = (
        df[df["Producto"].isin(productos_sel)]["Pais"].dropna().unique()
    )
    paises_sel = st.multiselect("País", sorted(paises_disp))
    regiones_sel = st.multiselect(
        "Región de Brasil", sorted(df["Region"].unique()), default=[]
    )
    top_n = st.slider("Top países a mostrar", 5, 20, 10)
    st.markdown("---")
    st.caption("Fuente: [MDIC Brasil](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta)")

f = df[df["Producto"].isin(productos_sel) & df["CO_ANO"].isin(anios_sel)]
if paises_sel:
    f = f[f["Pais"].isin(paises_sel)]
if regiones_sel:
    f = f[f["Region"].isin(regiones_sel)]

if f.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

###Visualizador de los valores de las KPIs en estudio
total_fob = f["VL_FOB"].sum()
total_kg = f["KG_LIQUIDO"].sum()
n_paises = f["Pais"].nunique()
n_registros = len(f)
top_prod = f.groupby("Producto")["VL_FOB"].sum().idxmax()
top_pais = f.groupby("Pais")["VL_FOB"].sum().idxmax()

fob_2025 = f.loc[f["CO_ANO"] == 2025, "VL_FOB"].sum()
fob_2026 = f.loc[f["CO_ANO"] == 2026, "VL_FOB"].sum()
crecimiento = ((fob_2026 - fob_2025) / fob_2025 * 100) if fob_2025 else 0

st.subheader("Indicadores Clave de Desempeño (KPIs)")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Valor FOB total", formato_fob(total_fob))
k2.metric("Volumen total (kg)", formato_num(total_kg))
k3.metric("Países destino", formato_num(n_paises))
k4.metric("Operaciones", formato_num(n_registros))

k5, k6, k7, k8 = st.columns(4)
k5.metric("Producto líder", top_prod)
k6.metric("País líder", top_pais)
k7.metric("Participación 2026", f"{(fob_2026/total_fob*100 if total_fob else 0):.1f}%")
k8.metric("Variación 2026 vs 2025", f"{crecimiento:+.1f}%")

st.markdown("---")

###Representación de los valores en Gráficos interactivos
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Valor FOB por producto**")
    g = f.groupby("Producto", as_index=False)["VL_FOB"].sum().sort_values("VL_FOB")
    fig = px.bar(
        g, x="VL_FOB", y="Producto", orientation="h",
        color="Producto", color_discrete_sequence=COLORES, text_auto=".2s",
    )
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="US$ FOB")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(f"**Top {top_n} países destino (Valor FOB)**")
    g = (
        f.groupby("Pais", as_index=False)["VL_FOB"].sum()
        .nlargest(top_n, "VL_FOB").sort_values("VL_FOB")
    )
    fig = px.bar(
        g, x="VL_FOB", y="Pais", orientation="h",
        color="VL_FOB", color_continuous_scale="RdYlGn", text_auto=".2s",
    )
    fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="US$ FOB")
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("**Evolución mensual del Valor FOB**")
    g = f.groupby(["CO_ANO", "CO_MES", "Producto"], as_index=False)["VL_FOB"].sum()
    fig = px.line(g, x="CO_MES", y="VL_FOB", color="Producto", markers=True,
                  color_discrete_sequence=COLORES)
    fig.update_layout(xaxis_title="Mes", yaxis_title="US$ FOB",
                      xaxis=dict(dtick=1), legend_title="")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.markdown("**Participación de cada producto**")
    g = f.groupby("Producto", as_index=False)["VL_FOB"].sum()
    fig = px.pie(g, names="Producto", values="VL_FOB", hole=0.45,
                 color_discrete_sequence=COLORES)
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(legend_title="")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("**Mapa-producto: países por producto (Valor FOB)**")
g = f.groupby(["Producto", "Pais"], as_index=False)["VL_FOB"].sum()
g_top = g.sort_values("VL_FOB", ascending=False).groupby("Producto").head(top_n)
fig = px.treemap(g_top, path=["Producto", "Pais"], values="VL_FOB",
                 color="VL_FOB", color_continuous_scale="RdYlGn")
fig.update_layout(margin=dict(t=20, l=10, r=10, b=10))
st.plotly_chart(fig, use_container_width=True)

###Mapa por estados de Brasil
st.markdown("---")
st.subheader("Origen de las exportaciones por estado de Brasil")

with open(GEOJSON, encoding="utf-8") as fh:
    geojson = json.load(fh)

mapa_por = st.radio(
    "Ver mapa por:", ["Producto", "Total (todos los productos)"],
    horizontal=True, label_visibility="collapsed",
)

if mapa_por == "Producto":
    prod_mapa = st.selectbox("Producto del mapa", productos_sel)
    fm = f[f["Producto"] == prod_mapa]
    titulo_mapa = f"Valor FOB por estado - {prod_mapa}"
else:
    fm = f
    titulo_mapa = "Valor FOB por estado - Todos los productos"

geo_estado = (
    fm.groupby("SG_UF_NCM", as_index=False)
    .agg(
        VL_FOB=("VL_FOB", "sum"),
        KG=("KG_LIQUIDO", "sum"),
        Estado=("Estado", "first"),
        Region=("Region", "first"),
    )
)
geo_estado = geo_estado.rename(columns={"SG_UF_NCM": "sigla"})

fig_mapa = px.choropleth(
    geo_estado,
    geojson=geojson,
    locations="sigla",
    featureidkey="properties.sigla",
    color="VL_FOB",
    color_continuous_scale="RdYlGn",
    hover_name="Estado",
    hover_data={
        "VL_FOB": ":,.0f",
        "KG": ":,.0f",
        "Region": True,
        "sigla": True,
    },
    labels={"VL_FOB": "US$ FOB", "KG": "Kg"},
)
fig_mapa.update_geos(fitbounds="locations", visible=False)
fig_mapa.update_layout(margin=dict(t=40, l=10, r=10, b=10), title=titulo_mapa)
st.plotly_chart(fig_mapa, use_container_width=True)

col_uf1, col_uf2 = st.columns([1, 1])
with col_uf1:
    st.markdown("**Ranking de estados (Valor FOB)**")
    g_uf = geo_estado.sort_values("VL_FOB", ascending=False).head(top_n)
    fig_uf = px.bar(
        g_uf.sort_values("VL_FOB"), x="VL_FOB", y="sigla", orientation="h",
        color="VL_FOB", color_continuous_scale="RdYlGn", text_auto=".2s",
    )
    fig_uf.update_layout(coloraxis_showscale=False, yaxis_title="Estado",
                         xaxis_title="US$ FOB")
    st.plotly_chart(fig_uf, use_container_width=True)

with col_uf2:
    st.markdown("**Mezcla de productos por estado (Top estados)**")
    tops = geo_estado.nlargest(top_n, "VL_FOB")["sigla"].tolist()
    fmix = (
        f[f["SG_UF_NCM"].isin(tops)]
        .groupby(["SG_UF_NCM", "Producto"], as_index=False)["VL_FOB"].sum()
    )
    fig_mix = px.bar(
        fmix, x="SG_UF_NCM", y="VL_FOB", color="Producto",
        color_discrete_sequence=COLORES, barmode="stack",
    )
    fig_mix.update_layout(xaxis_title="Estado", yaxis_title="US$ FOB", legend_title="")
    st.plotly_chart(fig_mix, use_container_width=True)

col_reg1, col_reg2 = st.columns([1, 1])
with col_reg1:
    st.markdown("**Valor FOB por región de Brasil**")
    g_reg = (
        fm.groupby("Region", as_index=False)["VL_FOB"].sum()
        .sort_values("VL_FOB")
    )
    fig_reg = px.bar(
        g_reg, x="VL_FOB", y="Region", orientation="h",
        color="Region", color_discrete_sequence=COLORES, text_auto=".2s",
    )
    fig_reg.update_layout(showlegend=False, yaxis_title="", xaxis_title="US$ FOB")
    st.plotly_chart(fig_reg, use_container_width=True)

with col_reg2:
    st.markdown("**Composición por producto en cada región**")
    g_regp = fm.groupby(["Region", "Producto"], as_index=False)["VL_FOB"].sum()
    fig_regp = px.bar(
        g_regp, x="Region", y="VL_FOB", color="Producto",
        color_discrete_sequence=COLORES, barmode="stack",
    )
    fig_regp.update_layout(xaxis_title="", yaxis_title="US$ FOB", legend_title="")
    st.plotly_chart(fig_regp, use_container_width=True)

st.markdown("---")
st.subheader("Detalle de la Base")
st.dataframe(
    f.sort_values("VL_FOB", ascending=False).head(500),
    use_container_width=True, height=380,
)
st.caption("Mostrando las 500 operaciones de mayor valor FOB según los filtros aplicados.")