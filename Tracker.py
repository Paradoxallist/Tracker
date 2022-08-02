from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2, imutils
from random import randint
from numpy import double

import pymysql
import sys
import os

image_path = 'C:/Users/User/Desktop/ImagesBoat/'
index = 0
ext = '.JPG'

listTypeBoat = ["Linienschiff ","Motorboot ","Elektroboot ","Segelboot","Unbekannt"]

image_paths = []

bboxes = []
colors = []
boatType = []

sizeX = 840
sizeY = 560
indentX = 35
indentY = 23
maxX = 1192 - indentX
maxY = 795 - indentY

isChooseBoat = False

class Ui_MainWindow(object):

	multiTracker = cv2.MultiTracker_create()
        
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(860, 640)
  
		self.db = DataBase()
		self.db.dropTable()
		self.db.creatTable()

		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
		self.gridLayout_2.setObjectName("gridLayout_2")
		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setObjectName("gridLayout")
		self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_3.setObjectName("horizontalLayout_3")
		self.label = QtWidgets.QLabel(self.centralwidget)
		self.label.setGeometry(10,10,sizeX,sizeY)
		self.label.mousePressEvent = self.clickImage
		self.label.setText("")
		#self.label.setPixmap(QtGui.QPixmap("images/2.jpg"))
		self.label.setObjectName("label")
		#self.horizontalLayout_3.addWidget(self.label)
		self.horizontalLayout = QtWidgets.QHBoxLayout()
		self.horizontalLayout.setObjectName("horizontalLayout")
		#self.horizontalLayout_3.addLayout(self.horizontalLayout)
		#self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 2)
		self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_2.setObjectName("horizontalLayout_2")
  
		self.pushButton = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton.setObjectName("pushButton")
		self.pushButton.setGeometry(10,580,70,22)
		
		self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_2.setObjectName("pushButton_2")
		self.pushButton_2.setGeometry(90,580,70,22)
  
		self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_3.setObjectName("pushButton_3")
		self.pushButton_3.setGeometry(170,580,70,22)
  
		self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_4.setObjectName("pushButton_4")
		self.pushButton_4.setGeometry(250,580,70,22)
  
		self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
		spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
		self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
		MainWindow.setCentralWidget(self.centralwidget)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		self.retranslateUi(MainWindow)
		self.pushButton.clicked.connect(self.earlyImage)
		self.pushButton_2.clicked.connect(self.nextImage)
		self.pushButton_3.clicked.connect(self.addTracker)
		self.pushButton_4.clicked.connect(self.editTracker)
  		
		QtCore.QMetaObject.connectSlotsByName(MainWindow)
		
		self.image = cv2.imread(image_paths[index])
		self.setPhoto(self.image)
  
		# Added code here
		self.filename = None # Will hold the image address location
		self.tmp = None # Will hold the temporary image for display

    
	def clickImage(self , event):
		x = event.pos().x() * 1192/840
		y = event.pos().y() * 795/560
		if event.button() == QtCore.Qt.LeftButton:
			frame = self.resizeImage()	
			dialog = DialogChooseTypeBoat()
			dialog.exec_()

			global isChooseBoat
			if isChooseBoat:

				x = max(min(maxX, x), indentX) 
				y = max(min(maxY, y), indentY)
				bbox = (x - indentX,y - indentY,indentX * 2,indentY * 2)
				bboxes.append(bbox)
				colors.append((randint(64, 255), randint(64, 255), randint(64, 255)))
				self.multiTracker.add(cv2.TrackerCSRT_create(), frame, bbox)
				self.setPhotoManipulation(False)
				isChooseBoat = False
		elif event.button() == QtCore.Qt.RightButton:
			for i, newbox in enumerate(bboxes):
				if(bboxes[i] != (0,0,0,0)):
					p1 = (int(newbox[0]), int(newbox[1]))
					p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
					if p1[0] < x < p2[0] and p1[1] < y < p2[1]:
						bboxes[i] = (0,0,0,0)
						self.setPhotoManipulation(False)
						break
			

	
	def earlyImage(self):
		global index
		if index > 0:
			index-=1
			self.setPhotoManipulation(False)
	
	def setPhoto(self,image):
		self.tmp = image
		image = imutils.resize(image,width=sizeX)
		frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
		self.label.setPixmap(QtGui.QPixmap.fromImage(image))

		
	def addTracker(self):

		frame = self.resizeImage()	

		bbox = cv2.selectROI('Add Tracker', frame)
		dialog = DialogChooseTypeBoat()
		dialog.exec_()
		if bbox != (0,0,0,0) and isChooseBoat:
			bboxes.append(bbox)
			colors.append((randint(64, 255), randint(64, 255), randint(64, 255)))
			self.multiTracker.add(cv2.TrackerCSRT_create(), frame, bbox)
		cv2.destroyAllWindows()

		self.setPhotoManipulation(False)
	
	def resizeImage(self):
		img = cv2.imread(image_paths[index])
		scale_percent = 15

		width = int(img.shape[1] * scale_percent / 100)
		height = int(img.shape[0] * scale_percent / 100)
		dsize = (width, height)

		frame = cv2.resize(img, dsize)
		return frame

	def editTracker(self):
		dialog = ClssDialog()
		dialog.exec_()
		self.setPhotoManipulation(False)
        
	def nextImage(self):
		global index
		if index < len(image_paths):
			index+=1
			self.setPhotoManipulation(True)
	
	def setPhotoManipulation(self,isRecord):
     
		frame = self.resizeImage()	
		ret, boxes = self.multiTracker.update(frame)

		for i, newbox in enumerate(boxes):
			if(bboxes[i] != (0,0,0,0)):
				bboxes[i] = (newbox[0],newbox[1],newbox[2],newbox[3])
				p1 = (int(newbox[0]), int(newbox[1]))
				p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
				cv2.rectangle(frame, p1, p2, colors[i], 2, 1)
				cv2.putText(frame, boatType[i] + f"({i})", (int(newbox[0]), int(newbox[1] - newbox[3]/5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,50),2)
				if isRecord:
					x = newbox[0] + newbox[2]/2
					y = newbox[1] + newbox[3]/2
					self.db.addRecord(index,boatType[i],x,y)
   
		self.setPhoto(frame)

	
	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		#MainWindow.setWindowTitle(_translate("MainWindow", "Tracker"))
		#self.setWindowIcon(QIcon('1.png'))
		self.pushButton.setText(_translate("MainWindow", "Back"))
		self.pushButton_2.setText(_translate("MainWindow", "Next"))
		self.pushButton_3.setText(_translate("MainWindow", "AddTracker"))
		self.pushButton_4.setText(_translate("MainWindow", "EditTracker"))

class ClssDialog(QDialog):

    def __init__(self, parent=None):
        super(ClssDialog, self).__init__(parent)
        
        self.setWindowTitle('Edit Tracker')
        
        self.listView = QListView()
        self.slm = QStringListModel()
        self.qlist = []
        self.listTr = []
        self.setInfoList()

        dlgLayout = QVBoxLayout()
        dlgLayout.addWidget(self.listView)
        self.setLayout(dlgLayout)
        
    def showDialog(self,qModelIndex):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Delete Tracker?")
        msgBox.setWindowTitle("Delete")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        #msgBox.buttonClicked.connect(self.msgButtonClick)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            bboxes[self.qlist[qModelIndex.row()]] = (0,0,0,0)
            self.qlist.clear()
            self.listTr.clear()
            self.setInfoList()
    
    def setInfoList(self):
        for x in range(0,len(bboxes)):
            if(bboxes[x] != (0,0,0,0)):
                self.qlist.append(x)
                self.listTr.append('Tracker ' + str(x))
        self.slm.setStringList(self.listTr)
        self.listView.setModel(self.slm)
        self.listView.clicked.connect(self.showDialog)
   
    def msgButtonClick(i):
        print("Button clicked is:",i.text())

class DialogChooseTypeBoat(QDialog):

	def __init__(self, parent=None):
		super(DialogChooseTypeBoat, self).__init__(parent)
        
		self.setWindowTitle('Choose Type Boat')
        
		self.listView = QListView()
		self.slm = QStringListModel()
		self.qlist = listTypeBoat
        
		self.setInfoList()
  
		dlgLayout = QVBoxLayout()
		dlgLayout.addWidget(self.listView)
		self.setLayout(dlgLayout)
        
	def showDialog(self,qModelIndex):
		boatType.append(self.qlist[qModelIndex.row()])
		global isChooseBoat
		isChooseBoat = True
		self.close()

    
	def setInfoList(self):
		self.slm.setStringList(self.qlist)
		self.listView.setModel(self.slm)
		self.listView.clicked.connect(self.showDialog)


class DataBase():
	def __init__(self):
		super(DataBase,self).__init__()
		self.mydb = pymysql.connect(
		host="localhost",
		user="root",
		database="boats",
		passwd="Password1234567890")
		self.mycursor = self.mydb.cursor()

        
	def creatTable(self):
		query = "CREATE TABLE IF NOT EXISTS BoatPositions(ID int  PRIMARY KEY AUTO_INCREMENT, NumImg int, Type VARCHAR(255), X DOUBLE, Y DOUBLE);"
		self.mycursor.execute(query)
		self.mydb.commit()
        
	def dropTable(self):
		drop_query = "DROP TABLE BoatPositions;"
		self.mycursor.execute(drop_query)
		self.mydb.commit()
	
	def addRecord(self,num,Type,x,y):
		query = f"INSERT INTO BoatPositions(NumImg, Type, X, Y) VALUES({int(num)}, '{str(Type)}', {double(x)}, {double(y)});"
		self.mycursor.execute(query)
		self.mydb.commit()
        

if __name__ == "__main__":
    
	image_paths = [os.path.join(image_path, img) for img in os.listdir(image_path) if ext in img]
	image_paths = sorted(image_paths)
 
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())
 
