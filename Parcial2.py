import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class InventarioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Inventario - Sucursales El Salvador")
        self.setGeometry(100, 100, 1050, 700)
        
        # Cargar el archivo CSV generado
        try:
            self.df = pd.read_csv('inventario_sucursales.csv')
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "No se encontró el archivo 'inventario_sucursales.csv'.")
            sys.exit(1)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Encabezado
        titulo = QLabel("Control de inventario El Salvador")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        main_layout.addWidget(titulo)

        # ventanas
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        #  Tabla 
        self.tab_tabla = QWidget()
        self.init_tab_tabla()
        self.tabs.addTab(self.tab_tabla, "Inventario general")

        #Gráficos 
        self.tab_graficos = QWidget()
        self.init_tab_graficos()
        self.tabs.addTab(self.tab_graficos, "Análisis grafico")

    def init_tab_tabla(self):
        layout = QVBoxLayout(self.tab_tabla)
        self.tabla = QTableWidget()
        
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in self.df.columns])

        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                val = str(self.df.iloc[i, j])
                item = QTableWidgetItem(val)
                if j in [3, 4]:  # Alinear stock y precio a la derecha
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla.setItem(i, j, item)

        self.tabla.resizeColumnsToContents()
        layout.addWidget(self.tabla)

    def init_tab_graficos(self):
        layout = QHBoxLayout(self.tab_graficos)

        
        self.canvas_stock = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        stock_por_sucursal = self.df.groupby('sucursal')['stock'].sum()
        
        ax1 = self.canvas_stock.axes
        bars1 = ax1.bar(stock_por_sucursal.index, stock_por_sucursal.values, color='#2980B9')
        ax1.set_title("Stock Total por Sucursal", fontsize=11, fontweight='bold')
        ax1.set_ylabel("Unidades")
        ax1.tick_params(axis='x', rotation=25)
        ax1.bar_label(bars1, padding=3)

        # Grsfico 2
        self.canvas_valor = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        self.df['valor_total'] = self.df['stock'] * self.df['precio_unitario']
        valor_por_sucursal = self.df.groupby('sucursal')['valor_total'].sum()

        ax2 = self.canvas_valor.axes
        bars2 = ax2.bar(valor_por_sucursal.index, valor_por_sucursal.values, color='#27AE60')
        ax2.set_title("Valor del Inventario ($ USD)", fontsize=11, fontweight='bold')
        ax2.set_ylabel("Monto USD ($)")
        ax2.tick_params(axis='x', rotation=25)
        ax2.bar_label(bars2, fmt='$%.0f', padding=3)

        layout.addWidget(self.canvas_stock)
        layout.addWidget(self.canvas_valor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = InventarioApp()
    ventana.show()
    sys.exit(app.exec_())