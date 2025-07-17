import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg

# Create the application
app = QApplication(sys.argv)

# Create a window
win = QMainWindow()
win.setWindowTitle('PyQtGraph Test')
win.resize(800, 600)

# Create a plot widget
plot_widget = pg.PlotWidget()
win.setCentralWidget(plot_widget)

# Add data to the plot
x = list(range(10))
y = [i**2 for i in x]
plot_widget.plot(x, y, pen='r')

# Show the window
win.show()

# Start the event loop
sys.exit(app.exec_()) 