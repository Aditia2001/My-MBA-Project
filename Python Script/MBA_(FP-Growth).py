# import sys
# import timeit
# import time
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog, QMessageBox, QDesktopWidget,QPushButton
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QListWidgetItem, QTableWidget, \
    QTableWidgetItem, QScrollArea
# import os

# Mengimpor library
# from arulespy.arules import eclat, Transactions
import pandas as pd
from mlxtend.frequent_patterns import association_rules
from FIM import fpgrowth
from FIM.fpgrowth import construct_fptree
from mlxtend.preprocessing import TransactionEncoder
import ast
import gc


from MyGUI import Ui_MainWindow
from PyQt5.QtCore import QCoreApplication






def FPG(dataset, minSupp, minConf):
    dataset['itemDescription'] = dataset['itemDescription'].apply(ast.literal_eval)
    all_values = dataset['itemDescription'].tolist()
    # all_values = dataset['itemDescription'].tolist()
    # all_values = [list(set(sublist)) for sublist in all_values]

    # Encode data
    TE = TransactionEncoder()
    TE.fit(all_values)
    item_matrix = TE.transform(all_values)
    item_matrix = pd.DataFrame(item_matrix, columns=TE.columns_)

    freq_itemsets = fpgrowth(item_matrix, min_support=minSupp, show_colnames=True)




    if len(freq_itemsets) > 0:
        freq_itemsets['k-itemset'] = freq_itemsets['itemsets'].apply(lambda x: len(x))
        Hasil_FI = pd.DataFrame(freq_itemsets)
        freq_itemsets.drop(columns=['support', 'itemsets'])

        Tampil_Hasil_fp = pd.DataFrame(Hasil_FI)
        Tampil_Hasil_fp['itemsets'] = Tampil_Hasil_fp['itemsets'].apply(lambda x: ', '.join(list(x)))
        # Tampil_Hasil_fp['itemsets'] = Tampil_Hasil_fp['itemsets'].apply(lambda x: x.replace(', ', ' => ', 1))
        Tampil_Hasil_fp['itemsets'] = Tampil_Hasil_fp['itemsets'].apply(lambda x: f'{{{x}}}')
        Tampil_Freq_Itemsets = Tampil_Hasil_fp.sort_values( [ "k-itemset","support"], ascending= [False,False])
        Tampil_Freq_Itemsets['total jenis k-itemset'] = Tampil_Freq_Itemsets.groupby('k-itemset')[
            'k-itemset'].transform('count')

        rules_fp = association_rules(Hasil_FI, metric="confidence", min_threshold=minConf, )
        rules_fp2 = rules_fp.drop(columns=['leverage', 'conviction', 'zhangs_metric'])
        rules_fp3 = rules_fp2[(rules_fp2['lift'] > 1) & (rules_fp2['confidence'] >= minConf)]

        Tampil_Asosiasi_FPG = pd.DataFrame(rules_fp3)
        Tampil_Asosiasi_FPG['antecedents'] = Tampil_Asosiasi_FPG['antecedents'].apply(lambda x: ', '.join(list(x)))
        Tampil_Asosiasi_FPG['consequents'] = Tampil_Asosiasi_FPG['consequents'].apply(lambda x: ', '.join(list(x)))
        Tampil_Asosiasi_FPG['antecedents'] = Tampil_Asosiasi_FPG['antecedents'].apply(lambda x: f'{{{x}}}')
        Tampil_Asosiasi_FPG['consequents'] = Tampil_Asosiasi_FPG['consequents'].apply(lambda x: f'{{{x}}}')
        # Tampil_Asosiasi_FPG = Tampil_Asosiasi_FPG.sort_values("lift", ascending=False)
        Tampil_Asosiasi = Tampil_Asosiasi_FPG.sort_values(["lift", "support", "confidence"],
                                                              ascending=[False, False, False])

        Tampil_Asosiasi['Support * Confidence'] = Tampil_Asosiasi['support'] * Tampil_Asosiasi['confidence']
        sumSC_Asosiasi= Tampil_Asosiasi['Support * Confidence'].sum()
        # Tampil_Asosiasi.astype(str).to_csv('Aturan Asosiasi FP-Growth.csv')
        n_Asosiasi = len(rules_fp3)
    else:

        Tampil_Hasil_fp = []
        Tampil_Asosiasi = []
        Tampil_Freq_Itemsets = []
        sumSC_Asosiasi = 0
        n_Asosiasi = 0
        rules_fp3 = []
        Hasil_FI = []


    freq_itemsets = None
    del freq_itemsets
    gc.collect()
    return Hasil_FI, Tampil_Freq_Itemsets, Tampil_Asosiasi, n_Asosiasi, sumSC_Asosiasi




class ShowImage(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ShowImage, self).__init__()
        self.setupUi(self)
        self.DataButton.clicked.connect(self.OpenFile)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def OpenFile(self):
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Pilih File CSV", "", "CSV Files (*.csv);;All Files (*)",
                                                       options=options)
        if self.fileName:

            # Membaca file CSV menggunakan pandas
            self.dataset = pd.read_csv(self.fileName)
            self.dataset =self.dataset.reset_index(drop=True)
            self.DataText = self.DataLineEdit.setText(self.fileName)
            del self.fileName
            gc.collect()
            # self.View(self.dataset, self.minSupport, self.minConfidence, self.Lift)
            self.minSupport = self.doubleSpinBoxSupport.value()
            self.minConfidence = self.doubleSpinBoxConfidence.value()
            self.algoritma= str(self.comboBoxAlgo.currentText())
            # self.Lift = self.doubleSpinBoxLift.value()
            self.Cek()
        else:
            QMessageBox.warning(self, "Invalid Input", "Data Dalam Format CSV Belum Dipilih")

    def Cek(self):


        # print(self.minSupport)
        # print(self.minConfidence)
        # print(self.Lift)
        if ("Algoritma FP-Growth") in self.algoritma :
            Hasil_FI, Tampil_Freq_Itemsets, Tampil_Asosiasi, n_Asosiasi, sumSC_Asosiasi \
                = FPG(self.dataset, self.minSupport, self.minConfidence)
            self.FrequentLabel.setText('Frequent Itemsets Dari Algoritma FP-Growth')
            self. AturanAsosiasiLabel.setText('Hasil Aturan Asosiasi Dari Algoritma FP-Growth')
            self.LabelKetFI.setText('Banyaknya aturan frequent itemsets yang dibuat algoritma FP-Growth : ')
            self.LabelKetAsosiasi.setText('Banyaknya aturan asosiasi yang dibuat berdasarkan frequent itemsets dari algoritma FP-Growth : ')
            self.LabelKetTingkat.setText('Tingkat kekuatan algoritma FP-Growth : ')



        self.DatasetTable.clear()
        self.TableFI.clear()
        self.TableRuleAsosiasi.clear()
        # Set ke Null
        self.labelFIAlgo.setText("Null")
        self.labelRuleAlgo.setText("Null")
        self.KekuatanAlgo.setText("Null")


        numRows = len(self.dataset.index)
        self.DatasetTable.setColumnCount(len(self.dataset.columns))
        self.DatasetTable.setRowCount(len(self.dataset.index))
        self.DatasetTable.setHorizontalHeaderLabels(self.dataset.columns)
        for i in range(numRows):
            for j in range(len(self.dataset.columns)):
                self.DatasetTable.setItem(i, j, QTableWidgetItem(str(self.dataset.iat[i, j])))
        self.DatasetTable.resizeColumnsToContents()
        self.DatasetTable.resizeRowsToContents()

        if len(Hasil_FI) > 0:
            numRows = len(Tampil_Freq_Itemsets.index)
            numColumn = len(Tampil_Freq_Itemsets.columns)
            self.TableFI.setColumnCount(numColumn)
            self.TableFI.setRowCount(numRows)
            self.TableFI.setHorizontalHeaderLabels(Tampil_Freq_Itemsets.columns)
            for i in range(numRows):
                for j in range(numColumn):
                    self.TableFI.setItem(i, j, QTableWidgetItem(str(Tampil_Freq_Itemsets.iat[i, j])))
            self.TableFI.resizeColumnsToContents()
            self.TableFI.resizeRowsToContents()

            FI_DF=pd.DataFrame(Tampil_Freq_Itemsets)
            FI_DF.to_excel('@ Hasil Frequent Itemset.xlsx', index=False, engine='openpyxl')

            numRowsRule= len(Tampil_Asosiasi.index)
            numColumnRule = len(Tampil_Asosiasi.columns)
            self.TableRuleAsosiasi.setColumnCount(numColumnRule)
            self.TableRuleAsosiasi.setRowCount(numRowsRule)
            self.TableRuleAsosiasi.setHorizontalHeaderLabels(Tampil_Asosiasi.columns)
            for i in range(numRowsRule):
                for j in range(numColumnRule):
                    self.TableRuleAsosiasi.setItem(i, j, QTableWidgetItem(str(Tampil_Asosiasi.iat[i, j])))
            self.TableRuleAsosiasi.resizeColumnsToContents()
            self.TableRuleAsosiasi.resizeRowsToContents()

            AI_DF = pd.DataFrame(Tampil_Asosiasi)
            AI_DF.to_excel('@ Hasil Asosiasi.xlsx', index=False, engine='openpyxl')

            self.labelFIAlgo.setText(str(len(Tampil_Freq_Itemsets)))

            self.labelRuleAlgo.setText(str(n_Asosiasi))


        # print("n aturan asosiasi dari kandidat Apriori :", n_apriori)

        if sumSC_Asosiasi > 0:
            kekuatan_algoritma = sumSC_Asosiasi / n_Asosiasi
            self.KekuatanAlgo.setText(str(kekuatan_algoritma))
            print('Sum_SC :',sumSC_Asosiasi)
            print('Nilai Asosiasi :',kekuatan_algoritma)



        # message box object
        msgBox = QMessageBox()

        # Set up the message box
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Proses Data Mining Telah Selesai.")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok)
        retval = msgBox.exec_()


        if len(Hasil_FI) == 0:
            QMessageBox.warning(self, "Tidak Ada Frequent Items )",
                                "Cobalah untuk mengganti treshold nilai minimum support")
        elif len(Tampil_Asosiasi) == 0:
            QMessageBox.warning(self, "Tidak Ada Aturan Asosiasi )",
                                "Cobalah untuk mengganti treshold nilai min support, confidence")



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ShowImage()
    mainWindow.setWindowTitle("FP-Growth MBA")
    mainWindow.show()
    sys.exit(app.exec_())
