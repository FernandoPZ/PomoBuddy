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
        self.alto_expandido = 230
        self.ancho_colapsado = 60
        self.alto_colapsado = 60
        self.esta_expandido = True
        
        self.posicionar_ventana(self.ancho_expandido, self.alto_expandido)

        # 2. Variables de la Lógica del Pomodoro
        self.minutos_trabajo = 25
        self.minutos_descanso = 5
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
        """Configura los dos marcos (Pantalla Principal y Pantalla de Configuración)"""
        
        # --- PANTALLA 1: MARCO PRINCIPAL ---
        self.frame_principal = ctk.CTkFrame(self, corner_radius=15)
        
        self.label_mascota = ctk.CTkLabel(self.frame_principal, text="⏳", font=("Arial", 35))
        self.label_mascota.pack(pady=(20, 5))
        self.label_mascota.bind("<Button-1>", lambda event: self.conmutar_vista())

        self.label_tiempo = ctk.CTkLabel(
            self.frame_principal, text=self.formatear_tiempo(self.tiempo_restante), font=("Consolas", 28, "bold")
        )
        self.label_tiempo.pack()

        self.boton_control = ctk.CTkButton(
            self.frame_principal, text="Iniciar", command=self.controlar_temporizador, width=100, height=30
        )
        self.boton_control.pack(pady=10)
        
        self.boton_config = ctk.CTkButton(
            self.frame_principal, text="⚙️", command=self.mostrar_pantalla_config,
            width=20, height=20, fg_color="transparent", text_color="gray"
        )
        self.boton_config.place(relx=0.1, rely=0.08, anchor="center")

        self.boton_cerrar = ctk.CTkButton(
            self.frame_principal, text="✕", command=self.destroy,
            width=20, height=20, fg_color="transparent", text_color="gray"
        )
        self.boton_cerrar.place(relx=0.9, rely=0.08, anchor="center")

        # --- PANTALLA 2: MARCO DE CONFIGURACIÓN ---
        self.frame_config = ctk.CTkFrame(self, corner_radius=15)
        
        ctk.CTkLabel(self.frame_config, text="Ajustes", font=("Arial", 16, "bold")).pack(pady=(15, 10))
        
        ctk.CTkLabel(self.frame_config, text="Trabajo (minutos):").pack()
        self.entrada_trabajo = ctk.CTkEntry(self.frame_config, width=100, justify="center")
        self.entrada_trabajo.insert(0, str(self.minutos_trabajo))
        self.entrada_trabajo.pack(pady=(0, 10))

        ctk.CTkLabel(self.frame_config, text="Descanso (minutos):").pack()
        self.entrada_descanso = ctk.CTkEntry(self.frame_config, width=100, justify="center")
        self.entrada_descanso.insert(0, str(self.minutos_descanso))
        self.entrada_descanso.pack(pady=(0, 15))

        self.boton_guardar = ctk.CTkButton(
            self.frame_config, text="Guardar", command=self.guardar_cambios, width=100, height=30
        )
        self.boton_guardar.pack()

        # Botón para cancelar y volver sin guardar
        self.boton_volver = ctk.CTkButton(
            self.frame_config, text="←", command=self.mostrar_pantalla_principal,
            width=20, height=20, fg_color="transparent", text_color="gray"
        )
        self.boton_volver.place(relx=0.1, rely=0.08, anchor="center")

        # Mostramos la pantalla principal por defecto al iniciar
        self.frame_principal.pack(fill="both", expand=True, padx=5, pady=5)

    # --- Lógica de Cambio de Pantallas ---
    def mostrar_pantalla_config(self):
        """Oculta la pantalla principal y muestra los ajustes."""
        if self.corriendo:
            self.controlar_temporizador() # Pausa el tiempo si entras a config
            
        self.frame_principal.pack_forget()
        self.frame_config.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Actualizamos los inputs por si acaso
        self.entrada_trabajo.delete(0, 'end')
        self.entrada_trabajo.insert(0, str(self.minutos_trabajo))
        self.entrada_descanso.delete(0, 'end')
        self.entrada_descanso.insert(0, str(self.minutos_descanso))

    def mostrar_pantalla_principal(self):
        """Oculta los ajustes y vuelve a la pantalla principal."""
        self.frame_config.pack_forget()
        self.frame_principal.pack(fill="both", expand=True, padx=5, pady=5)

    def guardar_cambios(self):
        """Guarda los valores y vuelve a la pantalla principal."""
        try:
            self.minutos_trabajo = int(self.entrada_trabajo.get())
            self.minutos_descanso = int(self.entrada_descanso.get())
            
            self.tiempo_trabajo = self.minutos_trabajo * 60
            self.tiempo_descanso = self.minutos_descanso * 60
            
            # Reiniciamos el reloj
            self.estado = "trabajo"
            self.tiempo_restante = self.tiempo_trabajo
            self.label_tiempo.configure(text=self.formatear_tiempo(self.tiempo_restante))
            self.label_mascota.configure(text="⏳")
            self.frame_principal.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
            
            # Volvemos a la pantalla principal
            self.mostrar_pantalla_principal()
        except ValueError:
            print("Error: Por favor ingresa solo números.")

    # --- Lógica de Colapsar ---
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
            self.label_mascota.pack(pady=(20, 5))
            self.label_mascota.configure(font=("Arial", 35))
            self.label_tiempo.pack()
            self.boton_control.pack(pady=10)
            self.boton_cerrar.place(relx=0.9, rely=0.08, anchor="center")
            self.boton_config.place(relx=0.1, rely=0.08, anchor="center")
            self.esta_expandido = True

    # --- Lógica del Temporizador ---
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
            self.frame_principal.configure(fg_color="#27AE60") 
        else:
            self.estado = "trabajo"
            self.tiempo_restante = self.tiempo_trabajo
            self.label_mascota.configure(text="⏳")
            self.frame_principal.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

        self.label_tiempo.configure(text=self.formatear_tiempo(self.tiempo_restante))
        
        if self.corriendo:
             self.hilo_temporizador = threading.Thread(target=self.bucle_temporizador, daemon=True)
             self.hilo_temporizador.start()

if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()