import streamlit as st
import pandas as pd
import altair as alt

# ⚠️ Obligatoire : doit être le premier appel Streamlit
st.set_page_config(page_title="Financial Deals Dashboard", page_icon="💰")

# ----------------------- CHARGEMENT DU FICHIER -----------------------
try:
    df = pd.read_excel("data/Data_stage.xlsm", sheet_name="F", header=1)
except Exception as e:
    st.stop()  # Ne pas afficher d'erreur avant set_page_config

# Nettoyage de base et vérif colonne
if 'Trade Date' not in df.columns:
    st.error("❌ La colonne 'Trade Date' est introuvable.")
    st.stop()

# Conversion des colonnes
df['Trade Date'] = pd.to_datetime(df['Trade Date'], errors='coerce')
df['Value date'] = pd.to_datetime(df.get('Value date'), errors='coerce')
df['Maturity'] = pd.to_datetime(df.get('Maturity'), errors='coerce')
df['Amount'] = pd.to_numeric(df.get('Amount'), errors='coerce')
df['Rate'] = pd.to_numeric(df.get('Rate'), errors='coerce')
df.dropna(subset=['Trade Date', 'Amount', 'Rate'], inplace=True)

# ----------------------- UI STREAMLIT -----------------------
st.title("💰 Financial Deals Dashboard")

# Filtres
min_date = df['Trade Date'].min()
max_date = df['Trade Date'].max()

date_range = st.slider("Select Trade Date Range:", min_value=min_date, max_value=max_date, value=(min_date, max_date))
selected_currency = st.multiselect("Select Currency:", options=df['Currency'].dropna().unique(), default=list(df['Currency'].dropna().unique()))
selected_type = st.multiselect("Select Deal Type:", options=df['Deal type'].dropna().unique(), default=list(df['Deal type'].dropna().unique()))

# Filtrage
filtered_df = df[
    (df['Trade Date'] >= date_range[0]) &
    (df['Trade Date'] <= date_range[1]) &
    (df['Currency'].isin(selected_currency)) &
    (df['Deal type'].isin(selected_type))
]

# ----------------------- KPI -----------------------
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Deals", len(filtered_df))
col2.metric("Total Amount", f"{filtered_df['Amount'].sum():,.0f}")
col3.metric("Average Rate (%)", f"{filtered_df['Rate'].mean():.2f}")

# ----------------------- GRAPHIQUE -----------------------
st.subheader("📈 Rate Over Time")

if filtered_df.empty:
    st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
else:
    chart = alt.Chart(filtered_df).mark_line(point=True).encode(
        x='Trade Date:T',
        y='Rate:Q',
        color='Currency:N',
        tooltip=['Trade Date:T', 'Currency:N', 'Rate:Q']
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

# ----------------------- TABLEAU -----------------------
st.subheader("📋 Data Table")
st.dataframe(filtered_df)

# ----------------------- EXPORT -----------------------
st.download_button("📥 Download Filtered Data", filtered_df.to_csv(index=False), file_name="filtered_deals.csv")
