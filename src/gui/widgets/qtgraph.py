import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush


class Graph(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.setBackground(QBrush(Qt.transparent))  # Transparent background

        # Set axis labels
        self.getPlotItem().setLabel('left', 'Signal', units='Volt')
        self.getPlotItem().setLabel('bottom', 'Frequency', units='Hz')

        self.line_curve = self.plot(pen=pg.mkPen(QColor(65, 105, 224), width=2), symbol = 'o')
        self.dot_curve = self.plot(pen=pg.mkPen(QColor(65, 105, 224), width=0), symbol = 'o')


        # Set the plot color scheme
        self.showGrid(x=True, y=True, alpha=0.3)