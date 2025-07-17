from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MemoryGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        
        # Set style for better appearance
        plt.style.use('bmh')  # Using 'bmh' style instead of seaborn
        
    def update_graph(self, before_stats, after_stats):
        """Update the memory usage graph with before and after stats"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Ensure we're working with dictionary values
        if isinstance(before_stats, dict) and isinstance(after_stats, dict):
            before_percent = before_stats['percent']
            after_percent = after_stats['percent']
        else:
            before_percent = before_stats.percent
            after_percent = after_stats.percent
        
        # Data for the bar chart
        labels = ['Before', 'After']
        values = [before_percent, after_percent]
        colors = ['#ff9999', '#66b3ff']
        
        # Create bar chart
        bars = ax.bar(labels, values, color=colors)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,f'{height:.1f}%',ha='center', va='bottom')
        
        # Customize the graph
        ax.set_title('Memory Usage Optimization', pad=15)
        ax.set_ylabel('Memory Usage (%)')
        ax.grid(True, axis='y', alpha=0.3)
        
        # Add improvement indicator
        improvement = before_percent - after_percent
        if improvement > 0:
            ax.text(0.5, -0.1, f'Improvement: {improvement:.1f}%',ha='center', transform=ax.transAxes,color='green', fontsize=10)
        
        self.canvas.draw() 