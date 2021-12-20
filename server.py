import socket
import threading
import json
import requests
import time
import datetime
import locale

import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image

import webbrowser

MAX_BYTES = 1024
FORMAT = "utf-8"
PORT = 55555
IP = ''

SIGNUP = "SIGNUP"
LOGIN = "LOGIN"
LOGOUT = "LOGOUT"
GETDATE = "GETDATE"
GETCOUNTRY = "GETCOUNTRY"
GETCOVIDDATA = "GETCOVIDDATA"
LOGIN_SUCCESS = "LOGIN_SUCCESS"
LOGIN_FAILED = "LOGIN_FAILED"
LOGOUT_SUCCESS = "LOGOUT_SUCCESS"
LOGOUT_FAILED = "LOGOUT_FAILED"
SIGNUP_SUCCESS = "SIGNUP_SUCCESS"
SIGNUP_FAILED = "SIGNUP_FAILED"

COVID_API = "https://coronavirus-19-api.herokuapp.com/countries"

FONT = ("Tahoma", 13)
FONT_BOLD = ("Tahoma", 13, "bold")

UPDATE_INTERVAL = 3600 # 1 hour

DATABASE_FILENAME = {
		"user": "database/user.json",
		"covid": "database/covid.json"
}

locale.setlocale(locale.LC_ALL, 'en_US')

def filterData(data):
		result = {}
		result["country"] = data["country"]
		result["cases"] = data["cases"]
		result["deaths"] = data["deaths"]
		result["recovered"] = data["recovered"]
		return result

def formatNumber(number):
		if number == None: return "N/A"
		return locale.format_string("%d", int(number), grouping=True)

def messageCreate(type, payload):
		return json.dumps({"type": type, "payload": payload}).encode(FORMAT)

class Database():
		def __init__(self, userFn, covidFn):
				self.userFn = userFn
				self.covidFn = covidFn

		def updateCovidData(self, date, data):
				with open(self.covidFn, 'r+') as f:
						file_data = json.load(f)
						file_data[date] = data
						f.seek(0)
						json.dump(file_data, f, indent=2)
						f.close()

		def getCovidData(self, date, country="World"):
				with open(self.covidFn, 'r') as f:
						data = json.load(f)
						f.close()
				return list(filter(lambda x: x["country"] == country, data[date]))[0]

		def getDate(self):
				with open(self.covidFn, 'r') as f:
						data = json.load(f)
						f.close()
				return list(data.keys())

		def getCountry(self, date):
				# print(date)
				with open(self.covidFn, 'r') as f:
						data = json.load(f)
						f.close()
				return [country["country"] for country in data[date]]

		def hasUser(self, username):
				with open(self.userFn, 'r') as f:
						data = json.load(f)
						f.close()
				return username in data

		def getPassword(self, username):
				with open(self.userFn, 'r') as f:
						data = json.load(f)
						f.close()
				return data[username]["password"]

		def getAllUsername(self):
				with open(self.userFn, 'r') as f:
						data = json.load(f)
						f.close()
				return list(data.keys())

		def getUserIpAdress(self, username):
				with open(self.userFn, 'r') as f:
						data = json.load(f)
						f.close()
				return data[username]["ipaddress"]

		def setUserIpAdress(self, username, ipaddress):
				with open(self.userFn, 'r+') as f:
						data = json.load(f)
						data[username]["ipaddress"] = ipaddress
						f.seek(0)
						json.dump(data, f, indent=2)
						f.close()

		def addNewUser(self, username, password, ipaddress):
				with open(self.userFn, 'r+') as f:
						data = json.load(f)
						data[username] = {"password": password, "ipaddress": ipaddress}
						f.seek(0)
						json.dump(data, f, indent=2)
						f.close()

class Users():
		def __init__(self):
				self.users = self.load()

		def load(self):
				self.usernames = db.getAllUsername()
				users = {}
				for username in self.usernames:
						users[username] = {"ipaddress": db.getUserIpAdress(username), "port": None, "isLoggedIn": False}
				return users

		def logIn(self, username, ipaddress, port):
				self.users[username]["ipaddress"] = ipaddress
				self.users[username]["port"] = port
				self.users[username]["isLoggedIn"] = True
				db.setUserIpAdress(username, ipaddress)
		
		def isLoggedIn(self, username):
				return self.users[username]["isLoggedIn"]

		def logOut(self, username):
				self.users[username]["isLoggedIn"] = False

		def logOutIP(self, ipaddress, port):
				for username in self.users:
						if self.users[username]["ipaddress"] == ipaddress and self.users[username]["port"] == port:
								self.users[username]["isLoggedIn"] = False

		def logAllOut(self):
				for username in self.users:
						self.users[username]["isLoggedIn"] = False

		def signUp(self, username, password, ipaddress, port):
				self.users[username] = {"ipaddress": ipaddress, "port": port, "isLoggedIn": True}
				db.addNewUser(username, password, ipaddress)

class Card():
		def __init__(self, master, pos, numberColor, labelColor, labelText):
				self.valueLabel = tk.Label(master, text="000,000,000", background=numberColor[0], foreground=numberColor[1], justify="center", font=FONT_BOLD)
				self.valueLabel.place(x=pos[0], y=pos[1], width=260, height=40)
				self.label = tk.Label(master, text=labelText, background=labelColor[0], foreground=labelColor[1], justify="center")
				self.label.place(x=pos[0], y=(pos[1] + 40), width=260)
		
		def setValue(self, value):
				self.valueLabel.config(text=value)

class Countdown():
		def __init__(self, master, pos, interval):
				self.interval = interval
				
				self.hour = tk.StringVar()
				self.minute = tk.StringVar()
				self.second = tk.StringVar()

				self.hourEntry = tk.Entry(master, textvariable=self.hour, width=4, state="readonly")
				self.hourEntry.place(x=pos[0], y=pos[1])
				self.minuteEntry = tk.Entry(master, textvariable=self.minute, width=4, state="readonly")
				self.minuteEntry.place(x=(pos[0] + 40), y=pos[1])
				self.secondEntry = tk.Entry(master, textvariable=self.second, width=4, state="readonly")
				self.secondEntry.place(x=(pos[0] + 80), y=pos[1])

				self.update()

		def update(self):
				self.hour.set("{:02d}h".format(self.interval // 3600))
				self.minute.set("{:02d}m".format(self.interval % 3600 // 60))
				self.second.set("{:02d}s".format(self.interval % 60))
				
class TabTracker(ttk.Frame):
		def __init__(self, master):
				ttk.Frame.__init__(self, master)

				tk.Label(self, text="Stats Overview").place(x=10, y=10)

				self.dateComboValue = tk.StringVar()
				self.dateCombo = ttk.Combobox(self, textvariable=self.dateComboValue)
				self.dateCombo.place(x=10, y=40, width=280)
				self.dateCombo.bind('<<ComboboxSelected>>', self.onSelect)
				
				self.countryComboValue = tk.StringVar()
				self.countryCombo = ttk.Combobox(self, textvariable=self.countryComboValue)
				self.countryCombo.place(x=10, y=75, width=280)
				self.countryCombo.bind('<<ComboboxSelected>>', self.onSelect)
				

				bgFrame = tk.Frame(self, highlightbackground="#333", highlightthickness=1, bg="#aaa")
				bgFrame.place(x=10, y=110, width=280, height=250)

				self.casesCard = Card(bgFrame, (10, 10), ("#fff5f5", "#e53e3e"), ("#fed7d7", "#e53e3e"), "Cases")
				self.recoveredCard = Card(bgFrame, (10, 90), ("#f0fff4", "#38a169"), ("#c6f6d5", "#38a169"), "Recovered")
				self.deathsCard = Card(bgFrame, (10, 170), ("#edf2f7", "#718096"), ("#e2e8f0", "#718096"), "Deaths")

				tk.Label(self, text="Next Update:").place(x=10, y=365)

				self.countdownEntries = Countdown(self, (160, 365), UPDATE_INTERVAL)
				
				self.updateThread = threading.Thread(target=self.countdown)
				self.updateThread.setDaemon(True)
				self.updateThread.start()

				self.updateButton = tk.Button(self, text="Update Now", relief="ridge", command=self.updateData)
				self.updateButton.place(x=10, y=395, width=280, height=30)

				self.reset()

		def reset(self):
				self.setDate(db.getDate())
				self.setCountry(db.getCountry(self.getDate()))
				self.updateButton.config(text="Update Now", state="normal")
				self.onSelect()

		def setDate(self, date):
				if len(date) > 0:
						self.dateCombo["values"] = date
						self.dateCombo.current(len(date) - 1)

		def getDate(self):
				return self.dateComboValue.get()

		def setCountry(self, countries):
				if len(countries) > 0:
						self.countryCombo["values"] = countries
						self.countryCombo.current(0)

		def getCountry(self):
				return self.countryComboValue.get()

		def onSelect(self, event=None):
				date = self.getDate()
				country = self.getCountry()
				self.setCovidData(date, country)

		def setCovidData(self, date, country="World"):
				data = db.getCovidData(date, country)
				# print(data)
				self.casesCard.setValue(formatNumber(data["cases"]))
				self.recoveredCard.setValue(formatNumber(data["recovered"]))
				self.deathsCard.setValue(formatNumber(data["deaths"]))

		def updateData(self):
				self.updateButton.config(text="Updating...", state="disabled")
				r = requests.get(COVID_API)
				data = r.json()
				data = list(map(filterData, data))
				date = datetime.datetime.now().strftime("%Y-%m-%d")
				db.updateCovidData(date, data)
				self.reset()
				print("Update Data")

		def countdown(self):
				while True:
						self.countdownEntries.interval -= 1
						self.countdownEntries.update()
						time.sleep(1)
						if self.countdownEntries.interval <= 0:
								self.updateData()
								self.countdownEntries.interval = UPDATE_INTERVAL
								
class TabServer(ttk.Frame):
		def __init__(self, master):
				ttk.Frame.__init__(self, master)

				tk.Label(self, text="Port:").place(x=10, y=10)

				self.port = tk.IntVar()
				self.portEntry = tk.Entry(self, textvariable=self.port)
				self.portEntry.place(x=60, y=11, width=90)
				self.port.set(PORT)

				self.startButton = tk.Button(self, text="Start Server", relief="ridge", command=self.start)
				self.startButton.place(x=160, y=10, width=130, height=27)

				tk.Label(self, text="Connected Users").place(x=10, y=50)
				self.clientTreeview = ttk.Treeview(self, columns=("1", "2"), show="headings")
				self.clientTreeview.place(x=10, y=80, width=280, height=345)
				
				self.clientTreeview.column("1", anchor='w', width=150)
				self.clientTreeview.column("2", anchor='w', width=120)

				self.clientTreeview.heading("1", text ="Username", anchor='w')
				self.clientTreeview.heading("2", text ="IP Address", anchor="w")

				self.client = {}
				self.clientAddress = []
				self.isStart = False

		def start(self):
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

				# try:
				self.socket.bind(('14.243.118.234', self.port.get()))
				self.isStart = True
				print("Server started on port: " + str(self.socket.getsockname()[1]))
				print("IP: " + socket.gethostbyname(socket.gethostname()))
				# except 
				# 		messagebox.showerror("Error", f'Port {self.port.get()} is already in use.')
				# 		return

				self.socketThread = threading.Thread(target=self.listen)
				self.socketThread.setDaemon(True)

				self.socketThread.start()
				self.startButton.config(text="Stop Server", command=self.stop)
				self.portEntry.config(state="disabled")

		def stop(self):
				users.logAllOut()
				self.updateTreeview()
				for client in self.client:
						self.client[client].close()
				self.socket.close()
				self.startButton.config(text="Start Server", command=self.start)
				self.portEntry.config(state="normal")

		def listen(self):
				self.socket.listen()
				while self.isStart:
						try:
								conn, addr = self.socket.accept()
								self.clientAddress.append(f'{addr[0]}:{addr[1]}')
								self.client[self.clientAddress[-1]] = conn
								print(self.clientAddress[-1] + ' connected')
								clientThread = threading.Thread(target=self.handleClient, args=(conn, addr))
								clientThread.setDaemon(True)
								clientThread.start()
						except:
								print("Server stopped")
								return

		def handleClient(self, conn, addr):
				while True:
						try:
								data = conn.recv(MAX_BYTES).decode(FORMAT)
								if not data:
										users.logOutIP(addr[0], addr[1])
										self.updateTreeview()
										self.clientAddress.remove(f'{addr[0]}:{addr[1]}')
										conn.close()
										print(f'{addr[0]}:{addr[1]} disconnected')
										return
								msg = json.loads(data)
								if msg["type"] == LOGIN:
										self.clientLogIn(conn, addr, msg["payload"])
								elif msg["type"] == LOGOUT:
										self.clientLogOut(conn, msg["payload"])
								elif msg["type"] == SIGNUP:
										self.clientSignUp(conn, addr, msg["payload"])
								elif msg["type"] == GETDATE:
										self.clientGetDate(conn)
								elif msg["type"] == GETCOUNTRY:
										self.clientGetCountry(conn, msg["payload"])
								elif msg["type"] == GETCOVIDDATA:
										self.clientGetCovidData(conn, msg["payload"])
						except:
								users.logOutIP(addr[0], addr[1])
								self.clientAddress.remove(f'{addr[0]}:{addr[1]}')
								self.updateTreeview()
								print(f'{addr[0]}:{addr[1]} disconnected')
								return

		def clientLogIn(self, conn, addr, payload):
				hasUser = db.hasUser(payload["username"])
				if not hasUser:
						conn.send(messageCreate(LOGIN_FAILED, {"message": "User not found"}))
						return
				if users.isLoggedIn(payload["username"]):
						conn.send(messageCreate(LOGIN_FAILED, {"message": "User already logged in"}))
						return
				dbPassword = db.getPassword(payload["username"])
				if dbPassword == payload["password"]:
						users.logIn(payload["username"], addr[0], addr[1])
						self.updateTreeview()
						conn.send(messageCreate(LOGIN_SUCCESS, {"message": "Login Success"}))
				else:
						conn.send(messageCreate(LOGIN_FAILED, {"message": "Wrong Password"}))

		def clientLogOut(self, conn, payload):
				users.logOut(payload["username"])
				self.updateTreeview()
				conn.send(messageCreate(LOGOUT_SUCCESS, {"message": "Logout Success"}))

		def clientSignUp(self, conn, addr, payload):
				hasUser = db.hasUser(payload["username"])
				if hasUser:
						conn.send(messageCreate(SIGNUP_FAILED, {"message": "User already exists"}))
						return
				users.signUp(payload["username"], payload["password"], addr[0], addr[1])
				self.updateTreeview()
				conn.send(messageCreate(SIGNUP_SUCCESS, {"message": "Signup Success"}))

		def clientGetDate(self, conn):
				conn.send(messageCreate(GETDATE, {"date": db.getDate()}))

		def clientGetCountry(self, conn, payload):
				conn.send(messageCreate(GETCOUNTRY, {"country": db.getCountry(payload["date"])}))

		def clientGetCovidData(self, conn, payload):
				conn.send(messageCreate(GETCOVIDDATA, {"data": db.getCovidData(payload["date"], payload["country"])}))

		def updateTreeview(self):
				self.clientTreeview.delete(*self.clientTreeview.get_children())
				for username in users.users:
						if users.users[username]["isLoggedIn"]:
								self.clientTreeview.insert("", "end", text="", values=(username, f'{users.users[username]["ipaddress"]}:{users.users[username]["port"]}'))

class TabAbout(ttk.Frame):
		def __init__(self, master):
				ttk.Frame.__init__(self, master)

				self.vnuhcmLabel = tk.Label(self, text="VNU HCM", font=FONT_BOLD, foreground="#28306a", cursor="hand2")
				self.vnuhcmLabel.place(x=40, y=10)
				self.hcmusLabel = tk.Label(self, text="HCMUS", font=FONT_BOLD, foreground="#3c5182", cursor="hand2")
				self.hcmusLabel.place(x=140, y=10)
				self.fitLabel = tk.Label(self, text="FIT", font=FONT_BOLD, foreground="#0184cc", cursor="hand2")
				self.fitLabel.place(x=220, y=10)
				tk.Label(self, text="-", font=FONT_BOLD).place(x=127, y=10)
				tk.Label(self, text="-", font=FONT_BOLD).place(x=208, y=10)
				tk.Label(self, text="Computer Networking").place(relx=0.5, y=50, anchor="center")

				self.logo = ImageTk.PhotoImage(Image.open("image/hcmus_logo.png").resize((200, 200), Image.ANTIALIAS))
				self.logoLabel = tk.Label(self, image = self.logo, cursor="hand2")
				self.logoLabel.place(relx=0.5, y=170, anchor="center")

				tk.Label(self, text="The project is developed by:").place(relx=0.5, y=280, anchor="center")
				self.std1Label = tk.Label(self, text="20120488 - Thái Nguyễn Việt Hùng", cursor="hand2", foreground="blue")
				self.std1Label.place(x=15, y=300)
				self.std2Label = tk.Label(self, text="20120489 - Võ Phi Hùng", cursor="hand2", foreground="blue")
				self.std2Label.place(x=15, y=330)
				self.std3Label = tk.Label(self, text="20120496 - Nguyễn Cảnh Huy", cursor="hand2", foreground="blue")
				self.std3Label.place(x=15, y=360)
				
				tk.Label(self, text="More info is on the").place(x=12, y=390)
				self.githubLabel = tk.Label(self, text="GitHub repository", cursor="hand2", foreground="blue", justify="left")
				self.githubLabel.place(x=157, y=390)

				self.vnuhcmLabel.bind("<Button-1>", lambda event: webbrowser.open("https://vnuhcm.edu.vn/"))
				self.hcmusLabel.bind("<Button-1>", lambda event: webbrowser.open("https://hcmus.edu.vn/"))
				self.fitLabel.bind("<Button-1>", lambda event: webbrowser.open("https://fit.hcmus.edu.vn/"))
				self.logoLabel.bind("<Button-1>", lambda event: webbrowser.open("https://hcmus.edu.vn/"))

				self.std1Label.bind("<Button-1>", lambda event: webbrowser.open("mailto://20120488@student.hcmus.edu.vn"))
				self.std2Label.bind("<Button-1>", lambda event: webbrowser.open("mailto://20120489@student.hcmus.edu.vn"))
				self.std3Label.bind("<Button-1>", lambda event: webbrowser.open("mailto://20120496@student.hcmus.edu.vn"))
				self.githubLabel.bind("<Button-1>", lambda event: webbrowser.open("https://github.com/phihungtf/socket-covid19-tracker"))

class ServerApp():
		def __init__(self):
				self.gui = tk.Tk()
				self.gui.geometry('300x460')
				self.gui.title('Covid-19 Tracker Server')
				self.gui.resizable(width=False, height=False)
				self.gui.option_add("*Font", FONT)

				self.tabControl = ttk.Notebook(self.gui)

				self.tabServer = TabServer(self.tabControl)
				self.tabTracker = TabTracker(self.tabControl)
				self.tabAbout = TabAbout(self.tabControl)

				self.tabControl.add(self.tabServer, text='Server')
				self.tabControl.add(self.tabTracker, text='Tracker')
				self.tabControl.add(self.tabAbout, text='About')
				self.tabControl.pack(expand=1, fill="both")

db = Database(DATABASE_FILENAME["user"], DATABASE_FILENAME["covid"])
users = Users()
app = ServerApp()

def __main__():
		app.gui.mainloop()

if __name__ == '__main__':
		__main__()
