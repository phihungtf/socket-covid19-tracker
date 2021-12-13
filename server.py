import socket
import threading
import json
import hashlib
from tkinter import font
from tkinter.constants import SW
import requests
import schedule
import time
import datetime
import locale

import tkinter as tk
from tkinter import ttk
# from tkinter import messagebox
# from tkinter import *
# from tkinter.ttk import *
# from typing import Sized
# from PIL import Image, ImageTk

# HOST = "127.0.0.1"
PORT = 55555
MAX_BYTES = 1024
FORMAT = "utf-8"
# ADDR = (HOST, PORT)
DISCONNECT_MESSAGE = "Disconnect"

SIGNUP = "SIGNUP"
LOGIN = "LOGIN"
LOGOUT = "LOGOUT"
SEARCH = "SEARCH"
LOGIN_SUCCESS = "LOGIN_SUCCESS"
LOGIN_NOUSER = "LOGIN_NOUSER"
LOGIN_WRONGPASS = "LOGIN_WRONGPASS"


COVID_API = "https://coronavirus-19-api.herokuapp.com/countries"

FONT = ("Tahoma", 13)
FONT_BOLD = ("Tahoma", 13, "bold")

UPDATE_INTERVAL = 3600 # 1 hour

DATABASE_FILENAME = {
    "user": "database/user.json",
    "covid": "database/covid.json"
}

locale.setlocale(locale.LC_ALL, 'en_US')

LiveAccount = []


def addNewAccount(username, password):
    password = str(hashlib.md5(password.strip().encode(FORMAT)).hexdigest())
    newUser = {
        'username': username,
        'password': password
    }
    with open(DATABASE_FILENAME["user"], 'r') as fin:
        data = json.load(fin)
        fin.close()
    data['users'].append(newUser)
    with open(DATABASE_FILENAME["user"], 'w') as fout:
        json.dump(data, fout, indent=4)
        fout.close()


def checkClientSignUp(username):
    with open(DATABASE_FILENAME["user"], 'r') as fin:
        data = json.load(fin)
        fin.close()

    for i in data["users"]:
        if(i["username"].strip() == username.strip()):
            return False
    return True


def clientSignUp(conn):
    username = conn.recv(MAX_BYTES).decode(FORMAT)
    conn.sendall(username.encode(FORMAT))

    password = conn.recv(MAX_BYTES).decode(FORMAT)

    username = username.strip()

    accepted = checkClientSignUp(username)
    print("accept:", accepted)
    conn.sendall(str(accepted).encode(FORMAT))
    if accepted:
        addNewAccount(username, password)

    print("End Sign Up\n")


def checkLivedAccount(username):
    for i in LiveAccount:
        if i == username:
            return True
    return False


def checkClientLogin(username, password):
    password = str(hashlib.md5(password.strip().encode(FORMAT)).hexdigest())
    if checkLivedAccount(username) == True:
        return 0

    with open(DATABASE_FILENAME["user"], 'r') as fin:
        data = json.load(fin)
        fin.close()

    for i in data["users"]:
        if(i["username"].strip() == username.strip() and i["password"] == password):
            return 1
    return 2


def clientLogIn(conn):
    username = conn.recv(MAX_BYTES).decode(FORMAT)
    conn.sendall(username.encode(FORMAT))

    password = conn.recv(MAX_BYTES).decode(FORMAT)

    accepted = checkClientLogin(username, password)
    if accepted == 1:
        LiveAccount.append(username)

    print("accepted:", accepted)
    conn.sendall(str(accepted).encode(FORMAT))
    print("End Log In\n")


def clientSearch(conn):
    with open(DATABASE_FILENAME["covid"], 'r') as f:
        data = json.load(f)
        f.close()

    country = conn.recv(MAX_BYTES).decode(FORMAT)
    info = []
    key = datetime.datetime.now().strftime("%Y-%m-%d")
    for i in data[key]:
        if (i["country"] == country):
            info.append("Country: " + str(i["country"]))
            info.append("Cases: " + str(i["cases"]))
            info.append("Deaths: " + str(i["deaths"]))
            info.append("Recovered: " + str(i["recovered"]))
            info = "\n".join(info)
            conn.sendall(str(info).encode(FORMAT))


def clientLogOut(conn):
    username = conn.recv(MAX_BYTES).decode(FORMAT)
    for i in LiveAccount:
        if i == username:
            LiveAccount.remove(i)
            conn.sendall("True".encode(FORMAT))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        msg = conn.recv(MAX_BYTES).decode(FORMAT)

        if(msg == LOGIN):
            clientLogIn(conn)
        elif(msg == SIGNUP):
            clientSignUp(conn)
        elif(msg == SEARCH):
            clientSearch(conn)
        elif(msg == LOGOUT):
            clientLogOut(conn)

    conn.close()


def startServer():
    try:
        print(HOST)
        print("Waiting for Client")

        while True:
            conn, addr = s.accept()

            clientThread = threading.Thread(
                target=handle_client, args=(conn, addr))
            # sThread.daemon = True
            clientThread.start()

    except KeyboardInterrupt:
        print("Error")
        s.close()
    finally:
        s.close()
        print("end")


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
        key = datetime.datetime.now().strftime("%Y-%m-%d")
        # print(key)
        with open(DATABASE_FILENAME["covid"], 'r+') as file:
            file_data = json.load(file)
            # print(file_data)
            file_data[key] = data
            file.seek(0)
            json.dump(file_data, file, indent=2)
            file.close()

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

        # self.clientTreeview.insert("", "end", text="", values=("phihungtf", "1.2.3.4"))
        # self.clientTreeview.insert("", "end", text="", values=("phihungtf", "1.2.3.4"))
        # self.clientTreeview.insert("", "end", text="", values=("phihungtf", "1.2.3.4"))
        # self.clientTreeview.insert("", "end", text="", values=("phihungtf", "1.2.3.4"))
        # self.clientTreeview.insert("", "end", text="", values=("phihungtf", "1.2.3.4"))
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.socketThread = threading.Thread(target=self.listen)
        self.socketThread.setDaemon(True)

    def start(self):
        self.socket.bind(('', self.port.get()))
        self.socketThread.start()
        self.startButton.config(text="Stop Server", command=self.stop)
        self.portEntry.config(state="disabled")

    def stop(self):
        self.socket.close()
        self.socketThread.join()
        self.startButton.config(text="Start Server", command=self.start)
        self.portEntry.config(state="normal")

    def listen(self):
        print(self.socket)
        self.socket.listen()
        while True:
            conn, addr = self.socket.accept()
            clientThread = threading.Thread(target=self.handleClient, args=(conn, addr))
            clientThread.setDaemon(True)
            clientThread.start()
            # self.clientTreeview.insert("", "end", text="", values=(data, addr[0]))

    def handleClient(self, conn, addr):
        while True:
            data = conn.recv(MAX_BYTES).decode(FORMAT)
            print(data)
            msg = json.loads(data)
            if msg["type"] == LOGIN:
                self.clientLogIn(conn, addr, msg["payload"])
        # self.clientTreeview.insert("", "end", text="", values=(data, addr[0]))
        conn.close()

    def clientLogIn(self, conn, addr, payload):
        hasUser = db.hasUser(payload["username"])
        if hasUser:
            dbPassword = db.getPassword(payload["username"])
            if dbPassword == payload["password"]:
                self.clientTreeview.insert("", "end", text="", values=(payload["username"], addr[0]))
                conn.send(messageCreate(LOGIN_SUCCESS, {"message": "Login Success"}))
            else:
                conn.send(messageCreate(LOGIN_WRONGPASS, {"message": "Wrong Password"}))
        else:
            conn.send(messageCreate(LOGIN_NOUSER, {"message": "User not found"}))


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
        tabAbout = ttk.Frame(self.tabControl)

        self.tabControl.add(self.tabServer, text='Server')
        self.tabControl.add(self.tabTracker, text='Tracker')
        self.tabControl.add(tabAbout, text='About')
        self.tabControl.pack(expand=1, fill="both")

        # self.title("Covid Information")
        # self.geometry("1000x600")
        # self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # self.resizable(width=False, height=False)
        # self.option_add("*Font", FONT)

        # container = tk.Frame(self)
        # container.place(x=0, y=0)

        # container.grid_rowconfigure(0, weight=1)
        # container.grid_columnconfigure(0, weight=1)

        # self.frames = {}
        # for F in (Background_Server, Home_Server):
        #     frame = F(container, self)

        #     self.frames[F] = frame

        #     frame.grid(row=0, column=0, sticky="nsew")

        # self.showFrame(Background_Server)
        # self.thread = thread

        # self.showFrame(Home_Server)
    def showFrame(self, container):
        frame = self.frames[container]
        if container == Home_Server:
            self.geometry("500x500")

        else:
            self.geometry("1000x600")
        frame.tkraise()

    def logIn(self, curFrame):

        username = curFrame.entry_username.get()
        password = curFrame.entry_password.get()
        if password == "":
            curFrame.notice["text"] = "Password can not be empty !"
            return

        if username == "admin" and password == "1":
            self.showFrame(Home_Server)
            curFrame.notice["text"] = ""
            self.thread.start()
        else:
            curFrame.notice["text"] = "Invalid username or password !"

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()


# class Background_Server(tk.Frame):
#     def __init__(self, parent, control):
#         tk.Frame.__init__(self, parent)

#         self.img = Image.open("image/login_server.png")
#         self.render = ImageTk.PhotoImage(self.img)

#         canvas = Canvas(self, width=self.img.size[0], height=self.img.size[1])
#         canvas.create_image(0, 0, anchor=NW, image=self.render)
#         canvas.pack(fill=BOTH, expand=1)

#         self.notice = tk.Label(self, text="", bg="#6184D6", fg='white')
#         self.entry_username = tk.Entry(self, width=40, bg='white')
#         self.entry_password = tk.Entry(self, width=40, bg='white', show="•")
#         self.entry_username.place(x=607, y=260, height=40)
#         self.entry_password.place(x=607, y=340, height=40)
#         self.button_log = tk.Button(self, width=40, cursor="hand2", text="LOG IN",
#                                     bg="#7B96D4", fg='floral white', command=lambda: control.logIn(self))
#         self.button_log.place(x=607, y=410, height=40)
#         self.notice.place(x=670, y=380)


class Home_Server(tk.Frame):
    def __init__(self, parent, control):
        tk.Frame.__init__(self, parent)

        self.img = Image.open("image/home_server.png")
        self.render = ImageTk.PhotoImage(self.img)

        canvas = Canvas(self, width=self.img.size[0], height=self.img.size[1])
        canvas.create_image(0, 0, anchor=NW, image=self.render)
        canvas.place(x=0, y=0)

        self.data = tk.Listbox(self, height=15, width=40, bg='floral white',
                               activestyle='dotbox', font="Helvetica", fg='#20639b')
        self.data.place(x=30, y=120)
        self.button_log = tk.Button(self, width=15, cursor="hand2", text="REFRESH",
                                    bg="#20639b", fg='floral white', command=self.Update_Client)
        # self.button_back = tk.Button(self, width=15, cursor="hand2", text="LOG OUT", bg="#20639b",
        #                              fg='floral white', command=lambda: control.showFrame(Background_Server))
        self.button_log.place(x=90, y=430)
        self.button_back.place(x=300, y=430)

    def Update_Client(self):
        self.data.delete(0, len(LiveAccount))
        for i in range(len(LiveAccount)):
            self.data.insert(i, LiveAccount[i])


# def checkTimeUpdate():
#     schedule.every(5).seconds.do(updateData)

#     while True:
#         schedule.run_pending()
#         time.sleep(1)


# sThreadUpdate = threading.Thread(target=checkTimeUpdate)
# sThreadUpdate.daemon = True
# sThreadUpdate.start()

# sThread = threading.Thread(target=startServer)
# sThread.daemon = True
# sThread.start()

db = Database(DATABASE_FILENAME["user"], DATABASE_FILENAME["covid"])
app = ServerApp()

def __main__():
    app.gui.mainloop()


if __name__ == '__main__':
    __main__()
