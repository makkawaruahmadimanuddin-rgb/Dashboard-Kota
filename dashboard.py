import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi dasar Halaman
st.set_page_config(page_title="Dashboard Fiskal & Kesejahteraan", layout="wide")

# Judul Dashboard
st.title("📊 Dashboard Fiskal dan Kesejahteraan Kota")
st.markdown("Dashboard interaktif ini menampilkan ringkasan data pendapatan, belanja modal, dan indikator sosial-ekonomi kota.")

# Fungsi untuk memuat data (menggunakan cache agar loading aplikasi cepat)
@st.cache_data
def load_data():
    df = pd.read_csv("dataset_fiskal_97_hipoFull.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'dataset_fiskal_97_hipoFull.csv' tidak ditemukan. Pastikan file berada di folder yang sama dengan app.py")
    st.stop()

# --- SIDEBAR UNTUK FILTER ---
st.sidebar.header("Filter Data")
kota_list = df['Kota'].unique()
selected_kota = st.sidebar.selectbox("Pilih Kota", kota_list)

tahun_min = int(df['Tahun'].min())
tahun_max = int(df['Tahun'].max())
selected_tahun = st.sidebar.slider("Pilih Tahun untuk Indikator", tahun_min, tahun_max, tahun_max)

# Filter dataset berdasarkan pilihan user
df_kota = df[df['Kota'] == selected_kota]
df_kota_tahun = df_kota[df_kota['Tahun'] == selected_tahun]

# --- BARIS 1: KEY PERFORMANCE INDICATORS (KPI) ---
st.subheader(f"Indikator Utama: {selected_kota} (Tahun {selected_tahun})")
col1, col2, col3, col4 = st.columns(4)

with col1:
    pad_val = df_kota_tahun['PAD'].values[0] if not df_kota_tahun.empty else 0
    st.metric("Pendapatan Asli Daerah (PAD)", f"{pad_val:,.2f}")
with col2:
    ipm_val = df_kota_tahun['IPM'].values[0] if not df_kota_tahun.empty else 0
    st.metric("Indeks Pembangunan Manusia (IPM)", f"{ipm_val:,.2f}")
with col3:
    kemiskinan_val = df_kota_tahun['KEMISKINAN'].values[0] if not df_kota_tahun.empty else 0
    st.metric("Tingkat Kemiskinan (%)", f"{kemiskinan_val:,.2f}")
with col4:
    pe_val = df_kota_tahun['PE'].values[0] if not df_kota_tahun.empty else 0
    st.metric("Pertumbuhan Ekonomi (PE) (%)", f"{pe_val:,.2f}")

st.divider()

# --- BARIS 2: GRAFIK TREN KESEJAHTERAAN & PENDAPATAN ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Tren IPM & Kemiskinan")
    fig_tren = px.line(
        df_kota, x='Tahun', y=['IPM', 'KEMISKINAN'], 
        markers=True, 
        labels={'value': 'Nilai Indikator', 'variable': 'Indikator'}
    )
    st.plotly_chart(fig_tren, use_container_width=True)

with col_chart2:
    st.subheader(f"Proporsi Pendapatan ({selected_tahun})")
    if not df_kota_tahun.empty:
        # Kolom sumber pendapatan dari dataset
        pendapatan_cols = ['DBH_PAJAK', 'DBH_SDA', 'DBH_Lainnya', 'DAU_Grant', 'DAU_Earmark', 'DAK_Fisik', 'DAK_Nonfisik', 'PAD']
        pendapatan_data = df_kota_tahun[pendapatan_cols].T.reset_index()
        pendapatan_data.columns = ['Sumber', 'Nilai']
        
        fig_pie = px.pie(pendapatan_data, names='Sumber', values='Nilai', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Data tidak tersedia untuk tahun yang dipilih.")

# --- BARIS 3: GRAFIK BELANJA MODAL ---
st.subheader("Distribusi Belanja Modal per Tahun")
belanja_cols = ['bm_pendidikan', 'bm_kesehatan', 'bm_infrastruktur', 'bm_ekonomi', 'bm_perlindungan_sosial']
fig_belanja = px.bar(
    df_kota, x='Tahun', y=belanja_cols, barmode='group',
    labels={'value': 'Nilai Belanja Modal', 'variable': 'Sektor Belanja'}
)
st.plotly_chart(fig_belanja, use_container_width=True)