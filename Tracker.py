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

image_path = 'C:/Users/User/Desktop/Boote_310722/'
index = 100
ext = '.JPG'

listTypeBoat = ["Linienschiff ","Motorboot ","Elektroboot ","Segelboot","Unbekannt"]

image_paths = []

bboxes = []
colors = []
boatType = []

WidthImage = 1200
HeightImage = 800
indentX = 35
indentY = 23
maxX = 1192 - indentX
maxY = 795 - indentY

scale_percent = 15

isChooseBoat = False
isNoImg = False

DBhost = "localhost"
DBuser = "root"
DBdatabase = "boats"
DBpasswd = "Password1234567890"

class MainWindow(QMainWindow):

	multiTracker = cv2.MultiTracker_create()
    
	def __init__(self):
		super(MainWindow,self).__init__()

        #self.setWindowIcon(QIcon('1.png'))
		self.setWindowTitle("Tracker")
		self.setGeometry(350,100,1220,900)
        
		self.setupUi()
    
	def setupUi(self):
  
		self.creatDatabase()
		self.dropTable()
		self.creatTable()
  
		self.label = QLabel(self)
		self.label.setGeometry(10,20,WidthImage,HeightImage)
		self.label.mousePressEvent = self.clickImage
		self.label.setText("")
		#self.label.setPixmap(QtGui.QPixmap("images/2.jpg"))
		self.label.setObjectName("label")
  
		self.pushButton = QtWidgets.QPushButton(self)
		self.pushButton.setObjectName("pushButton")
		self.pushButton.setGeometry(10,HeightImage + 30,70,22)
		
		self.pushButton_2 = QtWidgets.QPushButton(self)
		self.pushButton_2.setObjectName("pushButton_2")
		self.pushButton_2.setGeometry(90,HeightImage + 30,70,22)
  
		self.pushButton_3 = QtWidgets.QPushButton(self)
		self.pushButton_3.setObjectName("pushButton_3")
		self.pushButton_3.setGeometry(170,HeightImage + 30,70,22)
  
		self.pushButton_4 = QtWidgets.QPushButton(self)
		self.pushButton_4.setObjectName("pushButton_4")
		self.pushButton_4.setGeometry(250,HeightImage + 30,70,22)

		self.pushButton.setText("Back")
		self.pushButton_2.setText("Next")
		self.pushButton_3.setText("AddTracker")
		self.pushButton_4.setText("EditTracker")
  
		self.pushButton.clicked.connect(self.earlyImage)
		self.pushButton_2.clicked.connect(self.nextImage)
		self.pushButton_3.clicked.connect(self.addTracker)
		self.pushButton_4.clicked.connect(self.editTracker)
  		

		global isNoImg

		if(isNoImg == False):
			image = cv2.imread(image_paths[index])
			self.setPhoto(image)
		else:
			image = cv2.imread("NoImg.JPG")
			image_paths.append("NoImg.JPG")
			self.setPhoto(image)
		self.createMenuBar()


	def createMenuBar(self):
		self.menuBar = QMenuBar(self)
		self.setMenuBar(self.menuBar)
        
		fileMenu = QMenu("&File",self)
		self.menuBar.addMenu(fileMenu)
        
		fileMenu.addAction('Specify the path', self.action_clicked_SpecifyPath)
		#fileMenu.addAction('Database setup', self.action_clicked_DB)
  
	@QtCore.pyqtSlot()
	def action_clicked_SpecifyPath(self):
		fname = QFileDialog.getExistingDirectory(self)
		if fname != "" :
			image_path = fname + "/"
			global image_paths
			image_paths = [os.path.join(image_path, img) for img in os.listdir(image_path) if ext in img]
			image_paths = sorted(image_paths)
			global index
			index = 0
			global isNoImg
			isNoImg = False
			self.setPhotoManipulation()
	
	@QtCore.pyqtSlot()
	def action_clicked_DB(self):
		dialog = DialogChooseDB()
		dialog.exec_()
		self.creatDatabase()
		self.creatTable()
	

    
	def clickImage(self , event):
		
		if isNoImg:
			return

		x = event.pos().x() * 1192/WidthImage
		y = event.pos().y() * 795/HeightImage
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
			

		
	def addTracker(self):

		if isNoImg:
			return

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

	def editTracker(self):
		dialog = ClssDialog()
		dialog.exec_()
		self.setPhotoManipulation(False)
    
	def earlyImage(self):
		global index
		if index > 0:
			index-=1
			self.setPhotoManipulation(False)
    
	def nextImage(self):
		global index
		if index < len(image_paths)-1:
			index+=1
			self.setPhotoManipulation(True)
    
##### image
    
	def setPhoto(self,image):
		image = imutils.resize(image,width=WidthImage)
		frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
		self.label.setPixmap(QtGui.QPixmap.fromImage(image))

	
	def resizeImage(self):
		img = cv2.imread(image_paths[index])

		global scale_percent

		width = int(img.shape[1] * scale_percent / 100)
		height = int(img.shape[0] * scale_percent / 100)
		dsize = (width, height)

		frame = cv2.resize(img, dsize)
		return frame
 
	def setPhotoManipulation(self,isRecord=False):
		
		if isNoImg:
			return

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
					self.addRecord(index,boatType[i],x,y)
   
		self.setPhoto(frame)


##### Database

	isCreatedDB = False

	def creatDatabase(self):
		try:
			self.mydb = pymysql.connect(
			host = DBhost,
			user = DBuser,
			database = DBdatabase,
			passwd = DBpasswd)
  
			self.mycursor = self.mydb.cursor()
			self.isCreatedDB = True
		except pymysql.connect.Error as err:
			print("Something went wrong: {}".format(err))
			msgBox = QMessageBox()
			msgBox.setIcon(QMessageBox.Information)
			msgBox.setText("Something went wrong: {}".format(err))
			msgBox.setWindowTitle("Error")
			msgBox.exec()
        
	def creatTable(self):
		if self.isCreatedDB == False:
			return
		try:
			query = "CREATE TABLE IF NOT EXISTS BoatPositions(ID int  PRIMARY KEY AUTO_INCREMENT, NumImg int, Type VARCHAR(255), X DOUBLE, Y DOUBLE);"
			self.mycursor.execute(query)
			self.mydb.commit()
		except pymysql.Error as err:
			print("Something went wrong: {}".format(err))
			msgBox = QMessageBox()
			msgBox.setIcon(QMessageBox.Information)
			msgBox.setText("Something went wrong: {}".format(err))
			msgBox.setWindowTitle("Error")
			msgBox.exec()
        
	def dropTable(self):
		if self.isCreatedDB == False:
			return
		try:
			drop_query = "DROP TABLE BoatPositions;"
			self.mycursor.execute(drop_query)
			self.mydb.commit()
		except pymysql.Error as err:
			print("Something went wrong: {}".format(err))
			msgBox = QMessageBox()
			msgBox.setIcon(QMessageBox.Information)
			msgBox.setText("Something went wrong: {}".format(err))
			msgBox.setWindowTitle("Error")
			msgBox.exec()
	
	def addRecord(self,num,Type,x,y):
		if self.isCreatedDB == False:
			return
		try:
			query = f"INSERT INTO BoatPositions(NumImg, Type, X, Y) VALUES({int(num)}, '{str(Type)}', {double(x)}, {double(y)});"
			self.mycursor.execute(query)
			self.mydb.commit()
		except pymysql.Error as err:
			print("Something went wrong: {}".format(err))
			msgBox = QMessageBox()
			msgBox.setIcon(QMessageBox.Information)
			msgBox.setText("Something went wrong: {}".format(err))
			msgBox.setWindowTitle("Error")
			msgBox.exec()


##### Window (Edit tracker)

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

##### Window (Choose Type Boat)

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

##### Window (Database setup)

class DialogChooseDB(QDialog):

	def __init__(self, parent=None):
		super(DialogChooseDB, self).__init__(parent)
        
		self.setWindowTitle('Database setup')

		flo = QFormLayout()
		self.LineEditHost = QLineEdit()
		self.LineEditUser = QLineEdit()
		self.LineEditDataBase = QLineEdit()
		self.LineEditPasswd = QLineEdit()
        
		flo.addRow("Host",self.LineEditHost)
		flo.addRow("User",self.LineEditUser)
		flo.addRow("DataBase",self.LineEditDataBase)
		flo.addRow("Password",self.LineEditPasswd)
  
		button_1 = QPushButton("Ok")
		#button_1.setObjectName("Ok")
		button_1.clicked.connect(self.pressOk)
		button_2 = QPushButton("Cancel")
		#button_2.setObjectName("Cancel")
		button_2.clicked.connect(self.reject)
		flo.addRow(button_1,button_2)

		self.LineEditPasswd.setEchoMode(QLineEdit.Password)

		self.setLayout(flo)

        
	def pressOk(self):
		global DBhost,DBuser,DBdatabase,DBpasswd
		DBhost = self.LineEditHost.text()
		DBuser = self.LineEditUser.text()
		DBdatabase = self.LineEditDataBase.text()
		DBpasswd = self.LineEditPasswd.text()
		self.reject()

#### init

if __name__ == "__main__":
    
	if(os.path.exists(image_path)):
		image_paths = [os.path.join(image_path, img) for img in os.listdir(image_path) if ext in img]
		image_paths = sorted(image_paths)
	else:
		isNoImg = True
	app = QtWidgets.QApplication(sys.argv)
	Window = MainWindow()
	Window.show()
	sys.exit(app.exec_())
 
