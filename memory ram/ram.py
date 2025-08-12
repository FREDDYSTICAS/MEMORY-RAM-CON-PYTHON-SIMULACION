import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import json
import os

class Proceso:
    def __init__(self, id, tamano, tiempo_ejecucion):
        self.id = id
        self.tamano = tamano
        self.tiempo_ejecucion = tiempo_ejecucion
        self.tiempo_restante = tiempo_ejecucion
        self.color = self.generar_color_aleatorio()
    
    def generar_color_aleatorio(self):
        # Colores vibrantes pero no demasiado claros para que se pueda leer el texto
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def ejecutar(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            return True
        return False
    
    def __str__(self):
        return f"Proceso {self.id} ({self.tamano} KB, {self.tiempo_restante}/{self.tiempo_ejecucion}s)"

class Particion:
    def __init__(self, id, tamano):
        self.id = id
        self.tamano = tamano
        self.proceso = None
        self.fragmentacion_interna = 0
    
    def asignar_proceso(self, proceso):
        if proceso.tamano <= self.tamano:
            self.proceso = proceso
            self.fragmentacion_interna = self.tamano - proceso.tamano
            return True
        return False
    
    def liberar(self):
        proceso_liberado = self.proceso
        self.proceso = None
        self.fragmentacion_interna = 0
        return proceso_liberado
    
    def esta_libre(self):
        return self.proceso is None
    
    def __str__(self):
        estado = f"Libre ({self.tamano} KB)" if self.esta_libre() else f"{self.proceso} - Frag.Int: {self.fragmentacion_interna} KB"
        return f"Partición {self.id}: {estado}"

class AdministradorMemoria:
    def __init__(self):
        self.particiones = []
        self.cola_espera = []
        self.procesos_completados = []
        self.tiempo_actual = 0
        self.id_proceso = 1
        self.memoria_total = 0
    
    def crear_particiones(self, tamanos):
        self.particiones = []
        for i, tamano in enumerate(tamanos):
            self.particiones.append(Particion(i+1, tamano))
            self.memoria_total += tamano
    
    def crear_proceso(self, tamano, tiempo_ejecucion):
        proceso = Proceso(self.id_proceso, tamano, tiempo_ejecucion)
        self.id_proceso += 1
        return proceso
    
    def agregar_proceso_a_cola(self, proceso):
        self.cola_espera.append(proceso)
    
    def asignar_procesos(self):
        if not self.cola_espera:
            return False
        
        asignado = False
        procesos_no_asignados = []
        
        for proceso in self.cola_espera:
            proceso_ubicado = False
            
            # Primer ajuste: asignar al primer espacio donde quepa
            for particion in self.particiones:
                if particion.esta_libre() and proceso.tamano <= particion.tamano:
                    particion.asignar_proceso(proceso)
                    proceso_ubicado = True
                    asignado = True
                    break
            
            if not proceso_ubicado:
                procesos_no_asignados.append(proceso)
        
        self.cola_espera = procesos_no_asignados
        return asignado
    
    def ejecutar_tick(self):
        self.tiempo_actual += 1
        procesos_terminados = []
        
        for particion in self.particiones:
            if not particion.esta_libre():
                if not particion.proceso.ejecutar():  # Si el proceso terminó
                    proceso_terminado = particion.liberar()
                    self.procesos_completados.append(proceso_terminado)
                    procesos_terminados.append(proceso_terminado)
        
        return procesos_terminados
    
    def calcular_estadisticas(self):
        # Uso de memoria
        memoria_usada = sum(p.tamano for p in self.particiones if not p.esta_libre())
        porcentaje_uso = (memoria_usada / self.memoria_total) * 100 if self.memoria_total > 0 else 0
        
        # Fragmentación interna total
        fragmentacion_total = sum(p.fragmentacion_interna for p in self.particiones)
        porcentaje_fragmentacion = (fragmentacion_total / self.memoria_total) * 100 if self.memoria_total > 0 else 0
        
        # Procesos en espera
        procesos_espera = len(self.cola_espera)
        
        # Procesos completados
        procesos_finalizados = len(self.procesos_completados)
        
        return {
            "memoria_usada": memoria_usada,
            "porcentaje_uso": porcentaje_uso,
            "fragmentacion_total": fragmentacion_total,
            "porcentaje_fragmentacion": porcentaje_fragmentacion,
            "procesos_espera": procesos_espera,
            "procesos_finalizados": procesos_finalizados
        }
    
    def guardar_estado(self, filename="estado_memoria.json"):
        estado = {
            "tiempo_actual": self.tiempo_actual,
            "id_proceso": self.id_proceso,
            "memoria_total": self.memoria_total,
            "particiones": [
                {
                    "id": p.id,
                    "tamano": p.tamano,
                    "proceso": {
                        "id": p.proceso.id,
                        "tamano": p.proceso.tamano,
                        "tiempo_ejecucion": p.proceso.tiempo_ejecucion,
                        "tiempo_restante": p.proceso.tiempo_restante,
                        "color": p.proceso.color
                    } if p.proceso else None,
                    "fragmentacion_interna": p.fragmentacion_interna
                }
                for p in self.particiones
            ],
            "cola_espera": [
                {
                    "id": p.id,
                    "tamano": p.tamano,
                    "tiempo_ejecucion": p.tiempo_ejecucion,
                    "tiempo_restante": p.tiempo_restante,
                    "color": p.color
                }
                for p in self.cola_espera
            ],
            "procesos_completados": [
                {
                    "id": p.id,
                    "tamano": p.tamano,
                    "tiempo_ejecucion": p.tiempo_ejecucion,
                    "color": p.color
                }
                for p in self.procesos_completados
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(estado, f, indent=2)
    
    def cargar_estado(self, filename="estado_memoria.json"):
        if not os.path.exists(filename):
            return False
            
        try:
            with open(filename, 'r') as f:
                estado = json.load(f)
            
            self.tiempo_actual = estado["tiempo_actual"]
            self.id_proceso = estado["id_proceso"]
            self.memoria_total = estado["memoria_total"]
            
            # Recrear particiones
            self.particiones = []
            for p_data in estado["particiones"]:
                particion = Particion(p_data["id"], p_data["tamano"])
                if p_data["proceso"]:
                    proceso_data = p_data["proceso"]
                    proceso = Proceso(proceso_data["id"], proceso_data["tamano"], proceso_data["tiempo_ejecucion"])
                    proceso.tiempo_restante = proceso_data["tiempo_restante"]
                    proceso.color = proceso_data["color"]
                    particion.asignar_proceso(proceso)
                    particion.fragmentacion_interna = p_data["fragmentacion_interna"]
                self.particiones.append(particion)
            
            # Recrear cola de espera
            self.cola_espera = []
            for p_data in estado["cola_espera"]:
                proceso = Proceso(p_data["id"], p_data["tamano"], p_data["tiempo_ejecucion"])
                proceso.tiempo_restante = p_data["tiempo_restante"]
                proceso.color = p_data["color"]
                self.cola_espera.append(proceso)
            
            # Recrear procesos completados
            self.procesos_completados = []
            for p_data in estado["procesos_completados"]:
                proceso = Proceso(p_data["id"], p_data["tamano"], p_data["tiempo_ejecucion"])
                proceso.tiempo_restante = 0
                proceso.color = p_data["color"]
                self.procesos_completados.append(proceso)
                
            return True
        except Exception as e:
            print(f"Error cargando estado: {e}")
            return False


class SimuladorMemoriaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Administración de Memoria RAM")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")
        
        self.admin_memoria = AdministradorMemoria()
        
        # Variables para controlar la simulación
        self.ejecutando_auto = False
        self.velocidad_auto = 1.0  # segundos entre ticks
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pestañas
        self.tab_control = ttk.Notebook(main_frame)
        
        # Pestaña de Configuración
        self.tab_config = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_config, text='Configuración')
        
        # Pestaña de Simulación
        self.tab_simulacion = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_simulacion, text='Simulación')
        
        # Pestaña de Estadísticas
        self.tab_estadisticas = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_estadisticas, text='Estadísticas')
        
        self.tab_control.pack(expand=1, fill=tk.BOTH)
        
        # Configurar el contenido de cada pestaña
        self.configurar_tab_config()
        self.configurar_tab_simulacion()
        self.configurar_tab_estadisticas()
        
        # Estilo de los botones
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        
        # Verificar si hay un estado guardado
        if self.admin_memoria.cargar_estado():
            self.actualizar_visualizaciones()
            self.tab_control.select(1)  # Cambiar a la pestaña de simulación
    
    def configurar_tab_config(self):
        config_frame = ttk.Frame(self.tab_config, padding="20")
        config_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo_lbl = ttk.Label(config_frame, text="Configuración de Particiones de Memoria", 
                          font=("Arial", 16, "bold"))
        titulo_lbl.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Frame para particiones
        part_frame = ttk.LabelFrame(config_frame, text="Particiones de Memoria", padding="10")
        part_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(part_frame, text="Número de particiones:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_particiones_var = tk.StringVar(value="5")
        num_particiones_entry = ttk.Entry(part_frame, textvariable=self.num_particiones_var, width=10)
        num_particiones_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(part_frame, text="Generar campos", command=self.generar_campos_particiones).grid(
            row=0, column=2, padx=5, pady=5)
        
        self.particiones_frame = ttk.Frame(part_frame)
        self.particiones_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        self.tamanos_entries = []
        
        # Por defecto generar 5 campos
        self.generar_campos_particiones()
        
        # Frame para plantillas pre-configuradas
        plantillas_frame = ttk.LabelFrame(config_frame, text="Plantillas Predefinidas", padding="10")
        plantillas_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        ttk.Button(plantillas_frame, text="Sistema Pequeño", 
                  command=lambda: self.cargar_plantilla([32, 64, 128, 256])).grid(
            row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Button(plantillas_frame, text="Sistema Mediano", 
                  command=lambda: self.cargar_plantilla([64, 128, 256, 512, 1024])).grid(
            row=1, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Button(plantillas_frame, text="Sistema Grande", 
                  command=lambda: self.cargar_plantilla([128, 256, 512, 1024, 2048, 4096])).grid(
            row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Botón para iniciar simulación
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Iniciar Simulación", style='Accent.TButton',
                  command=self.iniciar_simulacion).pack(pady=10, ipadx=20, ipady=5)
    
    def configurar_tab_simulacion(self):
        sim_frame = ttk.Frame(self.tab_simulacion, padding="10")
        sim_frame.pack(fill=tk.BOTH, expand=True)
        
        # División en panel izquierdo y derecho
        panel_izq = ttk.Frame(sim_frame)
        panel_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        panel_der = ttk.Frame(sim_frame)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Panel izquierdo: Visualización de memoria y controles
        # Visualización gráfica de la memoria
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=panel_izq)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Controles de simulación
        controles_frame = ttk.LabelFrame(panel_izq, text="Controles de Simulación", padding="10")
        controles_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Fila 1: Tick único y automático
        ttk.Button(controles_frame, text="Ejecutar 1 Tick", 
                  command=self.ejecutar_tick).grid(row=0, column=0, padx=5, pady=5)
        
        self.btn_auto = ttk.Button(controles_frame, text="Iniciar Auto", 
                                  command=self.toggle_auto)
        self.btn_auto.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(controles_frame, text="Velocidad:").grid(row=0, column=2, padx=5, pady=5)
        
        self.velocidad_var = tk.DoubleVar(value=1.0)
        velocidad_scale = ttk.Scale(controles_frame, from_=0.1, to=2.0, 
                                   variable=self.velocidad_var, orient=tk.HORIZONTAL,
                                   length=100)
        velocidad_scale.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(controles_frame, textvariable=tk.StringVar(value="x")).grid(row=0, column=4)
        
        # Fila 2: Indicador de tiempo
        ttk.Label(controles_frame, text="Tiempo actual:").grid(row=1, column=0, padx=5, pady=5)
        
        self.tiempo_var = tk.StringVar(value="0s")
        ttk.Label(controles_frame, textvariable=self.tiempo_var, font=("Arial", 12, "bold")).grid(
            row=1, column=1, padx=5, pady=5)
        
        # Guardar/Cargar
        ttk.Button(controles_frame, text="Guardar Estado", 
                  command=lambda: self.admin_memoria.guardar_estado()).grid(
            row=1, column=2, padx=5, pady=5)
        
        ttk.Button(controles_frame, text="Cargar Estado", 
                  command=self.cargar_estado).grid(
            row=1, column=3, padx=5, pady=5)
        
        # Panel derecho: Procesos y cola
        # Creación de procesos
        crear_proceso_frame = ttk.LabelFrame(panel_der, text="Crear Proceso", padding="10")
        crear_proceso_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(crear_proceso_frame, text="Tamaño (KB):").grid(row=0, column=0, padx=5, pady=5)
        self.tamano_proceso_var = tk.StringVar(value="50")
        ttk.Entry(crear_proceso_frame, textvariable=self.tamano_proceso_var, width=10).grid(
            row=0, column=1, padx=5, pady=5)
        
        ttk.Label(crear_proceso_frame, text="Tiempo (s):").grid(row=0, column=2, padx=5, pady=5)
        self.tiempo_proceso_var = tk.StringVar(value="5")
        ttk.Entry(crear_proceso_frame, textvariable=self.tiempo_proceso_var, width=10).grid(
            row=0, column=3, padx=5, pady=5)
        
        ttk.Button(crear_proceso_frame, text="Crear Proceso", command=self.crear_proceso).grid(
            row=0, column=4, padx=5, pady=5)
        
        # Procesos en cola
        cola_frame = ttk.LabelFrame(panel_der, text="Cola de Procesos", padding="10")
        cola_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Lista para mostrar la cola de procesos
        self.cola_listbox = tk.Listbox(cola_frame, height=10)
        self.cola_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Información de las particiones
        particiones_frame = ttk.LabelFrame(panel_der, text="Estado de Particiones", padding="10")
        particiones_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Lista para mostrar las particiones
        self.particiones_listbox = tk.Listbox(particiones_frame, height=10)
        self.particiones_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def configurar_tab_estadisticas(self):
        stats_frame = ttk.Frame(self.tab_estadisticas, padding="20")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(stats_frame, text="Estadísticas de Uso de Memoria", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Panel de métricas básicas
        metricas_frame = ttk.LabelFrame(stats_frame, text="Métricas", padding="10")
        metricas_frame.pack(fill=tk.X, pady=10)
        
        # Uso de memoria
        uso_frame = ttk.Frame(metricas_frame)
        uso_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(uso_frame, text="Uso de Memoria:").pack(side=tk.LEFT, padx=5)
        self.uso_memoria_var = tk.StringVar(value="0 KB / 0 KB (0%)")
        ttk.Label(uso_frame, textvariable=self.uso_memoria_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Fragmentación
        frag_frame = ttk.Frame(metricas_frame)
        frag_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frag_frame, text="Fragmentación Interna:").pack(side=tk.LEFT, padx=5)
        self.fragmentacion_var = tk.StringVar(value="0 KB (0%)")
        ttk.Label(frag_frame, textvariable=self.fragmentacion_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Procesos
        proc_frame = ttk.Frame(metricas_frame)
        proc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(proc_frame, text="Procesos en Cola:").pack(side=tk.LEFT, padx=5)
        self.cola_var = tk.StringVar(value="0")
        ttk.Label(proc_frame, textvariable=self.cola_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        ttk.Label(proc_frame, text="Procesos Completados:").pack(side=tk.LEFT, padx=(20, 5))
        self.completados_var = tk.StringVar(value="0")
        ttk.Label(proc_frame, textvariable=self.completados_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Gráficas
        graficas_frame = ttk.Frame(stats_frame)
        graficas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Gráfico de uso de memoria
        self.fig_stats, (self.ax_uso, self.ax_frag) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas_stats = FigureCanvasTkAgg(self.fig_stats, master=graficas_frame)
        self.canvas_stats.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Inicializar gráficas
        self.ax_uso.set_title('Distribución de Memoria')
        self.ax_uso.set_xlabel('KB')
        self.ax_uso.set_ylabel('Particiones')
        
        self.ax_frag.set_title('Fragmentación Interna')
        self.ax_frag.set_xlabel('Partición')
        self.ax_frag.set_ylabel('KB')
        
        # Historial
        historial_frame = ttk.LabelFrame(stats_frame, text="Historial de Procesos Completados", padding="10")
        historial_frame.pack(fill=tk.X, pady=10)
        
        # Lista para mostrar los procesos completados
        self.completados_listbox = tk.Listbox(historial_frame, height=5)
        self.completados_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def generar_campos_particiones(self):
        # Limpiar frame
        for widget in self.particiones_frame.winfo_children():
            widget.destroy()
        
        try:
            num_particiones = int(self.num_particiones_var.get())
            if num_particiones <= 0:
                raise ValueError("El número debe ser positivo")
            
            self.tamanos_entries = []
            
            for i in range(num_particiones):
                ttk.Label(self.particiones_frame, text=f"Partición {i+1} (KB):").grid(
                    row=i, column=0, padx=5, pady=2, sticky="w")
                
                tamano_var = tk.StringVar(value=str((i+1)*128))  # Valores predeterminados crecientes
                entry = ttk.Entry(self.particiones_frame, textvariable=tamano_var, width=10)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky="w")
                
                self.tamanos_entries.append(tamano_var)
        
        except ValueError as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")
    
    def cargar_plantilla(self, tamanos):
        # Actualizar número de particiones
        self.num_particiones_var.set(str(len(tamanos)))
        self.generar_campos_particiones()
        
        # Establecer tamaños
        for i, tamano in enumerate(tamanos):
            if i < len(self.tamanos_entries):
                self.tamanos_entries[i].set(str(tamano))
    
    def iniciar_simulacion(self):
        try:
            # Obtener tamaños de particiones
            tamanos = []
            for entry_var in self.tamanos_entries:
                tamano = int(entry_var.get())
                if tamano <= 0:
                    raise ValueError("Todos los tamaños deben ser positivos")
                tamanos.append(tamano)
            
            # Crear particiones
            self.admin_memoria = AdministradorMemoria()
            self.admin_memoria.crear_particiones(tamanos)
            
            # Cambiar a la pestaña de simulación
            self.tab_control.select(1)
            
            # Actualizar visualizaciones
            self.actualizar_visualizaciones()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")
    
    def crear_proceso(self):
        try:
            tamano = int(self.tamano_proceso_var.get())
            tiempo = int(self.tiempo_proceso_var.get())
            
            if tamano <= 0 or tiempo <= 0:
                raise ValueError("El tamaño y tiempo deben ser positivos")
            
            # Crear proceso y añadirlo a la cola
            proceso = self.admin_memoria.crear_proceso(tamano, tiempo)
            self.admin_memoria.agregar_proceso_a_cola(proceso)
            
            # Intentar asignar procesos en cola
            self.admin_memoria.asignar_procesos()
            
            # Actualizar visualizaciones
            self.actualizar_visualizaciones()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")
    
    def ejecutar_tick(self):
        # Ejecutar un tick en el administrador de memoria
        procesos_terminados = self.admin_memoria.ejecutar_tick()
        
        # Intentar asignar procesos en cola
        self.admin_memoria.asignar_procesos()
        
        # Actualizar visualizaciones
        self.actualizar_visualizaciones()
        
        # Notificar sobre procesos terminados
        if procesos_terminados:
            ids = [p.id for p in procesos_terminados]
            messagebox.showinfo("Procesos Completados", 
                              f"Los procesos {', '.join(map(str, ids))} han terminado.")
    
    def toggle_auto(self):
        self.ejecutando_auto = not self.ejecutando_auto
        
        if self.ejecutando_auto:
            self.btn_auto.configure(text="Detener Auto")
            self.ejecutar_auto()
        else:
            self.btn_auto.configure(text="Iniciar Auto")
    
    def ejecutar_auto(self):
        if not self.ejecutando_auto:
            return
        
        # Ejecutar un tick
        self.ejecutar_tick()
        
        # Programar el siguiente tick
        velocidad = self.velocidad_var.get()
        self.root.after(int(velocidad * 1000), self.ejecutar_auto)
    
    def cargar_estado(self):
        if self.admin_memoria.cargar_estado():
            self.actualizar_visualizaciones()
            messagebox.showinfo("Carga Exitosa", "Estado cargado correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo cargar el estado.")
    
    def actualizar_visualizaciones(self):
        # Actualizar tiempo
        self.tiempo_var.set(f"{self.admin_memoria.tiempo_actual}s")
        
        # Actualizar visualización de particiones
        self.particiones_listbox.delete(0, tk.END)
        for particion in self.admin_memoria.particiones:
            self.particiones_listbox.insert(tk.END, str(particion))
        
        # Actualizar cola de procesos
        self.cola_listbox.delete(0, tk.END)
        for proceso in self.admin_memoria.cola_espera:
            self.cola_listbox.insert(tk.END, str(proceso))
        
        # Actualizar procesos completados
        self.completados_listbox.delete(0, tk.END)
        for proceso in self.admin_memoria.procesos_completados:
            self.completados_listbox.insert(tk.END, f"Proceso {proceso.id} ({proceso.tamano} KB, {proceso.tiempo_ejecucion}s)")
        
        # Actualizar estadísticas
        stats = self.admin_memoria.calcular_estadisticas()
        
        # Uso de memoria
        self.uso_memoria_var.set(f"{stats['memoria_usada']} KB / {self.admin_memoria.memoria_total} KB ({stats['porcentaje_uso']:.1f}%)")
        
        # Fragmentación
        self.fragmentacion_var.set(f"{stats['fragmentacion_total']} KB ({stats['porcentaje_fragmentacion']:.1f}%)")
        
        # Procesos
        self.cola_var.set(str(stats['procesos_espera']))
        self.completados_var.set(str(stats['procesos_finalizados']))
        
        # Actualizar gráficos
        self.actualizar_grafico_memoria()
        self.actualizar_grafico_estadisticas()
    
    def actualizar_grafico_memoria(self):
        # Limpiar gráfico
        self.ax.clear()
        
        # Configurar aspecto del gráfico
        self.ax.set_ylim(0, 1)
        self.ax.set_xlim(0, self.admin_memoria.memoria_total)
        self.ax.set_title('Estado de la Memoria RAM')
        self.ax.set_xlabel('Tamaño (KB)')
        self.ax.get_yaxis().set_visible(False)
        
        # Variables para el seguimiento
        pos_inicio = 0
        altura_bloque = 0.6
        y_pos = 0.2
        
        # Dibujar cada partición
        for particion in self.admin_memoria.particiones:
            # Rectángulo de la partición
            rect = patches.Rectangle((pos_inicio, y_pos - altura_bloque/2), 
                                    particion.tamano, altura_bloque,
                                    linewidth=1, edgecolor='black', facecolor='lightgray')
            self.ax.add_patch(rect)
            
            # Si hay un proceso en la partición
            if not particion.esta_libre():
                # Rectángulo del proceso
                proc_rect = patches.Rectangle((pos_inicio, y_pos - altura_bloque/2), 
                                             particion.proceso.tamano, altura_bloque,
                                             linewidth=0, facecolor=particion.proceso.color)
                self.ax.add_patch(proc_rect)
                
                # Etiqueta del proceso
                self.ax.text(pos_inicio + particion.proceso.tamano/2, y_pos, 
                            f"P{particion.proceso.id}\n{particion.proceso.tamano} KB",
                            ha='center', va='center', color='white', 
                            fontweight='bold', fontsize=10)
                
                # Mostrar fragmentación si existe
                if particion.fragmentacion_interna > 0:
                    # Línea punteada para separar proceso y fragmentación
                    self.ax.plot([pos_inicio + particion.proceso.tamano, pos_inicio + particion.proceso.tamano],
                                [y_pos - altura_bloque/2, y_pos + altura_bloque/2],
                                'k--', linewidth=1)
                    
                    # Etiqueta de fragmentación
                    self.ax.text(pos_inicio + particion.proceso.tamano + particion.fragmentacion_interna/2, y_pos,
                                f"Frag.\n{particion.fragmentacion_interna} KB",
                                ha='center', va='center', color='black', 
                                fontsize=8)
            else:
                # Etiqueta para partición libre
                self.ax.text(pos_inicio + particion.tamano/2, y_pos, 
                            f"Libre\n{particion.tamano} KB",
                            ha='center', va='center', color='black', 
                            fontweight='bold', fontsize=10)
            
            # Etiqueta de la partición
            self.ax.text(pos_inicio + particion.tamano/2, y_pos - altura_bloque/2 - 0.1,
                        f"Partición {particion.id}",
                        ha='center', va='center', color='black', fontsize=8)
            
            # Actualizar posición para la siguiente partición
            pos_inicio += particion.tamano
        
        # Actualizar el canvas
        self.canvas.draw()
    
    def actualizar_grafico_estadisticas(self):
        # Limpiar gráficos
        self.ax_uso.clear()
        self.ax_frag.clear()
        
        # Configurar títulos
        self.ax_uso.set_title('Distribución de Memoria')
        self.ax_frag.set_title('Fragmentación Interna')
        
        # Datos para gráficos
        particiones = [f"P{p.id}" for p in self.admin_memoria.particiones]
        tamanos = [p.tamano for p in self.admin_memoria.particiones]
        
        # Calcular uso real y fragmentación
        uso_real = []
        fragmentacion = []
        colores = []
        
        for p in self.admin_memoria.particiones:
            if p.esta_libre():
                uso_real.append(0)
                fragmentacion.append(0)
                colores.append('lightgray')
            else:
                uso_real.append(p.proceso.tamano)
                fragmentacion.append(p.fragmentacion_interna)
                colores.append(p.proceso.color)
        
        # Gráfico de barras apiladas para uso de memoria
        self.ax_uso.bar(particiones, tamanos, color='lightgray', label='Total')
        self.ax_uso.bar(particiones, uso_real, color=colores, label='Usado')
        
        # Gráfico de barras para fragmentación
        self.ax_frag.bar(particiones, fragmentacion, color='orange', label='Fragmentación')
        
        # Configurar etiquetas y leyendas
        self.ax_uso.set_xlabel('Particiones')
        self.ax_uso.set_ylabel('Tamaño (KB)')
        self.ax_uso.legend()
        
        self.ax_frag.set_xlabel('Particiones')
        self.ax_frag.set_ylabel('Tamaño (KB)')
        
        # Actualizar canvas
        self.fig_stats.tight_layout()
        self.canvas_stats.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorMemoriaGUI(root)
    root.mainloop()