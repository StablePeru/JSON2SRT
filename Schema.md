# Esquema del Proyecto JSON2SRT

## Estructura del Proyecto

```
project/
├── main.py                  # Punto de entrada de la aplicación
├── converter.py             # Lógica principal para la conversión JSON a SRT
├── utils/                   # Utilidades y herramientas auxiliares
│   ├── character_utils.py   # Gestión de personajes y códigos de color
│   ├── subtitle_rules.py    # Reglas y validaciones para subtítulos
│   ├── text_utils.py        # Procesamiento de texto
│   └── time_utils.py        # Conversiones de formato de tiempo
└── ui/                      # Interfaz de usuario
    └── qt_ui.py             # Implementación de la interfaz con PyQt5
```

## Componentes Principales

### 1. Interfaz de Usuario (ui/qt_ui.py)
- Implementa la interfaz gráfica usando PyQt5
- Gestiona la interacción del usuario
- Proporciona funcionalidades de arrastrar y soltar
- Muestra el progreso de la conversión
- Maneja la selección de archivos

### 2. Conversor Principal (converter.py)
- Coordina el proceso de conversión
- Lee y parsea archivos JSON
- Genera archivos SRT
- Integra las utilidades de procesamiento

### 3. Utilidades (utils/)

#### Character Utils (character_utils.py)
- Identifica personajes principales
- Asigna códigos de color:
  * Amarillo (<AN1>) - Personaje principal 1
  * Azul claro (<CN1>) - Personaje principal 2
  * Magenta (<MN1>) - Personaje principal 3
  * Verde (<VN1>) - Personaje principal 4
  * Blanco (<BN1>) - Personajes secundarios

#### Subtitle Rules (subtitle_rules.py)
- Define reglas de formato para subtítulos
- Valida la estructura de los subtítulos
- Aplica restricciones de formato

#### Text Utils (text_utils.py)
- Procesa y formatea texto
- Maneja caracteres especiales
- Aplica estilos y formatos

#### Time Utils (time_utils.py)
- Convierte formatos de tiempo
- Sincroniza tiempos de entrada/salida
- Ajusta FPS (Frames Por Segundo)

## Flujo de Datos

1. **Entrada**
   - Archivo JSON con subtítulos
   - Configuración de FPS

2. **Procesamiento**
   - Lectura y validación del JSON
   - Identificación de personajes
   - Asignación de colores
   - Conversión de tiempos
   - Formateo de texto

3. **Salida**
   - Archivo SRT con códigos de color
   - Subtítulos sincronizados
   - Personajes identificados

## Características Principales

- Conversión JSON a SRT
- Codificación de colores por personaje
- Interfaz drag & drop
- Personalización de FPS
- Barra de progreso
- Manejo de errores
- Validación de formato