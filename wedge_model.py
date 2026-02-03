import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analizador de Sintonía Sísmica", layout="wide")

st.title("📈 Analizador de Sintonía Sísmica (Wedge Model)")
st.write("Configura los parámetros en la barra lateral para actualizar el modelo en tiempo real.")

# --- Barra Lateral (Entradas) ---
st.sidebar.header("Propiedades de las Rocas")
v_sup = st.sidebar.number_input("Vp Superior (m/s)", value=4992)
rho_sup = st.sidebar.number_input("Rho Superior (g/cc)", value=2.62)

st.sidebar.markdown("---")
v_cuna = st.sidebar.number_input("Vp Cuña (m/s)", value=4556)
rho_cuna = st.sidebar.number_input("Rho Cuña (g/cc)", value=2.51)

st.sidebar.markdown("---")
v_inf = st.sidebar.number_input("Vp Inferior (m/s)", value=5639)
rho_inf = st.sidebar.number_input("Rho Inferior (g/cc)", value=2.66)

st.sidebar.header("Parámetros Sísmicos")
frec = st.sidebar.slider("Frecuencia (Hz)", 5, 100, 25)
esp_max = st.sidebar.slider("Espesor Máximo (m)", 10, 500, 200)

# --- Cálculos Geofísicos ---
tmax, dt = 0.5, 0.001
num_trazas = 500 # Streamlit es rápido, pero 500-1000 es ideal para web
tiempo = np.arange(0, tmax, dt)
espesores = np.linspace(esp_max, 0, num_trazas)
tope_cuna_tiempo = 0.2
base_cuna_tiempo = tope_cuna_tiempo + (2 * espesores / v_cuna)

# Vectorización
T, E = np.meshgrid(tiempo, base_cuna_tiempo, indexing='ij')
modelo = np.where(T <= tope_cuna_tiempo, 1, np.where(T < E, 2, 3))

ai = np.zeros_like(modelo)
ai[modelo == 1] = v_sup * rho_sup
ai[modelo == 2] = v_cuna * rho_cuna
ai[modelo == 3] = v_inf * rho_inf

rc = (ai[1:, :] - ai[:-1, :]) / (ai[1:, :] + ai[:-1, :])

# Ondícula Ricker
t_ric = np.arange(-0.064, 0.064, dt)
ondicula = (1 - 2*(np.pi**2)*(frec**2)*(t_ric**2)) * np.exp(-(np.pi**2)*(frec**2)*(t_ric**2))

sismograma = np.array([np.convolve(rc[:, i], ondicula, mode='same') for i in range(num_trazas)]).T

# Extracción de Amplitud (Ventana 40ms)
idx_i, idx_f = int(0.18/dt), int(0.22/dt)
amplitudes = np.max(np.abs(sismograma[idx_i:idx_f, :]), axis=0)
esp_tuning = espesores[np.argmax(amplitudes)]

# --- Visualización ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Modelo de Cuña")
    fig1, ax1 = plt.subplots()
    im = ax1.imshow(sismograma, aspect='auto', cmap='seismic_r', vmin=-.5, vmax=.5,
                    extent=[espesores[0], espesores[-1], tmax-dt, 0])
    ax1.axvline(esp_tuning, color='black', linestyle='--')
    ax1.set_ylabel("Tiempo (s)")
    ax1.set_xlabel("Espesor (m)")
    st.pyplot(fig1)

with col2:
    st.subheader("Curva de Sintonía")
    fig2, ax2 = plt.subplots()
    ax2.plot(espesores, amplitudes, color='blue')
    ax2.axvline(esp_tuning, color='red', label=f'Tuning: {esp_tuning:.2f}m')
    ax2.set_xlabel("Espesor (m)")
    ax2.set_ylabel("Amplitud Máxima")
    ax2.legend()
    st.pyplot(fig2)

st.success(output := f"El espesor de sintonía calculado es de **{esp_tuning:.2f} metros**.")






