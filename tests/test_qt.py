import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("PyQt5 Test")
window.setGeometry(100, 100, 280, 80)
label = QLabel("PyQt5 is working!", window)
label.move(90, 30)
window.show()
sys.exit(app.exec_()) 