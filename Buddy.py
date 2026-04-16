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
        self.title("PomoBuddy")
        self.overrideredirect(True) 
        self.attributes("-topmost", True)
        
        self.ancho_expandido = 220
        self.alto_expandido = 180
        self.ancho_colapsado = 60
        self.alto_colapsado = 60
        self.esta_expandido = True
        
        self.posicionar_ventana(self.ancho_expandido, self.alto_expandido)

        # 2. Variables de la Lógica del Pomodoro
        self.minutos_trabajo = 25
        self.minutos_descanso = 5
        
        # Convertimos a segundos para la lógica interna
        self.tiempo_trabajo = self.minutos_trabajo * 60 
        self.tiempo_descanso = self.minutos_descanso * 60
        self.tiempo_restante = self.tiempo_trabajo
        
        self.estado = "trabajo"
        self.corriendo = False
        self.hilo_temporizador = None

        # 3. Diseño de la Interfaz (UI)
        self.setup_ui()

    def posicionar_ventana(self, ancho, alto):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        margen = 20
        x = margen
        y = screen_height - alto - margen - 40
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.label_mascota = ctk.CTkLabel(self.main_frame, text="⏳", font=("Arial", 35))
        self.label_mascota.pack(pady=(15, 5))
        self.label_mascota.bind("<Button-1>", lambda event: self.conmutar_vista())

        self.label_tiempo = ctk.CTkLabel(
            self.main_frame, text=self.formatear_tiempo(self.tiempo_restante), font=("Consolas", 28, "bold")
        )
        self.label_tiempo.pack()

        self.boton_control = ctk.CTkButton(
            self.main_frame, text="Iniciar", command=self.controlar_temporizador, width=100, height=30
        )
        self.boton_control.pack(pady=10)
        
        # Botón de Configuración
        self.boton_config = ctk.CTkButton(
            self.main_frame, text="⚙️", command=self.abrir_configuracion,
            width=20, height=20, fg_color="transparent", text_color="gray"
        )
        self.boton_config.place(relx=0.1, rely=0.1, anchor="center")

        # Botón para cerrar la app
        self.boton_cerrar = ctk.CTkButton(
            self.main_frame, text="✕", command=self.destroy,
            width=20, height=20, fg_color="transparent", text_color="gray"
        )
        self.boton_cerrar.place(relx=0.9, rely=0.1, anchor="center")

    def conmutar_vista(self):
        if self.esta_expandido:
            self.posicionar_ventana(self.ancho_colapsado, self.alto_colapsado)
            self.label_tiempo.pack_forget()
            self.boton_control.pack_forget()
            self.boton_cerrar.place_forget()
            self.boton_config.place_forget()
            self.label_mascota.configure(font=("Arial", 45))
            self.esta_expandido = False
        else:
            self.posicionar_ventana(self.ancho_expandido, self.alto_expandido)
            self.label_mascota.pack(pady=(15, 5))
            self.label_mascota.configure(font=("Arial", 35))
            self.label_tiempo.pack()
            self.boton_control.pack(pady=10)
            self.boton_cerrar.place(relx=0.9, rely=0.1, anchor="center")
            self.boton_config.place(relx=0.1, rely=0.1, anchor="center")
            self.esta_expandido = True

    # --- Lógica de Configuración ---
    def abrir_configuracion(self):
        """Abre una ventana secundaria para editar los tiempos."""
        # Pausamos el temporizador si el usuario abre los ajustes
        if self.corriendo:
            self.controlar_temporizador()

        ventana_config = ctk.CTkToplevel(self)
        ventana_config.title("Ajustes")
        ventana_config.geometry("250x200")
        ventana_config.attributes("-topmost", True) # Mantenerla al frente también

        # Etiquetas y Entradas (Inputs)
        ctk.CTkLabel(ventana_config, text="Trabajo (minutos):").pack(pady=(10, 0))
        entrada_trabajo = ctk.CTkEntry(ventana_config, width=100)
        entrada_trabajo.insert(0, str(self.minutos_trabajo)) # Pone el valor actual
        entrada_trabajo.pack(pady=5)

        ctk.CTkLabel(ventana_config, text="Descanso (minutos):").pack(pady=(5, 0))
        entrada_descanso = ctk.CTkEntry(ventana_config, width=100)
        entrada_descanso.insert(0, str(self.minutos_descanso)) # Pone el valor actual
        entrada_descanso.pack(pady=5)

        def guardar_cambios():
            try:
                # Obtenemos el texto y lo convertimos a entero
                self.minutos_trabajo = int(entrada_trabajo.get())
                self.minutos_descanso = int(entrada_descanso.get())
                
                # Actualizamos los segundos
                self.tiempo_trabajo = self.minutos_trabajo * 60
                self.tiempo_descanso = self.minutos_descanso * 60
                
                # Reiniciamos el reloj actual
                self.estado = "trabajo"
                self.tiempo_restante = self.tiempo_trabajo
                self.label_tiempo.configure(text=self.formatear_tiempo(self.tiempo_restante))
                self.label_mascota.configure(text="⏳")
                self.main_frame.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
                
                ventana_config.destroy() # Cierra la ventana de config
            except ValueError:
                # Si el usuario escribe letras en vez de números, lo ignoramos por ahora
                print("Error: Por favor ingresa solo números.")

        ctk.CTkButton(ventana_config, text="Guardar", command=guardar_cambios).pack(pady=15)

    # --- Lógica del Temporizador (Sin cambios importantes) ---
    def formatear_tiempo(self, segundos):
        minutos = segundos // 60
        segundos = segundos % 60
        return f"{minutos:02}:{segundos:02}"

    def controlar_temporizador(self):
        if not self.corriendo:
            self.corriendo = True
            self.boton_control.configure(text="Pausar", fg_color="#E74C3C")
            if self.hilo_temporizador is None or not self.hilo_temporizador.is_alive():
                self.hilo_temporizador = threading.Thread(target=self.bucle_temporizador, daemon=True)
                self.hilo_temporizador.start()
        else:
            self.corriendo = False
            self.boton_control.configure(text="Continuar", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def bucle_temporizador(self):
        while self.corriendo and self.tiempo_restante > 0:
            time.sleep(1)
            self.after(0, self.actualizar_ui_temporizador)

        if self.tiempo_restante <= 0:
            self.after(0, self.cambiar_estado)

    def actualizar_ui_temporizador(self):
        if self.corriendo:
            self.tiempo_restante -= 1
            self.label_tiempo.configure(text=self.formatear_tiempo(self.tiempo_restante))

    def cambiar_estado(self):
        print("¡BEEP! Tiempo terminado.")
        if self.estado == "trabajo":
            self.estado = "descanso"
            self.tiempo_restante = self.tiempo_descanso
            self.label_mascota.configure(text="☕")
            self.main_frame.configure(fg_color="#27AE60") 
        else:
            self.estado = "trabajo"
            self.tiempo_restante = self.tiempo_trabajo
            self.label_mascota.configure(text="⏳")
            self.main_frame.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

        self.label_tiempo.configure(text=self.formatear_tiempo(self.tiempo_restante))
        
        if self.corriendo:
             self.hilo_temporizador = threading.Thread(target=self.bucle_temporizador, daemon=True)
             self.hilo_temporizador.start()

if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()