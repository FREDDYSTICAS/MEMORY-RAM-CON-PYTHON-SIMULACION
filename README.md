
# 💻 Simulación de Memoria RAM en Python

Este proyecto es una **simulación interactiva de memoria RAM** utilizando Python.  
Permite entender cómo se almacenan, modifican y liberan datos en memoria de forma visual y sencilla.

---

## 🚀 Características
- Representación gráfica o textual de bloques de memoria.
- Simulación de **asignación** y **liberación** de espacios.
- Personalización del tamaño total de la memoria.
- Ejecución en consola o con interfaz (dependiendo de la versión que uses).
- Código claro y comentado para fines educativos.

---

## 📂 Estructura del Proyecto
```

📁 memory-ram-simulation
├── main.py            # Script principal de la simulación
├── ram.py             # Lógica de la memoria RAM
├── utils.py           # Funciones auxiliares
├── requirements.txt   # Dependencias del proyecto
└── README.md          # Documentación

````

---

## ⚙️ Requisitos
Antes de ejecutar, asegúrate de tener instalado:
- Python 3.8 o superior
- Pip (administrador de paquetes de Python)

Instalar dependencias:
```bash
pip install -r requirements.txt
````

---

## ▶️ Ejecución

Ejecuta el proyecto con:

```bash
python main.py
```

Si quieres usar **modo recarga automática** (solo para desarrollo):

```bash
python -m memory_profiler main.py
```

---

## 🧠 Ejemplo Visual

La RAM se representa como bloques.
Los números indican el **ID del proceso** y `0` representa espacio libre.

```
[0][0][1][1][1][0][0][2][2][0]
```

**Leyenda:**

* `0` = Memoria libre
* `1` = Proceso 1
* `2` = Proceso 2

📊 Ejemplo gráfico en Markdown:

```
| 0 | 0 | 1 | 1 | 1 | 0 | 0 | 2 | 2 | 0 |
|---|---|---|---|---|---|---|---|---|---|
```

---

## 📊 Diagrama de Bloques de Memoria

![Diagrama de memoria](https://raw.githubusercontent.com/github/explore/main/topics/memory/memory.png)

*(La imagen es ilustrativa, no representa datos reales)*

---

## 📜 Licencia

Este proyecto está bajo la licencia MIT.
Si lo usas para tus clases o proyectos, ¡menciona la fuente! 😉

```

