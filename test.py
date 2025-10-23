# Using PyQt6 (you can adapt to PyQt5 or PySide2/6)
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget
from PyQt6.QtCore import QStringListModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QComboBox Placeholder Text Example")
        self.setGeometry(100, 100, 300, 150)

        central_widget = QWidget()
        layout = QVBoxLayout()

        # Example 1: Basic Placeholder Text
        combo1 = QComboBox()
        combo1.setPlaceholderText("Select your favorite color")
        combo1.addItems(["Red", "Green", "Blue", "Yellow"])
        layout.addWidget(combo1)

        # Example 2: Placeholder Text with No Initial Selection
        combo2 = QComboBox()
        combo2.setPlaceholderText("Choose an option")
        items = ["Option A", "Option B", "Option C"]
        combo2.addItems(items)
        combo2.setCurrentIndex(-1) # Ensure no item is initially selected
        layout.addWidget(combo2)

        # Example 3: Placeholder Text with an Empty Combo Box initially
        combo3 = QComboBox()
        combo3.setPlaceholderText("Loading data...")
        # In a real application, you might populate this combo box later
        layout.addWidget(combo3)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
