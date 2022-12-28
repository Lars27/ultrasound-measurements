
import sys
import time
from PyQt5 import QtWidgets, uic
import numpy as np
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Qt5Agg')

qtcreator_file  = "test_graph.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

class test_result:  # Initialise with impossible values. To be set at object creation
    def __init__( self ):
        self.x0   = 0.0
        self.xmax = 10
        self.n    =  10
        self.finished = False
        self.invert   = False
        self.freeze   = False
        self.close_ok = True
        
    def x( self ):
            return np.linspace( self.x0, self.x0+2, 10 )        
        
    def y( self ):
        y = self.x()**2
        if self.invert:
            y=-y
        return y
        

#%% Class definitions
class test_plot_gui(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        #  Setup gtaph    
        plt.ion()
        resultfig, ax= plt.subplots(figsize=(10, 8))
        ax.set_xlabel('x [Arb. units]')
        ax.set_ylabel('y [Arb. units]')
        xmax= 10
        ax.set_xlim( -xmax    , xmax    )
        ax.set_ylim( -xmax**2 , xmax**2 )
        ax.set_title('Test plot')
        ax.grid(True)
        graph =ax.plot( [], [] )[0]
        resultfig.show()
        
        self.graph=graph
        self.resultfig = resultfig       

        # Connect GUI
        self.close_button.clicked.connect( self.close_app )
        self.run_button.clicked.connect( self.run_graph_plot )
        self.stop_button.clicked.connect( self.stop )
        self.invert_checkBox.clicked.connect( self.invert )
        self.freeze_checkBox.clicked.connect( self.freeze )
        
        self.res = test_result()
        
        self.statusBar().showMessage('Program started')
        

    def close_app(self):       
        self.statusBar().showMessage('Program closing')
        self.res.finished = True 
        plt.close(self.resultfig)
        self.close()
        
    def update_values(self):
        self.statusBar().showMessage('Values updated')
        self.end.setValue(self.end_slider.value())
        self.start.setValue(self.start_slider.value())
        self.statusBar().showMessage('Values updated')
        self.PlotGraph()
            
    def stop( self ): 
        self.res.finished = True
        self.status_lineEdit.setText(f'Stop command given {self.res.finished}')
        self.statusBar().showMessage('Program stopped')
        return 0

    def freeze( self ): 
        self.res.freeze = self.freeze_checkBox.isChecked()       
        self.status_lineEdit.setText( f'Freeze {self.res.freeze}' )
        self.statusBar().showMessage(f'Display freeze {self.res.freeze}' )
        return 0

    def invert( self ): 
        self.res.invert = self.invert_checkBox.isChecked()
        self.status_lineEdit.setText(  f'Invert {self.res.invert}' )
        self.statusBar().showMessage( f'Invert {self.res.invert}' )
        return 0
        
    def run_graph_plot( self ): 
        self.statusBar().showMessage( 'Running' )
        self.close_button.setEnabled(False)
        self.res.finished = False
        test_result()
        up       = True
        n        = 0
        self.status_lineEdit.setText('Starting')
        while not( self.res.finished):
            if not(self.res.freeze):
                n+=1
                x = self.res.x() 
                y = self.res.y() 
                self.counter_lineEdit.setText(f'{n} of 200')
                self.graph.set_xdata( x )                
                self.graph.set_ydata( y )
                
                if max(x) > self.res.xmax:
                    up = False
                if min(x) <-self.res.xmax:
                    up = True

                if up:
                    self.res.x0 += 1
                else:
                    self.res.x0 -= 1

            self.resultfig.canvas.draw()
            self.resultfig.canvas.flush_events()
                
            time.sleep( 0.05 )
            self.res.finished = self.res.finished or ( n > 200 )

        self.statusBar().showMessage( 'Finished' )
        self.status_lineEdit.setText('Loop finished')
        self.close_button.setEnabled(True)
            
        return 0            

        
    def plot_graph(self):        
        N    = 100
        start = (self.start.value())
        end   = (self.end.value())
        
        x= np.linspace(start,end,N)
        y= x**2
        graph_string= f"Start ={start} \n End ={end}"
        self.graph_data.setText(graph_string)
        
        self.graph.set_xdata(x)
        self.graph.set_ydata(y)
        self.resultfig.canvas.draw()
        self.resultfig.canvas.flush_events()

        
    def display_result(self):
        def __init__(self):
            resultfig, ax= plt.subplots()
            ax.set_xlabel('x [Arb. units]')
            ax.set_ylabel('y [Arb. units]')
            ax.set_title('Test plot')
            ax.plt.show()
            
            self.ax=ax
            
#%% MAin program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = test_plot_gui()
    window.show()
    sys.exit(app.exec_())
