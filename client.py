import json
import socket
import threading
import locale
import hashlib

import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 55555
MAX_BYTES = 1024
FORMAT = "utf-8"

SIGNUP = "SIGNUP"
LOGIN = "LOGIN"
LOGOUT = "LOGOUT"
TRACKER = "TRACKER"
GETDATE = "GETDATE"
GETCOUNTRY = "GETCOUNTRY"
GETCOVIDDATA = "GETCOVIDDATA"
LOGIN_SUCCESS = "LOGIN_SUCCESS"
LOGIN_FAILED = "LOGIN_FAILED"
LOGOUT_SUCCESS = "LOGOUT_SUCCESS"
LOGOUT_FAILED = "LOGOUT_FAILED"
SIGNUP_SUCCESS = "SIGNUP_SUCCESS"
SIGNUP_FAILED = "SIGNUP_FAILED"

FONT = ("Tahoma", 13)
FONT_BOLD = ("Tahoma", 13, "bold")

locale.setlocale(locale.LC_ALL, 'en_US')

def messageCreate(type, payload):
		return json.dumps({"type": type, "payload": payload}).encode(FORMAT)

def formatNumber(number):
    if number == None: return "N/A"
    return locale.format_string("%d", int(number), grouping=True)

class LinkLabel(tk.Label):
		def __init__(self, master, text, fg, font, command):
				super().__init__(master, text=text, fg=fg, font=font, cursor="hand2")
				self.linkFont = tk.font.Font(family=font[0], size=font[1], underline=True)
				self.normalFont = tk.font.Font(family=font[0], size=font[1])
				self.command = command
				self.bind("<Enter>", lambda e: self.configure(font=self.linkFont))
				self.bind("<Leave>", lambda e: self.configure(font=self.normalFont))
				self.bind("<Button-1>", lambda e: self.command())

		def disable(self):
				self.configure(state="disabled")
				self.unbind("<Enter>")
				self.unbind("<Leave>")
				self.unbind("<Button-1>")
				self.configure(cursor="arrow")

		def enable(self):
				self.configure(state="normal")
				self.bind("<Enter>", lambda e: self.configure(font=self.linkFont))
				self.bind("<Leave>", lambda e: self.configure(font=self.normalFont))
				self.bind("<Button-1>", lambda e: self.command())
				self.configure(cursor="hand2")


class LogInFrame():
		def __init__(self, master, showFrameCmd, connectCmd, logInCmd, disconnectCmd):
				self.isConnected = False
				self.frame = tk.Frame(master)

				tk.Label(self.frame, text="Connect to the server").place(x=10, y=10)

				self.ip = tk.StringVar()
				self.ipEntry = tk.Entry(self.frame, textvariable=self.ip)
				self.ipEntry.place(x=12, y=40, width=192)
				self.ip.set(HOST)

				self.port = tk.IntVar()
				self.portEntry = tk.Entry(self.frame, textvariable=self.port)
				self.portEntry.place(x=212, y=40, width=70)
				self.port.set(PORT)

				self.connectButton = tk.Button(self.frame, text="Connect", relief="ridge", command=self.connect)
				self.connectButton.place(x=12, y=70, width=270)

				tk.Label(self.frame, text="LOG IN", font=FONT_BOLD).place(x=112, y=115)
				tk.Label(self.frame, text="Username").place(x=10, y=140)

				self.usernameEntry = tk.Entry(self.frame)
				self.usernameEntry.place(x=12, y=170, width=270)

				tk.Label(self.frame, text="Password").place(x=10, y=200)

				self.passwordEntry = tk.Entry(self.frame, show="•")
				self.passwordEntry.place(x=12, y=230, width=270)

				self.logInButton = tk.Button(self.frame, text="Log In", relief="ridge", command=self.logIn)
				self.logInButton.place(x=12, y=270, width=270)

				tk.Label(self.frame, text="Don't have an account?",	font=("Tahoma", 10)).place(x=45, y=315)
				self.signUpButton = LinkLabel(self.frame, text="Sign Up!", fg="blue", font=("Tahoma", 10), command=lambda: showFrameCmd(SIGNUP))
				self.signUpButton.place(x=185, y=315)

				self.reset()
				self.connectCmd = connectCmd
				self.logInCmd = logInCmd
				self.disconnectCmd = disconnectCmd
				self.showFrameCmd = showFrameCmd

		def reset(self):
				self.usernameEntry.delete(0, tk.END)
				self.passwordEntry.delete(0, tk.END)
				self.disableLogIn()
				self.enableConnect()

		def connect(self):
				self.disableConnect()
				if self.connectCmd(self.ip.get(), self.port.get()):
					self.enableLogIn()
				else:
					self.enableConnect()
				# print(self.socket)

		def disconnect(self):
				self.enableConnect()
				self.disconnectCmd()
				self.disableLogIn()

		def logIn(self):
				username = self.usernameEntry.get()
				password = self.passwordEntry.get()
				self.passwordEntry.delete(0, tk.END)
				self.disableLogIn()

				if username == "" or password == "":
						messagebox.showerror("Error", "Username or password is empty!")
						self.enableLogIn()
						return

				self.enableLogIn()
				if self.logInCmd(username, password):
						self.showFrameCmd(TRACKER)


		def disableLogIn(self):
				self.logInButton.config(state="disabled")
				self.usernameEntry.config(state="disabled")
				self.passwordEntry.config(state="disabled")
				self.signUpButton.disable()

		def enableLogIn(self):
				self.logInButton.config(state="normal")
				self.usernameEntry.config(state="normal")
				self.passwordEntry.config(state="normal")
				self.signUpButton.enable()

		def disableConnect(self):
				self.connectButton.config(text="Disconnect", command=self.disconnect)
				self.ipEntry.config(state="disabled")
				self.portEntry.config(state="disabled")

		def enableConnect(self):
				self.connectButton.config(text="Connect", command=self.connect)
				self.ipEntry.config(state="normal")
				self.portEntry.config(state="normal")


class SignUpFrame():
		def __init__(self, master, showFrameCmd, signUpCmd):
				self.frame = tk.Frame(master)
				# self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

				tk.Label(self.frame, text="SIGN UP", font=FONT_BOLD).place(x=105, y=10)
				tk.Label(self.frame, text="Username", font=FONT).place(x=10, y=50)

				self.usernameEntry = tk.Entry(self.frame)
				self.usernameEntry.place(x=12, y=80, width=270)

				tk.Label(self.frame, text="Password", font=FONT).place(x=10, y=110)

				self.passwordEntry = tk.Entry(self.frame, show="•")
				self.passwordEntry.place(x=12, y=140, width=270)

				tk.Label(self.frame, text="Confirm Password", font=FONT).place(x=10, y=170)

				self.confirmPasswordEntry = tk.Entry(self.frame, show="•")
				self.confirmPasswordEntry.place(x=12, y=200, width=270)

				self.signUpButton = tk.Button(self.frame, text="Sign Up", font=FONT, relief="ridge", command=self.signUp)
				self.signUpButton.place(x=12, y=240, width=270)

				tk.Label(self.frame, text="Already have an account?", font=("Tahoma", 10)).place(x=35, y=295)
				self.logInButton = LinkLabel(self.frame, text="Log In!", fg="blue", font=("Tahoma", 10), command=lambda: showFrameCmd(LOGIN))
				self.logInButton.place(x=195, y=295)

				self.signUpCmd = signUpCmd
				self.showFrameCmd = showFrameCmd

		def signUp(self):
				username = self.usernameEntry.get()
				password = self.passwordEntry.get()
				confirmPassword = self.confirmPasswordEntry.get()

				self.passwordEntry.delete(0, tk.END)
				self.confirmPasswordEntry.delete(0, tk.END)

				if username == "" or password == "" or confirmPassword == "":
						messagebox.showerror("Error", "Username or password is empty!")
						return

				if password != confirmPassword:
						messagebox.showerror("Error", "Passwords do not match!")
						return

				if self.signUpCmd(username, password):
						self.usernameEntry.delete(0, tk.END)
						self.showFrameCmd(TRACKER)
				
class Card():
    def __init__(self, master, pos, numberColor, labelColor, labelText):
        self.valueLabel = tk.Label(master, text="000,000,000", background=numberColor[0], foreground=numberColor[1], justify="center", font=FONT_BOLD)
        self.valueLabel.place(x=pos[0], y=pos[1], width=260, height=40)
        self.label = tk.Label(master, text=labelText, background=labelColor[0], foreground=labelColor[1], justify="center")
        self.label.place(x=pos[0], y=(pos[1] + 40), width=260)
    
    def setValue(self, value):
        self.valueLabel.config(text=value)

class TrackerFrame():
		def __init__(self, master, showFrameCmd, logOutCmd, getDateCmd, getCountryCmd, getCovidDataCmd):
				self.frame = tk.Frame(master)

				tk.Label(self.frame, text="Stats Overview").place(x=10, y=10)

				self.dateComboValue = tk.StringVar()
				self.dateCombo = ttk.Combobox(self.frame, textvariable=self.dateComboValue)
				self.dateCombo.place(x=10, y=40, width=280)
				self.dateCombo.bind('<<ComboboxSelected>>', self.onSelect)

				self.countryComboValue = tk.StringVar()
				self.countryCombo = ttk.Combobox(self.frame, textvariable=self.countryComboValue)
				self.countryCombo.place(x=10, y=75, width=280)
				self.countryCombo.bind('<<ComboboxSelected>>', self.onSelect)

				bgFrame = tk.Frame(self.frame, highlightbackground="#333", highlightthickness=1, bg="#aaa")
				bgFrame.place(x=10, y=110, width=280, height=250)

				self.casesCard = Card(bgFrame, (10, 10), ("#fff5f5", "#e53e3e"), ("#fed7d7", "#e53e3e"), "Cases")
				self.recoveredCard = Card(bgFrame, (10, 90), ("#f0fff4", "#38a169"), ("#c6f6d5", "#38a169"), "Recovered")
				self.deathsCard = Card(bgFrame, (10, 170), ("#edf2f7", "#718096"), ("#e2e8f0", "#718096"), "Deaths")

				self.refreshButton = tk.Button(self.frame, text="Refresh", relief="ridge", command=self.reset)
				self.refreshButton.place(x=10, y=370, width=280, height=30)

				self.logOutButton = tk.Button(self.frame, text="Log Out", relief="ridge", command=self.logOut)
				self.logOutButton.place(x=210, y=10, width=80, height=27)
				
				self.showFrameCmd = showFrameCmd
				self.logOutCmd = logOutCmd
				self.getDateCmd = getDateCmd
				self.getCountryCmd = getCountryCmd
				self.getCovidDataCmd = getCovidDataCmd

		def reset(self):
				date = self.getDateCmd()
				if date == False:
						self.showFrameCmd(LOGIN)
						return
				self.setDate(date)
				country = self.getCountryCmd(self.getDate())
				if country == False:
						self.showFrameCmd(LOGIN)
						return
				self.setCountry(country)
				self.onSelect()

		def logOut(self):
				self.logOutCmd()
				self.showFrameCmd(LOGIN)

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
				data = self.getCovidDataCmd(date, country)
				if data == False:
						self.showFrameCmd(LOGIN)
						return
				# print(data)
				self.casesCard.setValue(formatNumber(data["cases"]))
				self.recoveredCard.setValue(formatNumber(data["recovered"]))
				self.deathsCard.setValue(formatNumber(data["deaths"]))
				


class ClientApp(tk.Tk):
		def __init__(self):
				self.gui = tk.Tk()
				self.gui.geometry('300x350')
				self.gui.title('Covid-19 Tracker Client')
				self.gui.resizable(width=False, height=False)
				self.gui.option_add("*Font", FONT)

				self.socket = None
				self.isConnected = False
				self.username = None

				self.frames = {
						SIGNUP: SignUpFrame(self.gui, self.showFrame, self.signUp),
						LOGIN: LogInFrame(self.gui, self.showFrame, self.connect, self.logIn, self.disconnect),
						TRACKER: TrackerFrame(self.gui, self.showFrame, self.logOut, self.getDate, self.getCountry, self.getCovidData)
				}

				self.currentFrame = LOGIN
				self.isLoggedIn = False
				self.showFrame(self.currentFrame)

		def showFrame(self, frame):
				self.frames[self.currentFrame].frame.pack_forget()
				self.currentFrame = frame
				self.frames[self.currentFrame].frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

				if self.currentFrame == LOGIN:
						self.gui.geometry("300x350")
				elif self.currentFrame == SIGNUP:
						self.gui.geometry("300x340")
				elif self.currentFrame == TRACKER:
						self.gui.geometry("300x420")

		def connect(self, ip, port):
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				try:
						self.socket.connect((ip, port))
						self.isConnected = True
						return True
				except:
						messagebox.showerror("Error", "Could not connect to server")
						return False
				# print(self.socket)

		def disconnect(self):
				self.isConnected = False
				self.socket.close()

		def logIn(self, username, password):
				try:
						self.socket.send(messageCreate(LOGIN, {"username": username, "password": str(hashlib.md5(password.encode(FORMAT)).hexdigest())}))
						response = self.socket.recv(MAX_BYTES).decode(FORMAT)
						response = json.loads(response)
						if response["type"] == LOGIN_SUCCESS:
								# messagebox.showinfo("Success", "Logged in successfully!")
								self.isLoggedIn = True
								self.username = username
								self.frames[TRACKER].reset()
								return True
						else:
								messagebox.showerror("Error", response["payload"]["message"])
								return False
				except:
						messagebox.showerror("Error", "Server disconnected")
						self.frames[LOGIN].reset()
						return False

		def logOut(self):
				try:
						self.socket.send(messageCreate(LOGOUT, {"username": self.username}))
						response = self.socket.recv(MAX_BYTES).decode(FORMAT)
						response = json.loads(response)
						if response["type"] == LOGOUT_SUCCESS:
								self.isLoggedIn = False
								self.username = None
								return True
						else:
								messagebox.showerror("Error", response["payload"]["message"])
								return False
				except:
						messagebox.showerror("Error", "Server disconnected")
						self.frames[LOGIN].reset()
						return False

		def signUp(self, username, password):
				try:
						self.socket.send(messageCreate(SIGNUP, {"username": username, "password": str(hashlib.md5(password.encode(FORMAT)).hexdigest())}))
						response = self.socket.recv(MAX_BYTES).decode(FORMAT)
						response = json.loads(response)
						if response["type"] == SIGNUP_SUCCESS:
								self.isLoggedIn = True
								self.username = username
								self.frames[TRACKER].reset()
								# messagebox.showinfo("Success", "Signed up successfully!")
								return True
						else:
								messagebox.showerror("Error", response["payload"]["message"])
								return False
				except:
						messagebox.showerror("Error", "Server disconnected")
						self.frames[LOGIN].reset()
						self.showFrame(LOGIN)
						return False

		def getDate(self):
				if self.isLoggedIn:
					try:
							self.socket.send(messageCreate(GETDATE, {}))
							response = self.socket.recv(MAX_BYTES).decode(FORMAT)
							response = json.loads(response)
							return response["payload"]["date"]
					except:
							messagebox.showerror("Error", "Server disconnected")
							self.frames[LOGIN].reset()
							return False

		def getCountry(self, date):
				if self.isLoggedIn:
					try:
							self.socket.send(messageCreate(GETCOUNTRY, {"date": date}))
							response = self.socket.recv(4 * MAX_BYTES).decode(FORMAT)
							response = json.loads(response)
							return response["payload"]["country"]
					except:
							messagebox.showerror("Error", "Server disconnected")
							self.frames[LOGIN].reset()
							return False
		
		def getCovidData(self, date, country):
				if self.isLoggedIn:
					try:
							self.socket.send(messageCreate(GETCOVIDDATA, {"date": date, "country": country}))
							response = self.socket.recv(MAX_BYTES).decode(FORMAT)
							response = json.loads(response)
							return response["payload"]["data"]
					except:
							messagebox.showerror("Error", "Server disconnected")
							self.frames[LOGIN].reset()
							return False

		def on_closing(self):
				if messagebox.askokcancel("Quit", "Do you want to quit?"):
						self.destroy()
						try:
								if(self.user == ''):
										return
								else:
										username = self.user
										msg = LOGOUT
										client.sendall(msg.encode(FORMAT))
										client.sendall(username.encode(FORMAT))
						except:
								pass



class Background_Client(tk.Frame):
		def __init__(self, parent, control):
				tk.Frame.__init__(self, parent)

				self.img = Image.open("image/login_client.png")
				self.render = ImageTk.PhotoImage(self.img)

				canvas = Canvas(self, width=self.img.size[0], height=self.img.size[1])
				canvas.create_image(0, 0, anchor=NW, image=self.render)
				canvas.pack(fill=BOTH, expand=1)

				self.notice = tk.Label(self, text="", bg="#6184D6", fg='red')
				self.entry_username = tk.Entry(self, width=40, bg='white')
				self.entry_password = tk.Entry(self, width=40, bg='white', show="*")
				self.entry_username.place(x=607, y=260, height=40)
				self.entry_password.place(x=607, y=340, height=40)
				self.button_log = tk.Button(self, width=10, cursor="hand2", text="LOG IN",
																		bg="#7B96D4", fg='floral white', command=lambda: control.logIn(self, client))
				self.button_sign = tk.Button(self, width=10, cursor="hand2", text="SIGN UP",
																		 bg="#7B96D4", fg='floral white', command=lambda: control.signUp(self, client))
				self.button_log.place(x=607, y=410, height=40)
				self.button_sign.place(x=810, y=410, height=40)
				self.notice.place(x=670, y=380)


class Home_Client(tk.Frame):
		def __init__(self, parent, control):
				tk.Frame.__init__(self, parent)

				self.img = Image.open("image/home_client.png")
				self.render = ImageTk.PhotoImage(self.img)

				canvas = Canvas(self, width=self.img.size[0], height=self.img.size[1])
				canvas.create_image(0, 0, anchor=NW, image=self.render)
				canvas.place(x=0, y=0)

				self.button_back = tk.Button(self, width=15, cursor="hand2", text="LOG OUT",
																		 bg="#20639b", fg='floral white', command=lambda: control.logOut(client, control))
				self.button_back.place(x=400, y=10)

				self.entry_search = tk.Entry(self, width=30, bg='white')
				self.button_search = tk.Button(self, width=10, cursor="hand2", text="SEARCH",
																			 bg="#7B96D4", fg='floral white', command=lambda: self.Search())
				self.entry_search.place(x=20, y=180, height=30)
				self.button_search.place(x=250, y=180)

				self.data = tk.Listbox(self, height=10, width=40, bg='floral white',
															 activestyle='dotbox', font="Helvetica", fg='#20639b')
				self.data.place(x=70, y=230)

		def Search(self):
				try:
						msg = SEARCH
						client.sendall(msg.encode(FORMAT))
						country = self.entry_search.get()
						client.sendall(country.encode(FORMAT))

						info = client.recv(HEADER).decode(FORMAT)
						show = info.split("\n")
						self.data.delete(0, len(show))

						for i in range(len(show)):
								self.data.insert(i, show[i])

				except:
						print("Error: Server is not responding")


def __main__():
		app = ClientApp()
		app.gui.mainloop()


if __name__ == '__main__':
		__main__()
