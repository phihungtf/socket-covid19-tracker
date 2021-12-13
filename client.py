import json
import socket
import threading
import os

import tkinter as tk 
from tkinter import ttk
import tkinter.font
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 55555
MAX_BYTES = 1024
FORMAT = "utf-8"
ADDR = (HOST, PORT)
DISCONNECT_MESSAGE = "Disconnect"

SIGNUP = "SIGNUP"
LOGIN = "LOGIN"
LOGOUT = "LOGOUT"
SEARCH = "SEARCH"

FONT = ("Tahoma", 13)
FONT_BOLD = ("Tahoma", 13, "bold")

#GLOBAL socket initialize
def messageCreate(type, payload):
    return json.dumps({"type": type, "payload": payload}).encode(FORMAT)

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
    def __init__(self, master, signUpCommand):
        self.isConnected = False
        self.frame = tk.Frame(master)
        # self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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

        tk.Label(self.frame, text="Don't have an account?", font=("Tahoma", 10)).place(x=45, y=315)
        self.signUpButton = LinkLabel(self.frame, text="Sign Up!", fg="blue", font=("Tahoma", 10), command=signUpCommand)
        self.signUpButton.place(x=185, y=315)

        # self.disableLogIn()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.disableConnect()
        self.enableLogIn()
        self.isConnected = True
        self.socket.connect((self.ip.get(), self.port.get()))
        print(self.socket)

    def disconnect(self):
        self.isConnected = False
        self.enableConnect()
        self.disableLogIn()
        self.socket.close()

    def logIn(self):
        username = self.usernameEntry.get()
        password = self.passwordEntry.get()
        if username == "" or password == "":
            messagebox.showerror("Error", "Username or password is empty!")
            return

        self.socket.send(messageCreate(LOGIN, {"username": username, "password": password}))
        response = self.socket.recv(MAX_BYTES).decode(FORMAT)
        messagebox.showinfo("Response", response)

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
    def __init__(self, master, logInCommand):
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

        self.signUpButton = tk.Button(self.frame, text="Sign Up", font=FONT, relief="ridge")
        self.signUpButton.place(x=12, y=240, width=270)

        tk.Label(self.frame, text="Already have an account?", font=("Tahoma", 10)).place(x=35, y=295)
        self.logInButton = LinkLabel(self.frame, text="Log In!", fg="blue", font=("Tahoma", 10), command=logInCommand)
        self.logInButton.place(x=195, y=295)

    def signUp(self):
        pass

class ClientApp(tk.Tk):
    def __init__(self):
        self.gui = tk.Tk()
        self.gui.geometry('300x350')
        self.gui.title('Covid-19 Tracker Server')
        self.gui.resizable(width=False, height=False)
        self.gui.option_add("*Font", FONT)

        self.frames = {
            SIGNUP: SignUpFrame(self.gui, lambda: self.showFrame(LOGIN)),
            LOGIN: LogInFrame(self.gui, lambda: self.showFrame(SIGNUP))
        }

        self.currentFrame = LOGIN
        self.showFrame(self.currentFrame)

    def showFrame(self, frame):
        self.frames[self.currentFrame].frame.pack_forget()
        self.currentFrame = frame
        self.frames[self.currentFrame].frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # if self.currentFrame == LOGIN:
        #     self.gui.geometry("300x280")
        # elif self.currentFrame == SIGNUP:
        #     self.gui.geometry("300x340")
        
    def logIn(self,curFrame,client):
        try:
            username = curFrame.entry_username.get()
            password = curFrame.entry_password.get()

            if username == '' or password == '':
                curFrame.notice = "username and password cannot be empty"
            
            msg = LOGIN
            client.sendall(msg.encode(FORMAT))

            client.sendall(username.encode(FORMAT))
            client.recv(HEADER)

            client.sendall(password.encode(FORMAT))

            self.user = username

            accepted = client.recv(HEADER).decode(FORMAT)
            if accepted == "1":
                self.showFrame(Home_Client)
                curFrame.notice["text"] = ""

            elif accepted == "2":
                curFrame.notice["text"] = "Invalid username or password"
            elif accepted == "0":
                curFrame.notice["text"] = "User already logged in"

        except:
            print("Error: Server is not responding")   


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

    def signUp(self, client, curFrame):
        try:

            username = curFrame.entry_username.get()
            password = curFrame.entry_password.get()

            msg = SIGNUP
            client.sendall(msg.encode(FORMAT))

            client.sendall(username.encode(FORMAT))
            client.recv(HEADER)

            client.sendall(password.encode(FORMAT))

            accepted = client.recv(HEADER).decode(FORMAT)
            if accepted == "True":
                self.showFrame(Background_Client)
                curFrame.notice["text"] = "Sign up success"
            else:
                curFrame.notice["text"] = "Username already exists"
            
        except:
            print("Error: Server is not responding") 

    def logOut(self, client, preFrame):
        try:
            username = preFrame.user
            msg = LOGOUT
            client.sendall(msg.encode(FORMAT))
            client.sendall(username.encode(FORMAT))
            accepted = client.recv(HEADER).decode(FORMAT)
            if accepted == "True":
                self.showFrame(Background_Client)
        except:
            print("Error: Server is not responding")  
    

class Background_Client(tk.Frame):
    def __init__(self, parent, control):
        tk.Frame.__init__(self, parent)

        self.img = Image.open("image/login_client.png")
        self.render = ImageTk.PhotoImage(self.img)
    
        canvas = Canvas(self, width=self.img.size[0], height=self.img.size[1])
        canvas.create_image(0, 0, anchor=NW, image=self.render)
        canvas.pack(fill=BOTH, expand=1)

        self.notice = tk.Label(self,text="",bg="#6184D6",fg='red')
        self.entry_username = tk.Entry(self,width=40,bg='white')
        self.entry_password = tk.Entry(self,width=40,bg='white', show="*")
        self.entry_username.place(x = 607, y = 260, height=40)
        self.entry_password.place(x = 607, y = 340, height=40)
        self.button_log = tk.Button(self,width = 10,cursor="hand2" ,text="LOG IN",bg="#7B96D4",fg='floral white',command=lambda: control.logIn(self, client))
        self.button_sign = tk.Button(self,width = 10,cursor="hand2" ,text="SIGN UP",bg="#7B96D4",fg='floral white',command=lambda: control.signUp(self, client))
        self.button_log.place(x = 607, y = 410, height=40)
        self.button_sign.place(x = 810, y = 410, height=40)
        self.notice.place(x = 670, y = 380)


class Home_Client(tk.Frame):
    def __init__(self, parent, control):
        tk.Frame.__init__(self, parent)
        
        self.img = Image.open("image/home_client.png")
        self.render = ImageTk.PhotoImage(self.img)
    
        canvas = Canvas(self, width=self.img.size[0], height=self.img.size[1])
        canvas.create_image(0, 0, anchor=NW, image=self.render)
        canvas.place(x = 0, y = 0)
        
        
        self.button_back = tk.Button(self,width= 15,cursor="hand2", text="LOG OUT",bg="#20639b",fg='floral white' ,command=lambda: control.logOut(client, control))
        self.button_back.place(x = 400, y = 10)  

        self.entry_search = tk.Entry(self,width = 30, bg = 'white')
        self.button_search = tk.Button(self,width=10,cursor="hand2", text="SEARCH",bg="#7B96D4",fg='floral white',command=lambda: self.Search())
        self.entry_search.place(x = 20, y = 180, height= 30)
        self.button_search.place(x = 250, y =180)

        self.data = tk.Listbox(self, height = 10, width = 40, bg='floral white',activestyle = 'dotbox', font = "Helvetica", fg='#20639b')
        self.data.place(x = 70, y = 230)

    def Search(self):
        try:
            msg = SEARCH
            client.sendall(msg.encode(FORMAT))
            country = self.entry_search.get()
            client.sendall(country.encode(FORMAT))

            info = client.recv(HEADER).decode(FORMAT)
            show = info.split("\n")
            self.data.delete(0,len(show))
            
            for i in range(len(show)):
                self.data.insert(i,show[i])

        except:
            print("Error: Server is not responding")    

def __main__():
  app = ClientApp()
  app.gui.mainloop()

if __name__ == '__main__':
  __main__()


