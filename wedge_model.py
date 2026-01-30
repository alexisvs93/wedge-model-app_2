import numpy as np
import matplotlib.pyplot as plt

# Propiedades de las rocas [Vp (m/s), Rho (g/cc)]
capa_superior = [4992, 2.62] #para este ejercicio es la velocidad y densidad promedia del KI
capa_cuna = [4556, 2.51] #velocidades y densidades promedio a nivel de interes todo el intervalo del JST en el C-157
capa_inferior = [5639, 2.66] #velocidades y densidades promedio de Pardo-1 por falta de info en C-157

# Parámetros de la ondícula
frecuencia = 25 # Hz

# Parámetros de la geometría
tmax = 0.5  # s
dt = 0.001  # s
num_trazas = 10000
espesor_max_cuna = 200 #m

# --- PASO 2 a 6: CÁLCULOS (Sin cambios) ---
# (El código de cálculo va aquí, es el mismo que ya tienes)
tiempo = np.arange(0, tmax, dt)
modelo_capas = np.zeros((len(tiempo), num_trazas))
tope_cuna_tiempo = 0.2
espesores = np.linspace(espesor_max_cuna, 0, num_trazas)
base_cuna_tiempo = tope_cuna_tiempo + (2 * espesores / capa_cuna[0])
for i in range(num_trazas):
    modelo_capas[:, i] = np.where((tiempo > tope_cuna_tiempo) & (tiempo < base_cuna_tiempo[i]), 2,
                                  np.where(tiempo <= tope_cuna_tiempo, 1, 3))
vp = np.zeros_like(modelo_capas)
rho = np.zeros_like(modelo_capas)
vp[modelo_capas == 1] = capa_superior[0]; vp[modelo_capas == 2] = capa_cuna[0]; vp[modelo_capas == 3] = capa_inferior[0]
rho[modelo_capas == 1] = capa_superior[1]; rho[modelo_capas == 2] = capa_cuna[1]; rho[modelo_capas == 3] = capa_inferior[1]
ai = vp * rho
rc = (ai[1:, :] - ai[:-1, :]) / (ai[1:, :] + ai[:-1, :])
def ricker_wavelet(f, length=0.128, dt=0.001):
    t = np.arange(-length/2, length/2, dt)
    ricker = (1 - 2 * (np.pi**2) * (f**2) * (t**2)) * np.exp(-(np.pi**2) * (f**2) * (t**2))
    return ricker
ondicula = ricker_wavelet(frecuencia, dt=dt)
sismograma = np.zeros_like(rc)
for i in range(num_trazas):
    sismograma[:, i] = np.convolve(rc[:, i], ondicula, mode='same')

# --- EXTRACCIÓN DEL PICO MÁXIMO ---
ventana_inicio = tope_cuna_tiempo - 0.02
ventana_fin = tope_cuna_tiempo + 0.02
idx_inicio = int(ventana_inicio / dt)
idx_fin = int(ventana_fin / dt)
amplitudes_tope = [np.max(np.abs(sismograma[idx_inicio:idx_fin, i])) for i in range(num_trazas)]
idx_pico_maximo = np.argmax(amplitudes_tope)
espesor_tuning = espesores[idx_pico_maximo]
# print(f"El pico máximo de amplitud (espesor de sintonía) ocurre a: {espesor_tuning:.1f} m")


# --- VISUALIZACIÓN COMBINADA CON SUBPLOTS ---
# Se eliminó la gráfica anterior para generar una sola figura

# 1. Crear una figura con 2 subplots, uno al lado del otro
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7),
                               gridspec_kw={'width_ratios': [1, 1]})

fig.suptitle('Análisis del Modelo de Cuña y Curva de Sintonía', fontsize=16)

# --- Gráfica 1: Modelo de Cuña (Eje Izquierdo, ax1) ---
im = ax1.imshow(sismograma, aspect='auto', cmap='seismic_r', vmin=-.5, vmax=.5,
                extent=[espesores[0], espesores[-1], tmax-dt, 0])
ax1.axvline(espesor_tuning, color='black', linestyle='--', linewidth=2,
            label=f'Espesor de Sintonía ({espesor_tuning:.1f} m)')
ax1.set_title('Modelo de Cuña Sintético')
ax1.set_xlabel('Espesor de la Cuña (m)')
ax1.set_ylabel('Tiempo (s)')
ax1.legend()
ax1.invert_xaxis()
ax1.grid(True, alpha=.7, linestyle='--')

# --- Gráfica 2: Curva de Sintonía (Eje Derecho, ax2) ---
ax2.plot(espesores, amplitudes_tope, color='blue', label='Amplitud del Reflector')
ax2.axvline(espesor_tuning, color='black', linestyle='-',
            label=f'Pico Máximo ({espesor_tuning:.1f} m)')
ax2.set_title('Curva de Sintonía')
ax2.set_xlabel('Espesor de la Cuña (m)')
ax2.set_ylabel('Amplitud Máxima')
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend()
# ax2.invert_xaxis()

# Añadir una barra de color
fig.colorbar(im, ax=ax1, orientation='vertical', fraction=0.05, pad=0.02, label='Amplitud Sísmica')

# Ajustar el diseño y mostrar la figura completa
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

input("Presiona Enter para salir...)