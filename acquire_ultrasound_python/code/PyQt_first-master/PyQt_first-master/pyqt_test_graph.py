
import sys
from PyQt5 import QtWidgets, uic
import numpy as np
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Qt5Agg')

qtcreator_file  = "test_graph.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        plt.ion()
        resultgraph, ax= plt.subplots(figsize=(10, 8))

        resultgraph.canvas.manager.window.setGeometry(800, 500, 800, 600)
        
        ax.set_xlabel('x [Arb. units]')
        ax.set_ylabel('y [Arb. units]')
        ax.set_xlim(-20 , 20)
        ax.set_ylim(  0, 400)
        ax.set_title('Test plot')
        x0 = np.linspace(0,10,100)
        y0 = np.linspace(0,10,100)
        graph, =ax.plot(x0,y0)
        resultgraph.show()
        
        self.graph=graph
        self.resultgraph = resultgraph       

        self.start.valueChanged.connect(self.PlotGraph)
        self.start_slider.valueChanged.connect(self.UpdateValues)
        self.end_slider.valueChanged.connect(self.UpdateValues)
        self.close_button.clicked.connect(self.CloseApp)

    def CloseApp(self):
        plt.close(self.resultgraph)
        self.close()
        
    def UpdateValues(self):
        self.end.setValue(self.end_slider.value())
        self.start.setValue(self.start_slider.value())
        self.PlotGraph()
            
    def PlotGraph(self):        
        N    = 100
        start = (self.start.value())
        end   = (self.end.value())
        
        x= np.linspace(start,end,N)
        y= x**2
        graph_string= f"Start ={start} \n End ={end}"
        self.graph_data.setText(graph_string)
        
        self.graph.set_xdata(x)
        self.graph.set_ydata(y)
        self.resultgraph.canvas.draw()
        self.resultgraph.canvas.flush_events()

        
    def DisplayResult(self):
        def __init__(self):
            resultgraph, ax= plt.subplots()
            ax.set_xlabel('x [Arb. units]')
            ax.set_ylabel('y [Arb. units]')
            ax.set_title('Test plot')
            ax.plt.show()
            
            self.ax=ax
            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
