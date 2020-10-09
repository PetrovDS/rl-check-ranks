#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
import sys, re, urllib, xmltodict
from htmldom import htmldom
from html.parser import HTMLParser
from PyQt5.QtWidgets import *
from PyQt5 import Qt, QtCore
from PyQt5.QtGui import *
 
class Example(QWidget):
	
	def __init__(self):
		super().__init__()
		self.sizeFlag = True
		self.initUI()
	


	def initUI(self):
		self.setGeometry(1920-330, 30, 300, 300)
		self.setFixedSize(300, 280)
		self.setWindowTitle('Узнать ранги')
		#self.setWindowFlags(Qt.Qt.FramelessWindowHint)
		self.setWindowIcon(QIcon('15.png'))

		btn = QPushButton('—', self)
		btn.resize(20, 10)
		btn.setFont(Qt.QFont('Myriad Pro', 5))
		btn.move(275, 5)
		btn.clicked.connect(self.changeSize)

		self.nickname = QLabel(self)
		self.nickname.move(5, 3)
		self.nickname.resize(240, 24)
		#self.nickname.setText("N/A")
		self.nickname.setFont(Qt.QFont('Myriad Pro', 14))

		self.totalScore = QLabel(self)
		self.totalScore.move(245, 14)
		self.totalScore.resize(50, 10)
		#self.totalScore.setText("N/A")
		self.totalScore.setFont(Qt.QFont('Tahoma', 7))
		self.totalScore.setAlignment(QtCore.Qt.AlignRight)

		self.rankImgs = [QPixmap(str(i) + ".png") for i in range(0, 16)]
		self.rankImgLbls = [QLabel(self) for i in range(0, 4)]

		# размещаем картинки
		c = 0
		for i in self.rankImgLbls:
			x = [30, 180][c % 2]
			y = [20, 130][int(c > 1)]
			c += 1
			i.move(x, y)
			i.resize(130, 130)
			i.setPixmap(self.rankImgs[0])
			i.setScaledContents(True)

		rankTypes = ["1x1", "2x2", "1x5", "3x3"]
		rankTypeLbls = [QLabel(self) for i in range(0, 4)]
		self.rankScoreLbls = [QLabel(self) for i in range(0, 4)]
		self.rankDivisionLbls = [QLabel(self) for i in range(0, 4)]

		# размещаем подписи
		for i in range(0, 4):
			x = [10, 160][i % 2]
			y = [65, 175][int(i > 1)]

			rankTypeLbls[i].setText(rankTypes[i])
			#self.rankScoreLbls[i].setText("N/A")
			#self.rankDivisionLbls[i].setText("N/A")

			rankTypeLbls[i].setFont(Qt.QFont('Tahoma', 10))
			self.rankScoreLbls[i].setFont(Qt.QFont('Tahoma', 10))
			self.rankDivisionLbls[i].setFont(Qt.QFont('Tahoma', 10))
			
			rankTypeLbls[i].resize(50, 10)
			self.rankScoreLbls[i].resize(50, 10)
			self.rankDivisionLbls[i].resize(50, 10)

			rankTypeLbls[i].move(x, y)
			self.rankScoreLbls[i].move(x, y + 15)
			self.rankDivisionLbls[i].move(x, y + 30)


		self.inpt = QLineEdit(self)
		self.inpt.move(0, 260)
		self.inpt.resize(300, 20)
		self.inpt.setFont(Qt.QFont('Myriad Pro', 12))
		self.inpt.setStyleSheet("QLineEdit {border:none;border-top:1px solid #ccc}")
		self.inpt.returnPressed.connect(self.getData)

		self.setUnranked()
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.update()

		self.show()

	def changeSize(self):
		if self.sizeFlag:
			self.setFixedSize(300, 30)
			self.update()
		else:
			self.setFixedSize(300, 280)
			self.update()
		self.sizeFlag = not self.sizeFlag

	def getData(self):
		text = self.inpt.text()

		if text == "":
			self.nickname.setText("Err: пустой запрос")

		flag = False
		url = ""

		m = re.search(re.compile("^http.*es\/(\d+)\/?", re.I), text)
		if m:
			url = "http://rocketleague.tracker.network/profile/steam/" + m.group(1)
			#url = "http://rltracker.pro/profiles/" + m.group(1) + "/steam"
			flag = True
			
		if not flag:
			m = re.search(re.compile("^\/?(\d+)\/?$", re.I), text)
			if m:
				url = "http://rocketleague.tracker.network/profile/steam/" + m.group(1)
				#url = "http://rltracker.pro/profiles/" + m.group(1) + "/steam"
				flag = True

		if not flag:
			m = re.search(re.compile("^http.*id\/(.+)\/?", re.I), text)
			if m:
				file = urllib.request.urlopen('http://steamcommunity.com/id/'+ m.group(1) + '/?xml=1')
				data = file.read()
				file.close()
				data = xmltodict.parse(data)
				url = "http://rocketleague.tracker.network/profile/steam/" + data["profile"]["steamID64"]
				#url = "http://rltracker.pro/profiles/" + data["profile"]["steamID64"] + "/steam"
				flag = True

		if not flag:
			url = "http://rocketleague.tracker.network/profile/ps/" + text

		print(url)
		user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
		head = { 'User-Agent' : user_agent }
		stat = urllib.request.Request(url, headers = head)
		with urllib.request.urlopen(stat) as response:
			data = response.read()

		data = data.decode("utf-8")
		data = data.replace("\n\n", "\n")

		if re.search("Invalid Steam Id or Steam is down", data):
			self.nickname.setText("Err: 404")
			return

		if re.search("The remote server returned an error", data):
			self.nickname.setText("Err: 403")
			return

		ts = re.search("<div class=\"name\">\s+Tracker Score[\S\s]{0,300}\"value\">([\,\d]+\.\d)<\/div", data).group(1)
		nick = re.search("<h1>(.+)<\/h1>", data).group(1)

		if ts == "0.0":
			self.setUnranked()
			self.nickname.setText(nick)
			self.totalScore.setText(ts)
			self.inpt.clear()
			return

		ranks = []
		#ranks.append(re.search("<td style=\"width:32px;\">\s+[^\d]+(\d+)[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+Ranked Duel 1v1\n[^\n]+\n[^\n]+\s+Division\s(\w+)\s+[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+\s+(\d+)", data))
		#ranks.append(re.search("<td style=\"width:32px;\">\s+[^\d]+(\d+)[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+Ranked Doubles 2v2\n[^\n]+\n[^\n]+\s+Division\s(\w+)\s+[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+\s+(\d+)", data))
		#ranks.append(re.search("<td style=\"width:32px;\">\s+[^\d]+(\d+)[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+Ranked Solo Standard 3v3\n[^\n]+\n[^\n]+\s+Division\s(\w+)\s+[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+\s+(\d+)", data))
		#ranks.append(re.search("<td style=\"width:32px;\">\s+[^\d]+(\d+)[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+Ranked Standard 3v3\n[^\n]+\n[^\n]+\s+Division\s(\w+)\s+[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+\s+(\d+)", data))
		
		ranks.append(re.search("<td style=\"width:32px;\">\s+[^\d]+(\d+)[^\n]+\s+[^\n]+\s+Ranked Duel 1v1\s+[^\n]+\s+[^\n]+\s+Division\s(\w+)\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+(\d+)", data))
		ranks.append(re.search("<td style=\"width:32px;\">\s+[^\d]+(\d+)[^\n]+\s+[^\n]+\s+Ranked Doubles 2v2\s+[^\n]+\s+[^\n]+\s+Division\s(\w+)\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+(\d+)", data))
		ranks.append(re.search("<td style=\"width:32px;\">\s+[^\d]+(\d+)[^\n]+\s+[^\n]+\s+Ranked Solo Standard 3v3\s+[^\n]+\s+[^\n]+\s+Division\s(\w+)\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+(\d+)", data))
		ranks.append(re.search("<td style=\"width:32px;\">\s+[^\d]+(\d+)[^\n]+\s+[^\n]+\s+Ranked Standard 3v3\s+[^\n]+\s+[^\n]+\s+Division\s(\w+)\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+[^\n]+\s+(\d+)", data))
		
		for i in range(0, 4):
			if ranks[i]:
				self.rankScoreLbls[i].setText(ranks[i].group(3))
				self.rankDivisionLbls[i].setText("DIV " + ranks[i].group(2))
				self.rankImgLbls[i].setPixmap(self.rankImgs[int(ranks[i].group(1))])
			else:
				self.rankScoreLbls[i].setText("N/A")
				self.rankDivisionLbls[i].setText("N/A")
				self.rankImgLbls[i].setPixmap(self.rankImgs[0])

		self.nickname.setText(nick)
		self.totalScore.setText(ts)

		self.inpt.clear()

	def setUnranked(self):
		for i in range(0, 4):
			self.rankScoreLbls[i].setText("N/A")
			self.rankDivisionLbls[i].setText("N/A")
			self.rankImgLbls[i].setPixmap(self.rankImgs[0])
		self.nickname.setText("N/A")
		self.totalScore.setText("N/A")


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())