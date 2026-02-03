import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

def calcular_y_graficar():
    try:
        # --- Obtener datos de la interfaz ---
        v_sup, rho_sup = float(ent_v_sup.get()), float(ent_r_sup.get())
        v_cuna, rho_cuna = float(ent_v_cuna.get()), float(ent_r_cuna.get())
        v_inf, rho_inf = float(ent_v_inf.get()), float(ent_r_inf.get())
        frec = float(ent_frec.get())
        esp_max = float(ent_esp.get())

        # --- Parámetros de alta resolución (Similares al Script 1) ---
        tmax, dt = 0.5, 0.001
        num_trazas = 10000  # Máxima precisión
        tiempo = np.arange(0, tmax, dt)
        espesores = np.linspace(esp_max, 0, num_trazas)
        tope_cuna_tiempo = 0.2
        
        # --- Cálculos Geofísicos Vectorizados ---
        base_cuna_tiempo = tope_cuna_tiempo + (2 * espesores / v_cuna)
        
        # Creamos una malla (grid) de tiempo para evitar el bucle for en la creación del modelo
        T, E = np.meshgrid(tiempo, base_cuna_tiempo, indexing='ij')
        modelo_capas = np.where(T <= tope_cuna_tiempo, 1, 
                               np.where(T < E, 2, 3))

        # Asignación de propiedades
        ai = np.zeros_like(modelo_capas)
        ai[modelo_capas == 1] = v_sup * rho_sup
        ai[modelo_capas == 2] = v_cuna * rho_cuna
        ai[modelo_capas == 3] = v_inf * rho_inf

        # Coeficientes de reflexión
        rc = (ai[1:, :] - ai[:-1, :]) / (ai[1:, :] + ai[:-1, :])

        # Ondícula Ricker Flexible (Script 1 style)
        def ricker(f, dt):
            length = 0.128
            t = np.arange(-length/2, length/2, dt)
            return (1 - 2*(np.pi**2)*(f**2)*(t**2)) * np.exp(-(np.pi**2)*(f**2)*(t**2))
        
        ondicula = ricker(frec, dt)

        # Convolución (Mantenemos el bucle pero es eficiente para 1D)
        sismograma = np.zeros_like(rc)
        for i in range(num_trazas):
            sismograma[:, i] = np.convolve(rc[:, i], ondicula, mode='same')

        # --- Extracción de Tuning (Ventana de 40ms) ---
        # Centrada en 0.2s (0.18s a 0.22s)
        idx_i, idx_f = int((tope_cuna_tiempo - 0.02)/dt), int((tope_cuna_tiempo + 0.02)/dt)
        amplitudes = np.max(np.abs(sismograma[idx_i:idx_f, :]), axis=0)
        idx_max = np.argmax(amplitudes)
        esp_tuning = espesores[idx_max]

        # --- Actualizar Gráficas ---
        ax1.clear()
        ax2.clear()

        # Visualización de Cuña
        im = ax1.imshow(sismograma, aspect='auto', cmap='seismic_r', vmin=-.5, vmax=.5,
                        extent=[espesores[0], espesores[-1], tmax-dt, 0])
        ax1.axvline(esp_tuning, color='black', linestyle='--', label=f'Tuning: {esp_tuning:.1f}m')
        ax1.set_title('Modelo de Cuña (Alta Resolución)')
        ax1.set_ylabel('Tiempo (s)')
        ax1.invert_xaxis()
        ax1.legend()

        # Curva de Sintonía
        ax2.plot(espesores, amplitudes, color='blue', lw=1.5)
        ax2.axvline(esp_tuning, color='red', linestyle='--', alpha=0.7)
        ax2.set_title(f'Curva de Sintonía (Pico: {esp_tuning:.2f} m)')
        ax2.set_xlabel('Espesor (m)')
        ax2.set_ylabel('Amplitud Máxima')
        ax2.grid(True, alpha=0.3)

        canvas.draw()
    except Exception as e:
        tk.messagebox.showerror("Error", f"Error en cálculo: {e}")

# --- Interfaz Gráfica ---
root = tk.Tk()
root.title("Analizador Geofísico de Sintonía (High-Res)")

frame_ctrl = ttk.Frame(root, padding="10")
frame_ctrl.pack(side=tk.LEFT, fill=tk.Y)

# Entradas simplificadas con valores por defecto del Script 1
campos = [
    ("Vp Sup (m/s)", "4992"), ("Rho Sup (g/cc)", "2.62"),
    ("Vp Cuña (m/s)", "4556"), ("Rho Cuña (g/cc)", "2.51"),
    ("Vp Inf (m/s)", "5639"), ("Rho Inf (g/cc)", "2.66"),
    ("Frecuencia (Hz)", "25"), ("Espesor Máx (m)", "200")
]

entries = {}
for i, (label, default) in enumerate(campos):
    ttk.Label(frame_ctrl, text=label).grid(row=i, column=0, sticky=tk.W)
    ent = ttk.Entry(frame_ctrl, width=10)
    ent.insert(0, default)
    ent.grid(row=i, column=1, pady=2, padx=5)
    entries[label] = ent

# Mapeo manual para el botón
ent_v_sup, ent_r_sup = entries["Vp Sup (m/s)"], entries["Rho Sup (g/cc)"]
ent_v_cuna, ent_r_cuna = entries["Vp Cuña (m/s)"], entries["Rho Cuña (g/cc)"]
ent_v_inf, ent_r_inf = entries["Vp Inf (m/s)"], entries["Rho Inf (g/cc)"]
ent_frec, ent_esp = entries["Frecuencia (Hz)"], entries["Espesor Máx (m)"]

btn_calc = ttk.Button(frame_ctrl, text="ACTUALIZAR MODELO", command=calcular_y_graficar)
btn_calc.grid(row=len(campos), column=0, columnspan=2, pady=20)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 6))
plt.subplots_adjust(wspace=0.3)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

calcular_y_graficar()
root.mainloop()
#Fin





