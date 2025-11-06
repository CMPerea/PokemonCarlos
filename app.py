import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Cargar y preparar datos

@st.cache_data
def load_data():
    df = pd.read_csv("pokedex_enriquecida.csv")

    df.rename(columns={
        'Nombre': 'Name',
        'Tipo': 'Type',
        'Ataque': 'Attack',
        'Defensa': 'Defense',
        'Velocidad': 'Speed',
        'País': 'Country'
    }, inplace=True, errors="ignore")

    df["Sprite"] = df["ID"].apply(
        lambda x: f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{x}.png"
    )

    # Crear columna 'Generación'
    if "Generación" not in df.columns:
        df["Generación"] = pd.cut(
            df.index,
            bins=[0, 152, 252, 387, 494, 650, 722, 810, 890, 1010],
            labels=["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"],
            include_lowest=True
        )

    return df


df = load_data()

# Configuración general

st.set_page_config(page_title="Pokédex - Dashboard", layout="wide")

TYPE_COLORS = {
    "normal": "#A8A878",
    "fire": "#F08030",
    "water": "#6890F0",
    "grass": "#78C850",
    "electric": "#F8D030",
    "ice": "#98D8D8",
    "fighting": "#C03028",
    "poison": "#A040A0",
    "ground": "#E0C068",
    "flying": "#A890F0",
    "psychic": "#F85888",
    "bug": "#A8B820",
    "rock": "#B8A038",
    "ghost": "#705898",
    "dragon": "#7038F8",
    "dark": "#705848",
    "steel": "#B8B8D0",
    "fairy": "#EE99AC"
}


def get_color_for_type(type_str: str) -> str:
    if not isinstance(type_str, str):
        return "#DDDDDD"
    primary_type = type_str.split("/")[0].strip().lower()
    return TYPE_COLORS.get(primary_type, "#DDDDDD")



# Estilos 

st.markdown("""
    <style>
    .stApp {
        background: repeating-linear-gradient(
            135deg, #f5f6fa 0, #f5f6fa 5px, #fafafa 5px, #fafafa 20px
        );
        color: #1e1e1e;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Segoe UI', sans-serif;
    }
    .metric-card {
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .poke-card {
        border-radius: 15px;
        padding: 10px;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
        text-align: center;
    }
    .poke-card:hover { transform: scale(1.05); }
    h3, h4 {
        border-bottom: 2px solid #4D96FF;
        padding-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)


# Título y filtros avanzados

st.title("Pokédex - Dashboard Interactivo")
st.caption("Análisis comparativo de Pokémon por estadísticas, tipo, generación y país de origen.")

st.sidebar.header("Filtros de búsqueda")

# Filtro múltiple por tipo
types = sorted(df["Type"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect("Tipos de Pokémon", types)

# Filtro por país
countries = sorted(df["Country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("País", ["Todos"] + countries)

# Filtro por generación
generations = sorted(df["Generación"].dropna().unique().tolist())
selected_generation = st.sidebar.selectbox("Generación", ["Todas"] + list(generations))

# Filtro por rango de poder total
min_total, max_total = int(df["Total"].min()), int(df["Total"].max())
rango_total = st.sidebar.slider(
    "Rango de poder total",
    min_total, max_total, (min_total, max_total)
)

# Aplicar filtros
filtered_df = df.copy()

if selected_types:
    filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]

if selected_country != "Todos":
    filtered_df = filtered_df[filtered_df["Country"] == selected_country]

if selected_generation != "Todas":
    filtered_df = filtered_df[filtered_df["Generación"] == selected_generation]

filtered_df = filtered_df[
    (filtered_df["Total"] >= rango_total[0]) & (filtered_df["Total"] <= rango_total[1])
]

st.write(f"Mostrando {len(filtered_df)} Pokémon según los filtros aplicados.")


# Métricas 

st.markdown("### Pokémon destacados")

col1, col2, col3 = st.columns(3)

strongest = filtered_df.loc[filtered_df["Attack"].idxmax()]
defensive = filtered_df.loc[filtered_df["Defense"].idxmax()]
fastest = filtered_df.loc[filtered_df["Speed"].idxmax()]

metrics = [
    ("Mayor poder ofensivo", strongest, "Attack", col1),
    ("Mayor resistencia", defensive, "Defense", col2),
    ("Mayor velocidad", fastest, "Speed", col3)
]

for title, poke, stat_name, col in metrics:
    color = get_color_for_type(poke["Type"])
    stat_value = poke[stat_name]
    with col:
        st.markdown(
            f"""
            <div class="metric-card" style="background-color:{color}22;border:2px solid {color}">
                <h4>{title}</h4>
                <img src="{poke['Sprite']}" width="100">
                <h3>{poke['Name']}</h3>
                <p><b>{poke['Type']}</b></p>
                <p>{stat_name}: <b>{stat_value}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )


# Gráficas 

st.subheader("Análisis general de estadísticas")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.bar_chart(filtered_df[["Name", "Attack"]].set_index("Name"))

with col_g2:
    st.bar_chart(filtered_df[["Name", "Defense"]].set_index("Name"))

st.subheader("Promedio de poder por país")
avg_stats = df.groupby("Country")[["Attack", "Defense", "Speed"]].mean().sort_values("Attack", ascending=False)
st.bar_chart(avg_stats)


# Nuevas gráficas relevantes

st.subheader("Promedio de estadísticas por tipo")
avg_by_type = df.groupby("Type")[["Attack", "Defense", "Speed", "Total"]].mean().sort_values("Total", ascending=False)
st.bar_chart(avg_by_type)

st.subheader("Top 10 Pokémon con mayor poder total")
top10 = df.nlargest(10, "Total")[["Name", "Total"]].set_index("Name")
st.bar_chart(top10)

st.subheader("Relación entre ataque y defensa")
fig, ax = plt.subplots()
ax.scatter(filtered_df["Attack"], filtered_df["Defense"], alpha=0.6)
ax.set_xlabel("Ataque")
ax.set_ylabel("Defensa")
ax.set_title("Dispersión entre ataque y defensa")
st.pyplot(fig)


# Galería de Pokémon (filtrada por generación)

st.subheader("Galería de Pokémon")

if selected_generation != "Todas":
    filtered_df = filtered_df[filtered_df["Generación"] == selected_generation]

cols = st.columns(5)
for idx, row in enumerate(filtered_df.itertuples()):
    color = get_color_for_type(row.Type)
    with cols[idx % 5]:
        st.markdown(
            f"""
            <div class="poke-card" style="background-color:{color}22;border:1px solid {color};">
                <img src="{row.Sprite}" width="96">
                <h5>{row.Name}</h5>
                <p style='font-size:13px;'>
                    Ataque: {row.Attack} | Defensa: {row.Defense} | Velocidad: {row.Speed}<br>
                    <b style='color:{color}'>{row.Type}</b> | Gen {row.Generación}
                </p>
            </div>
            """, unsafe_allow_html=True
        )
