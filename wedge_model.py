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

        # --- Parámetros fijos ---
        tmax, dt, num_trazas = 0.5, 0.001, 500 # Reducido para mayor fluidez en GUI
        
        # --- Cálculos Geofísicos ---
        tiempo = np.arange(0, tmax, dt)
        espesores = np.linspace(esp_max, 0, num_trazas)
        tope_cuna_tiempo = 0.2
        base_cuna_tiempo = tope_cuna_tiempo + (2 * espesores / v_cuna)
        
        modelo_capas = np.zeros((len(tiempo), num_trazas))
        for i in range(num_trazas):
            modelo_capas[:, i] = np.where((tiempo > tope_cuna_tiempo) & (tiempo < base_cuna_tiempo[i]), 2,
                                         np.where(tiempo <= tope_cuna_tiempo, 1, 3))
        
        vp = np.zeros_like(modelo_capas)
        rho = np.zeros_like(modelo_capas)
        vp[modelo_capas == 1], rho[modelo_capas == 1] = v_sup, rho_sup
        vp[modelo_capas == 2], rho[modelo_capas == 2] = v_cuna, rho_cuna
        vp[modelo_capas == 3], rho[modelo_capas == 3] = v_inf, rho_inf
        
        ai = vp * rho
        rc = (ai[1:, :] - ai[:-1, :]) / (ai[1:, :] + ai[:-1, :])
        
        t_ric = np.arange(-0.064, 0.064, dt)
        ondicula = (1 - 2*(np.pi**2)*(frec**2)*(t_ric**2)) * np.exp(-(np.pi**2)*(frec**2)*(t_ric**2))
        
        sismograma = np.zeros_like(rc)
        for i in range(num_trazas):
            sismograma[:, i] = np.convolve(rc[:, i], ondicula, mode='same')

        # --- Extracción de Tuning ---
        idx_i, idx_f = int(0.18/dt), int(0.25/dt)
        amplitudes = [np.max(np.abs(sismograma[idx_i:idx_f, i])) for i in range(num_trazas)]
        esp_tuning = espesores[np.argmax(amplitudes)]

        # --- Actualizar Gráficas ---
        ax1.clear()
        ax2.clear()
        
        im = ax1.imshow(sismograma, aspect='auto', cmap='seismic_r', vmin=-.5, vmax=.5,
                        extent=[espesores[0], espesores[-1], tmax-dt, 0])
        ax1.axvline(esp_tuning, color='black', linestyle='--')
        ax1.set_title('Modelo de Cuña')
        ax1.invert_xaxis()
        
        ax2.plot(espesores, amplitudes, color='blue')
        ax2.axvline(esp_tuning, color='red', label=f'Tuning: {esp_tuning:.1f}m')
        ax2.set_title('Curva de Sintonía')
        ax2.legend()
        
        canvas.draw()
    except Exception as e:
        tk.messagebox.showerror("Error", f"Verifica los datos ingresados: {e}")

# --- Configuración de la Ventana Principal ---
root = tk.Tk()
root.title("Analizador de Sintonía Sísmica")
root.geometry("1100x700")

# Panel Lateral de Entradas
frame_ctrl = ttk.Frame(root, padding="10")
frame_ctrl.pack(side=tk.LEFT, fill=tk.Y)

def crear_entrada(label, default, row):
    ttk.Label(frame_ctrl, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
    ent = ttk.Entry(frame_ctrl)
    ent.insert(0, default)
    ent.grid(row=row, column=1, pady=2)
    return ent

ent_v_sup = crear_entrada("Vp Superior (m/s):", "4992", 0)
ent_r_sup = crear_entrada("Rho Superior (g/cc):", "2.62", 1)
ent_v_cuna = crear_entrada("Vp Cuña (m/s):", "4556", 2)
ent_r_cuna = crear_entrada("Rho Cuña (g/cc):", "2.51", 3)
ent_v_inf = crear_entrada("Vp Inferior (m/s):", "5639", 4)
ent_r_inf = crear_entrada("Rho Inferior (g/cc):", "2.66", 5)
ent_frec = crear_entrada("Frecuencia (Hz):", "25", 6)
ent_esp = crear_entrada("Espesor Máx (m):", "200", 7)

btn_calc = ttk.Button(frame_ctrl, text="Calcular Modelo", command=calcular_y_graficar)
btn_calc.grid(row=8, column=0, columnspan=2, pady=20)

# Área de Gráficas
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

calcular_y_graficar() # Ejecución inicial
root.mainloop()




