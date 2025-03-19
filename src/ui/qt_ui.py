"""
PyQt5-based user interface for the JSON to SRT converter.
"""
import os
import logging
# Update imports at the top of the file
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QProgressBar, 
                            QFileDialog, QMessageBox, QApplication, QFrame,
                            QSizePolicy, QSpacerItem, QStyle)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QMimeData
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QDragEnterEvent, QDropEvent, QIntValidator

# Import the converter function
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converter import process_json_to_srt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DropLineEdit(QLineEdit):
    """Custom QLineEdit that accepts drag and drop for files"""
    
    def __init__(self, parent=None, file_filter=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.file_filter = file_filter  # e.g., ".json"
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # Check if the file has the correct extension if filter is set
            if self.file_filter:
                for url in event.mimeData().urls():
                    if url.toLocalFile().endswith(self.file_filter):
                        event.acceptProposedAction()
                        return
            else:
                event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            
            # Check if the file has the correct extension if filter is set
            if self.file_filter and not file_path.endswith(self.file_filter):
                return
                
            self.setText(file_path)
            event.acceptProposedAction()
            
            # If this is the input field, auto-suggest output filename
            if self.file_filter == ".json":
                # Find the main window by traversing up the parent hierarchy
                parent = self.parent()
                while parent and not isinstance(parent, ConverterWindow):
                    parent = parent.parent()
                
                if parent and hasattr(parent, 'output_entry'):
                    output_filename = os.path.splitext(file_path)[0] + ".srt"
                    parent.output_entry.setText(output_filename)

class StyledButton(QPushButton):
    """Custom styled button for a more modern look"""
    def __init__(self, text, parent=None, primary=False):
        super().__init__(text, parent)
        self.setMinimumHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply different styles based on whether it's a primary button
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4a86e8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3a76d8;
                }
                QPushButton:pressed {
                    background-color: #2a66c8;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)

class ConverterWindow(QMainWindow):
    """
    Main window for the JSON to SRT converter application.
    """
    # Signal for progress updates
    progress_updated = pyqtSignal(float)
    
    def __init__(self):
        """
        Initializes the converter window.
        """
        super().__init__()
        
        # Configure the window
        self.setWindowTitle("JSON to SRT Converter")
        self.setGeometry(100, 100, 650, 450)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set application style
        self.setup_style()
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)
        
        # Create UI components
        self.create_ui_components()
        
        # Connect signals
        self.progress_updated.connect(self.update_progress)
    
    def setup_style(self):
        """Sets up the application style"""
        # Set font
        app_font = QFont("Segoe UI", 10)
        QApplication.setFont(app_font)
        
        # Set application style
        QApplication.setStyle("Fusion")
        
        # Optional: Set a light color palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        QApplication.setPalette(palette)
    
    def create_ui_components(self):
        """Creates all UI components."""
        # Title and description
        self.create_header()
        
        # Add a separator
        self.add_separator()
        
        # Input file selection
        self.create_input_section()
        
        # Output file selection
        self.create_output_section()
        
        # Progress bar
        self.create_progress_section()
        
        # Add a separator
        self.add_separator()
        
        # Convert button
        self.create_convert_button()
    
    def create_header(self):
        """Creates the header with title and description"""
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("JSON to SRT Converter")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2a66c8;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Convierte archivos JSON de subtítulos a formato SRT con códigos de color")
        desc_label.setStyleSheet("font-size: 12px; color: #666666;")
        desc_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(desc_label)
        
        self.main_layout.addLayout(header_layout)
    
    def add_separator(self):
        """Adds a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #cccccc;")
        self.main_layout.addWidget(line)
    
    def create_input_section(self):
        """Creates the input file selection section."""
        input_label = QLabel("Archivo JSON de entrada:")
        input_label.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(input_label)
        
        input_layout = QHBoxLayout()
        self.input_entry = DropLineEdit(self, file_filter=".json")
        self.input_entry.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
        """)
        self.input_entry.setMinimumHeight(36)
        self.input_entry.setPlaceholderText("Arrastra y suelta un archivo JSON aquí o haz clic en Examinar")
        
        self.browse_input_button = StyledButton("Examinar")
        self.browse_input_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.browse_input_button.clicked.connect(self.browse_input)
        
        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(self.browse_input_button)
        
        self.main_layout.addLayout(input_layout)
    
    def create_output_section(self):
        """Creates the output file selection section."""
        output_label = QLabel("Archivo SRT de salida:")
        output_label.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(output_label)
        
        output_layout = QHBoxLayout()
        self.output_entry = DropLineEdit(self, file_filter=".srt")
        self.output_entry.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
        """)
        self.output_entry.setMinimumHeight(36)
        self.output_entry.setPlaceholderText("Arrastra y suelta un archivo SRT aquí o haz clic en Examinar")
        
        self.browse_output_button = StyledButton("Examinar")
        self.browse_output_button.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.browse_output_button.clicked.connect(self.browse_output)
        
        output_layout.addWidget(self.output_entry)
        output_layout.addWidget(self.browse_output_button)
        
        self.main_layout.addLayout(output_layout)
        
        # Add FPS selection
        self.create_fps_section()
    
    def create_fps_section(self):
        """Creates the FPS selection section."""
        fps_layout = QHBoxLayout()
        
        fps_label = QLabel("Frames por segundo (FPS):")
        fps_label.setStyleSheet("font-weight: bold;")
        fps_layout.addWidget(fps_label)
        
        self.fps_entry = QLineEdit("25")  # Default value is 25
        self.fps_entry.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
        """)
        self.fps_entry.setMaximumWidth(60)
        self.fps_entry.setMinimumHeight(36)
        self.fps_entry.setAlignment(Qt.AlignCenter)
        
        # Only allow numbers
        self.fps_entry.setValidator(QIntValidator(1, 120))
        
        fps_layout.addWidget(self.fps_entry)
        fps_layout.addStretch()
        
        self.main_layout.addLayout(fps_layout)
    
    def create_progress_section(self):
        """Creates the progress bar and status section."""
        progress_layout = QVBoxLayout()
        
        # Progress label
        progress_label = QLabel("Progreso:")
        progress_label.setStyleSheet("font-weight: bold;")
        progress_layout.addWidget(progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(24)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #4a86e8;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Listo para convertir")
        self.status_label.setStyleSheet("color: #666666; font-style: italic;")
        progress_layout.addWidget(self.status_label)
        
        self.main_layout.addLayout(progress_layout)
    
    def create_convert_button(self):
        """Creates the convert button."""
        button_layout = QHBoxLayout()
        
        # Add spacer to center the button
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Create convert button
        self.convert_button = StyledButton("Convertir", primary=True)
        self.convert_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.convert_button.clicked.connect(self.convert)
        self.convert_button.setMinimumWidth(200)
        self.convert_button.setMinimumHeight(44)
        button_layout.addWidget(self.convert_button)
        
        # Add spacer to center the button
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.main_layout.addLayout(button_layout)
        self.main_layout.addStretch()
    
    def browse_input(self):
        """Opens a file dialog to select the input JSON file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo JSON", "", "JSON files (*.json)"
        )
        if filename:
            self.input_entry.setText(filename)
            
            # Auto-suggest output filename
            output_filename = os.path.splitext(filename)[0] + ".srt"
            self.output_entry.setText(output_filename)
    
    def browse_output(self):
        """Opens a file dialog to select the output SRT file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo SRT", "", "SRT files (*.srt)"
        )
        if filename:
            self.output_entry.setText(filename)
    
    def convert(self):
        """Converts the input JSON file to SRT format."""
        input_file = self.input_entry.text()
        output_file = self.output_entry.text()
        
        try:
            fps = int(self.fps_entry.text())
            if fps <= 0:
                raise ValueError("FPS debe ser un número positivo")
        except ValueError:
            QMessageBox.critical(
                self, "Error", "Por favor, introduce un valor válido para FPS"
            )
            return
        
        if not input_file or not output_file:
            QMessageBox.critical(
                self, "Error", "Por favor, selecciona los archivos de entrada y salida"
            )
            return
        
        # Reset the progress bar and update the status
        self.progress_bar.setValue(0)
        self.status_label.setText("Convirtiendo...")
        self.status_label.setStyleSheet("color: #666666; font-style: italic;")
        self.convert_button.setEnabled(False)
        QApplication.processEvents()
        
        try:
            # Process the file with callback for progress updates
            process_json_to_srt(
                input_file, 
                output_file,
                fps=fps,
                callback=self.progress_callback
            )
            
            # Update progress and status
            self.progress_bar.setValue(100)
            self.status_label.setText("Conversión completada con éxito")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            
            QMessageBox.information(
                self, "Éxito", f"Conversión completada con éxito.\nArchivo de salida: {output_file}"
            )
        except Exception as e:
            logger.error(f"Error during conversion: {str(e)}")
            self.status_label.setText("Error en la conversión")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            QMessageBox.critical(
                self, "Error", f"Ocurrió un error durante la conversión:\n{str(e)}"
            )
        finally:
            self.convert_button.setEnabled(True)
    
    def progress_callback(self, value):
        """Callback function for progress updates."""
        self.progress_updated.emit(value)
    
    def update_progress(self, value):
        """Updates the progress bar with the given value."""
        self.progress_bar.setValue(int(value))
        QApplication.processEvents()