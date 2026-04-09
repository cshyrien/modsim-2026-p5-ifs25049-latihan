import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
import time

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(page_title="Monte Carlo Proyek FITE", layout="wide")

# =========================
# STYLE SKY BLUE & RATA TENGAH
# =========================
st.markdown("""
<style>
/* Memastikan kontainer utama memiliki spasi yang rapi */
.block-container {
    padding-top: 2rem;
}
/* Style untuk kotak metrik */
.metric-box {
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    background: linear-gradient(135deg, #56ccf2, #2f80ed);
    margin-bottom: 20px;
}
/* Membantu rata tengah elemen teks umum jika diperlukan */
.center-text {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚙️ Konfigurasi Simulasi</h2>", unsafe_allow_html=True)

    n_simulasi = st.slider("Jumlah Iterasi", 1000, 50000, 10000, step=1000)

    st.markdown("<h3 style='text-align: center;'>📋 Tahapan Proyek (Bln)</h3>", unsafe_allow_html=True)

    def input_tahap(nama, default):
        with st.expander(f"🔹 {nama}"):
            low = st.number_input(f"{nama} Min", value=float(default[0]), step=0.5)
            mode = st.number_input(f"{nama} Most Likely", value=float(default[1]), step=0.5)
            high = st.number_input(f"{nama} Max", value=float(default[2]), step=0.5)
        return (low, mode, high)

    tahapan = {
        "Perencanaan": input_tahap("Perencanaan", (2.0, 3.0, 5.0)),
        "Desain": input_tahap("Desain", (3.0, 5.0, 7.0)),
        "Pengadaan": input_tahap("Pengadaan", (2.0, 4.0, 6.0)),
        "Konstruksi": input_tahap("Konstruksi", (6.0, 10.0, 14.0)),
        "Instalasi": input_tahap("Instalasi", (3.0, 5.0, 8.0)),
        "Finishing": input_tahap("Finishing", (2.0, 4.0, 6.0)),
    }

    st.markdown("<h3 style='text-align: center;'>⚡ Resource</h3>", unsafe_allow_html=True)
    percepatan = st.slider("Percepatan Konstruksi (%)", 0, 50, 0)

    run = st.button("🚀 Run Simulation", use_container_width=True, type="primary")

# =========================
# MAIN
# =========================
# Menggunakan HTML tag agar Judul rata tengah
st.markdown("<h1 style='text-align: center;'>📊 Dashboard Monte Carlo Proyek FITE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Simulasi estimasi durasi proyek secara real-time berdasarkan probabilitas.</p>", unsafe_allow_html=True)

if run:
    hasil = []
    kontribusi = {k: [] for k in tahapan}
    batch_size = 500

    placeholder = st.empty()
    progress = st.progress(0)

    # =========================
    # SIMULASI BERJALAN
    # =========================
    for i in range(0, n_simulasi, batch_size):
        
        batch_total = np.zeros(batch_size)
        
        for nama, tahap in tahapan.items():
            low, mode, high = tahap

            if nama == "Konstruksi":
                factor = 1 - (percepatan / 100)
                low, mode, high = low * factor, mode * factor, high * factor

            durasi_tahap = np.random.triangular(low, mode, high, size=batch_size)
            batch_total += durasi_tahap
            kontribusi[nama].extend(durasi_tahap)

        hasil.extend(batch_total)

        current_progress = min((i + batch_size) / n_simulasi, 1.0)
        progress.progress(current_progress)

        # Update grafik live
        df_live = pd.DataFrame({"Durasi": hasil})
        fig_live = px.histogram(
            df_live,
            x="Durasi",
            nbins=40,
            title=f"Simulasi berjalan ({len(hasil):,} data)",
            color_discrete_sequence=['#56ccf2']
        )
        # Tambahkan title_x=0.5 agar judul grafik rata tengah
        fig_live.update_layout(
            title_x=0.5, 
            xaxis_title="Durasi (Bulan)", 
            yaxis_title="Frekuensi", 
            margin=dict(t=40, b=0, l=0, r=0)
        )
        placeholder.plotly_chart(fig_live, use_container_width=True)
        
        time.sleep(0.05)

    hasil = np.array(hasil)

    # =========================
    # STATISTIK
    # =========================
    mean = np.mean(hasil)
    median = np.median(hasil)
    std = np.std(hasil)

    # Disesuaikan agar hasil probabilitas tidak 0%
    prob_30 = np.mean(hasil <= 30)
    prob_32 = np.mean(hasil <= 32)
    prob_34 = np.mean(hasil <= 34)

    # =========================
    # METRIC SKY BLUE
    # =========================
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>📊 Ringkasan Hasil</h2><br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="metric-box">
    ⏱️ Rata-rata<br>{mean:.1f} bulan
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="metric-box">
    📍 Median<br>{median:.1f} bulan
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="metric-box">
    📉 Deviasi Standar<br>{std:.1f}
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="metric-box">
    🎯 Prob ≤32 bulan<br>{prob_32*100:.1f}%
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # GRAFIK FINAL & PROBABILITAS
    # =========================
    st.markdown("<br>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("<h3 style='text-align: center;'>📈 Distribusi Akhir</h3>", unsafe_allow_html=True)
        df = pd.DataFrame({"Durasi": hasil})
        fig_final = px.histogram(df, x="Durasi", nbins=50, color_discrete_sequence=['#2f80ed'])
        fig_final.add_vline(x=mean, line_dash="dash", line_color="orange", annotation_text="Mean")
        # Menghapus update_layout(title_x=0.5) untuk menghindari "undefined"
        st.plotly_chart(fig_final, use_container_width=True)

    with col_chart2:
        st.markdown("<h3 style='text-align: center;'>🎯 Probabilitas Penyelesaian</h3>", unsafe_allow_html=True)
        prob_df = pd.DataFrame({
            "Deadline": ["30 bulan", "32 bulan", "34 bulan"],
            "Probabilitas": [prob_30*100, prob_32*100, prob_34*100]
        })
        fig_bar = px.bar(
            prob_df, x="Deadline", y="Probabilitas", 
            text=prob_df["Probabilitas"].apply(lambda x: f"{x:.1f}%"),
            color_discrete_sequence=['#56ccf2']
        )
        fig_bar.update_traces(textposition='outside')
        # Menghapus update_layout(title_x=0.5) untuk menghindari "undefined"
        fig_bar.update_yaxes(range=[0, 110]) 
        st.plotly_chart(fig_bar, use_container_width=True)

    # =========================
    # KONTRIBUSI
    # =========================
    st.markdown("<br><h3 style='text-align: center;'>📊 Rata-rata Kontribusi Durasi Tiap Tahap</h3>", unsafe_allow_html=True)

    avg_kontribusi = {k: np.mean(v) for k, v in kontribusi.items()}
    df_kontribusi = pd.DataFrame({
        "Tahap": list(avg_kontribusi.keys()),
        "Durasi": list(avg_kontribusi.values())
    })

    df_kontribusi = df_kontribusi.sort_values(by="Durasi", ascending=False)

    fig_kontribusi = px.bar(
        df_kontribusi, x="Tahap", y="Durasi",
        text=df_kontribusi["Durasi"].apply(lambda x: f"{x:.1f} bln"),
        color_discrete_sequence=['#2f80ed']
    )
    fig_kontribusi.update_traces(textposition='outside')
    # Menghapus update_layout(title_x=0.5) untuk menghindari "undefined"
    fig_kontribusi.update_yaxes(range=[0, max(df_kontribusi["Durasi"])*1.2])
    st.plotly_chart(fig_kontribusi, use_container_width=True)
