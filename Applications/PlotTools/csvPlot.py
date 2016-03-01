'''
Tools to plot data from CSV file to PDF file.
    Author: Bosc A.
    MAJ :2014-07-04
'''
#import tkFileDialog to propose a GUI to select file
from Tkinter import Tk
from tkFileDialog import askopenfilename as inputFileName
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing


#DEFAULT PARAMETERS
INTERACTIVE = False
CSV_separator =','


#DEFINITIONS
class DataList(list):
    '''A list that support attribut affectation'''
    pass

def loadData(filePathName = None,  CSV_separator =CSV_separator):
    '''#loaded data from csv structured file'''
    if filePathName is None : 
        filePathName = inputFileName()
    
    if INTERACTIVE: print('Load data... ')
    
    with open(filePathName, 'r') as dataFile:

        #create the datasets from header
        varDefs= dataFile.readline().split(CSV_separator)
        dataSetRange = range(len(varDefs))
        csvData = DataList( [DataList() for i in dataSetRange])
        csvData.fileName = filePathName
        
        for i_col in dataSetRange:
            dataField = csvData[i_col]
            dataField.column = i_col
            dataField.header = varDefs[i_col].strip() 
            dataField.title = '%s: %s' %(dataField.column+1, dataField.header )
        
        #fill the datasets from records
        for line in dataFile.readlines():
            record = line.split(CSV_separator)
            for dataField in csvData:
                try:
                    dataField.append(float(record[dataField.column].strip()))
                except:
                    dataField.append(-9999)
    
    return csvData
    



def plotPDF(csvData = None):
    '''Plot all the dataset of a CSV file in a PDF file.
        csvData : CSV file name (string), if None ask to choose one by GUI.
    '''
    if csvData is None : csvData=loadData()
    
    if INTERACTIVE : print('Create %s plots. It could be long... ' % len(csvData))
    
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    with  PdfPages('%s.pdf'% csvData.fileName.rsplit('.', 1)[0]) as pp:
        for dataField in csvData:
            fig = plt.figure()
            plt.plot(dataField)
            plt.title ('%s'% dataField.title)
            pp.savefig(fig) 
            plt.close(fig)
            
    if INTERACTIVE : print('Cool, PDF file of graphs is made.')
    


def dualPlotPDF(csvData1 = None, csvData2 = None):
    '''plot the graph of two similar CSV files for comparaison in  a PDF file.
        csvData1 and csvData2 : CSV file names (string), if None ask to choose one by GUI.
    '''
    if csvData1 is None : csvData1=loadData()
    if csvData2 is None : csvData2=loadData()
    
    assert len(csvData1) == len(csvData2) 
    
    if INTERACTIVE : print('Create %s dual plots. It could be long... ' % len(csvData1))
    
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    with  PdfPages('%s_VS_%s.pdf'% (csvData1.fileName.rsplit('.', 1)[0], csvData2.fileName.rsplit('.', 1)[0].rsplit('/', 1)[1])) as pp:
        for i in range(len(csvData1)):
            dataField1,  dataField2  = csvData1[i], csvData2[i]

            fig = plt.figure()
            plt.plot(dataField1)
            plt.plot(dataField2)

            plt.title ('%s\n%s'%(dataField1.title,   dataField2.title))
            pp.savefig(fig) 
            plt.close(fig)
            
    if INTERACTIVE : print('Cool, PDF file of dual graphs is made.')
    
    
def multiPlotPDF(*csvData ):
    '''plot the graph of many similar CSV files for comparaison in a PDF file.
        csvData is a list of dataset
    '''
    
    if INTERACTIVE : print('Create %s dual plots. It could be long... ' % len(csvData[0]))
    
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    with  PdfPages('%s_VS_others.pdf'% csvData[0].fileName.rsplit('.', 1)[0]) as pp:
        for i in range(len(csvData[0])):
            fig = plt.figure()            
            for _data in csvData:
                dataField  = _data[i]
                plt.plot(dataField)


            plt.title ('%s'%dataField.title)
            pp.savefig(fig) 
            plt.close(fig)
            
    if INTERACTIVE : print('Cool, PDF file of multi graphs is made.')
    
    
    
    
    
if __name__ == '__main__':
    INTERACTIVE = True
    print('''
    ### CSVPlot #############################################
    For interactive use : 
        - plotPDF()  : to simply select a CSV file, load its data, and plot the data in an PDF file
        - dualPlotPDF() : plot the graph of two equivalente CSV file for comparaison
    #####################################################
    ''')
