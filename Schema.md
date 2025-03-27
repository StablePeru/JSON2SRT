# Documentación del Conversor JSON a SRT

## Descripción General
Este programa es una aplicación de escritorio diseñada para convertir archivos de subtítulos en formato JSON a formato SRT. Está desarrollada con Python y PyQt5, ofreciendo una interfaz gráfica intuitiva y fácil de usar.

## Características Principales

### Conversión de Formatos
- Convierte archivos JSON estructurados a formato SRT estándar
- Mantiene la precisión temporal en la conversión
- Preserva los estilos y formatos especiales del texto

### Interfaz de Usuario
- Interfaz gráfica intuitiva desarrollada con PyQt5
- Sistema de arrastrar y soltar para selección de archivos
- Barra de progreso visual durante la conversión
- Mensajes de error claros y descriptivos

### Gestión de Colores para Personajes
- Asignación automática de códigos de color basada en la prominencia de los personajes
- Facilita la identificación de diálogos por personaje
- Personalización de colores según preferencias

### Personalización de FPS
- Ajuste de cuadros por segundo (FPS) para sincronización precisa
- Garantiza la correcta temporización de los subtítulos

## Formato de Entrada (JSON)

### Estructura Esperada
```json
{
  "subtitles": [
    {
      "start": "00:01:23:10",
      "end": "00:01:25:15",
      "character": "Personaje1",
      "text": "Texto del subtítulo"
    }
  ]
}
```

### Campos Requeridos
- start: Tiempo de inicio en formato HH:MM:SS.mmm
- end: Tiempo de finalización en formato HH:MM:SS.mmm
- character: Nombre del personaje que habla
- text: Contenido del subtítulo

## Formato de Salida (SRT)

### Estructura del Archivo SRT
```
1
00:00:03,957 --> 00:00:06,290
<AN1>Texto correspondiente.

2
[siguiente subtítulo...]
```

### Características del Formato
- Numeración secuencial de subtítulos
- Marcas de tiempo en formato SRT estándar
- Códigos de color para identificar personajes
- Formato de texto enriquecido compatible

## Procesamiento de Texto

### Manejo de Caracteres Especiales
- Conversión automática de caracteres especiales
- Soporte para múltiples idiomas
- Preservación de formatos básicos

### Reglas de Formato
- Límite de caracteres por línea
- Mantenimiento de estilos de texto

## Gestión de Errores

### Validación de Entrada
- Verificación de formato JSON válido
- Comprobación de campos requeridos
- Validación de formato de tiempo

### Mensajes de Error
- Errores de formato de archivo
- Problemas de conversión de tiempo
- Errores de procesamiento de texto

## Características Adicionales

### Optimización de Rendimiento
- Procesamiento eficiente de archivos grandes
- Uso optimizado de memoria
- Conversión rápida y precisa

### Compatibilidad
- Compatible con reproductores multimedia estándar
- Soporte para diferentes codificaciones de texto
- Integración con sistemas de subtitulado existentes