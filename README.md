# JSON to SRT Converter

A simple and intuitive desktop application built with Python and PyQt5 that converts JSON subtitle files into SRT format, incorporating customizable color codes for easier identification of main characters.

## Features

- **JSON to SRT Conversion:** Convert JSON subtitle files into the widely supported SRT format.
- **Character Color Coding:** Automatically assigns color codes based on character prominence.
- **Drag and Drop Interface:** Intuitive drag-and-drop interface for quick file selection.
- **FPS Customization:** Adjust frames per second (FPS) to accurately convert subtitle timings.
- **Progress Feedback:** Visual progress bar indicating conversion status.
- **Error Handling:** Clear and informative error messages for user convenience.

## Files Structure

```
project/
├── main.py                  # Application entry point
├── converter.py             # Core logic for JSON to SRT conversion
├── character_utils.py       # Character counting and color code assignment
├── text_utils.py            # Text processing utilities
├── time_utils.py            # Time format conversions
└── ui/
    └── qt_ui.py             # PyQt5 user interface
```

## Installation

### Requirements

- Python 3.x
- PyQt5

### Installation Steps

Clone this repository:

```bash
git clone https://github.com/StablePeru/JSON2SRT.git
cd JSON2SRT
```

Install dependencies:

```bash
pip install PyQt5
```

## Usage

Launch the application by running:

```bash
python main.py
```

1. **Select JSON file:** Drag and drop a JSON file or browse using the "Examinar" button.
2. **Select output destination:** Choose where the converted SRT file will be saved.
3. **Set FPS (optional):** Default is set to 25, but you can adjust according to your needs.
4. **Convert:** Click "Convertir" to start the conversion.

## JSON Input Format

The application expects JSON files in either of the following formats:

```json
[
  {"IN": "hh:mm:ss:ff", "OUT": "hh:mm:ss:ff", "PERSONAJE": "CharacterName", "DIÁLOGO": "Dialogue text"},
  ...
]
```

or

```json
{
  "data": [
    {"IN": "hh:mm:ss:ff", "OUT": "hh:mm:ss:ff", "PERSONAJE": "CharacterName", "DIÁLOGO": "Dialogue text"},
    ...
  ]
}
```

## Output

The generated SRT file includes standard subtitle timing and text, enriched with Teletext color codes for improved readability and differentiation of main characters.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for new features, improvements, or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Developed by [StablePeru](https://github.com/StablePeru).

