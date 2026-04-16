import tkinter as tk
import customtkinter as ctk
import threading
import time

# --- Configuración Visual ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class PomodoroApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Configuración de la Ventana Flotante
        self.title("Pomodoro")
        # Elimina los bordes de la ventana (título, minimizar, cerrar)
        self.overrideredirect(True) 
        # Mantiene la ventana siempre encima de otras
        self.attributes("-topmost", True)
        
        # Dimensiones de la aplicación
        self.ancho_expandido = 220
        self.alto_expandido = 180
        self.ancho_colapsado = 60
        self.alto_colapsado = 60
        
        # Estado de la ventana
        self.esta_expandido = True
        
        # Posicionar la ventana en la esquina inferior izquierda
        self.posicionar_ventana(self.ancho_expandido, self.alto_expandido)

        # 2. Variables de la Lógica del Pomodoro
        self.tiempo_trabajo = 5 
        self.tiempo_descanso = 2
        self.tiempo_restante = self.tiempo_trabajo
        self.estado = "trabajo"
        self.corriendo = False
        self.hilo_temporizador = None

        # 3. Diseño de la Interfaz (UI)
        self.setup_ui()

    def posicionar_ventana(self, ancho, alto):
        """Calcula las coordenadas para la esquina inferior izquierda."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Margen desde la esquina
        margen = 20
        
        # X es el margen, Y es la altura total menos el alto de la app y el margen
        x = margen
        y = screen_height - alto - margen - 40 # -40 suele ser la barra de tareas
        
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def setup_ui(self):
        """Configura los elementos gráficos dentro de la ventana."""
        
        # Contenedor principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Zona de la Mascota/Emoji (Hacer clic aquí colapsa la app) ---
        self.label_mascota = ctk.CTkLabel(
            self.main_frame, 
            text="⏳", # Emoji inicial de trabajo
            font=("Arial", 35)
        )
        self.label_mascota.pack(pady=(15, 5))
        # Vincular el clic izquierdo a la función de colapsar
        self.label_mascota.bind("<Button-1>", lambda event: self.conmutar_vista())

        # --- Zona del Temporizador ---
        self.label_tiempo = ctk.CTkLabel(
            self.main_frame, 
            text=self.formatear_tiempo(self.tiempo_restante),
            font=("Consolas", 28, "bold")
        )
        self.label_tiempo.pack()

        # --- Botones de Control ---
        self.boton_control = ctk.CTkButton(
            self.main_frame, 
            text="Iniciar", 
            command=self.controlar_temporizador,
            width=100,
            height=30
        )
        self.boton_control.pack(pady=10)
        
        # Botón pequeño para cerrar la app (ya que no hay bordes)
        self.boton_cerrar = ctk.CTkButton(
            self.main_frame,
            text="✕",
            command=self.destroy,
            width=20,
            height=20,
            fg_color="transparent",
            text_color="gray"
        )
        # Posicionamiento absoluto en la esquina superior derecha del frame
        self.boton_cerrar.place(relx=0.9, rely=0.1, anchor="center")

    def conmutar_vista(self):
        """Cambia entre la vista completa y la vista de 'solo mascota'."""
        if self.esta_expandido:
            # Colapsar
            self.posicionar_ventana(self.ancho_colapsado, self.alto_colapsado)
            # Ocultar elementos (pady=0 para que no ocupen espacio)
            self.label_tiempo.pack_forget()
            self.boton_control.pack_forget()
            self.boton_cerrar.place_forget()
            # Agrandar el emoji un poco más
            self.label_mascota.configure(font=("Arial", 45))
            self.esta_expandido = False
        else:
            # Expandir
            self.posicionar_ventana(self.ancho_expandido, self.alto_expandido)
            # Volver a mostrar elementos en orden
            self.label_mascota.pack(pady=(15, 5))
            self.label_mascota.configure(font=("Arial", 35))
            self.label_tiempo.pack()
            self.boton_control.pack(pady=10)
            self.boton_cerrar.place(relx=0.9, rely=0.1, anchor="center")
            self.esta_expandido = True

    # --- Lógica del Temporizador con Hilos (Threading) ---
    def formatear_tiempo(self, segundos):
        """Convierte segundos a formato MM:SS."""
        minutos = segundos // 60
        segundos = segundos % 60
        return f"{minutos:02}:{segundos:02}"

    def controlar_temporizador(self):
        """Maneja el inicio y la pausa."""
        if not self.corriendo:
            self.corriendo = True
            self.boton_control.configure(text="Pausar", fg_color="#E74C3C") # Rojo
            # ¡Importante! Creamos un hilo para que no se congele la ventana
            if self.hilo_temporizador is None or not self.hilo_temporizador.is_alive():
                self.hilo_temporizador = threading.Thread(target=self.bucle_temporizador, daemon=True)
                self.hilo_temporizador.start()
        else:
            self.corriendo = False
            self.boton_control.configure(text="Continuar", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def bucle_temporizador(self):
        """Bucle que corre en segundo plano restando tiempo."""
        while self.corriendo and self.tiempo_restante > 0:
            time.sleep(1) # Espera 1 segundo
            
            # Como este hilo no es el principal, usamos .after para actualizar la UI
            self.after(0, self.actualizar_ui_temporizador)

        if self.tiempo_restante <= 0:
            # El tiempo terminó, cambiamos de estado
            self.after(0, self.cambiar_estado)

    def actualizar_ui_temporizador(self):
        """Actualiza el texto del reloj de forma segura."""
        if self.corriendo: # Verificamos de nuevo por si se pausó justo ahora
            self.tiempo_restante -= 1
            self.label_tiempo.configure(text=self.formatear_tiempo(self.tiempo_restante))

    def cambiar_estado(self):
        """Alterna entre trabajo y descanso e imprime sonidos (luego los pondremos de verdad)."""
        # Aquí imprimiríamos un sonido de alerta
        print("¡BEEP! Tiempo terminado.")
        
        if self.estado == "trabajo":
            self.estado = "descanso"
            self.tiempo_restante = self.tiempo_descanso
            self.label_mascota.configure(text="☕") # Emoji descanso
            # Color verde suave para descanso
            self.main_frame.configure(fg_color="#27AE60") 
        else:
            self.estado = "trabajo"
            self.tiempo_restante = self.tiempo_trabajo
            self.label_mascota.configure(text="⏳") # Emoji trabajo
            # Volver al color por defecto del frame
            self.main_frame.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

        self.label_tiempo.configure(text=self.formatear_tiempo(self.tiempo_restante))
        
        # Reiniciar bucle automáticamente
        if self.corriendo:
             self.hilo_temporizador = threading.Thread(target=self.bucle_temporizador, daemon=True)
             self.hilo_temporizador.start()

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()