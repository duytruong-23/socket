import socket
import threading
from threading import Thread
import pickle
import json
import requests
from tkinter import *
import tkinter
from tkinter import ttk
import datetime
import time

FORMAT = "utf8"
HOST = "127.0.0.1"
PORT = 65432
URL = 'https://tygia.com/json.php?ran=0&rate=0&gold=1&bank=VIETCOM&date'

LOGIN = "Log in"
SIGNUP = "Sign up"
TRUE = "True"
FALSE = "False"
POINTLESS_MESSAGE = "Socket"

def getListAccounts():
    ListAccounts = {}
    ListAccounts["username"] = []
    ListAccounts["password"] = []
    try:
        with open("Account.json", "r") as file:
            ListAccounts = json.load(file)
    except:
        ListAccounts["username"].append("admin")
        ListAccounts["password"].append("1234")
        with open("Account.json", "w") as file:
            json.dump(ListAccounts, file, indent = 4)
    return ListAccounts

def updateListAccounts(ListAccounts):
    with open("Account.json", "w") as file:
        json.dump(ListAccounts, file, indent = 4)

def insertNewAccount(ListAccounts, username, password):
    ListAccounts["username"].append(str(username))
    ListAccounts["password"].append(str(password))
    


def checkValidLogIn(ListAccounts, username, password):
    for i in range(len(ListAccounts["username"])):
        if ListAccounts["username"][i] == username and ListAccounts["password"][i] == password:
            return TRUE
    return FALSE


def checkValidSignUp(ListAccounts, username, password):
    for i in range(len(ListAccounts["username"])):
        if ListAccounts["username"][i] == username:
            return FALSE
    return TRUE


def clientSignUp(ListAccounts, username, password):

    if checkValidSignUp(ListAccounts, username, password) == TRUE:
        insertNewAccount(ListAccounts, username, password)
        return TRUE
    else:
        return FALSE


def clientLogIn(ListAccounts, username, password):

    if checkValidLogIn(ListAccounts, username, password) == TRUE:
        return TRUE
    else:
        return FALSE

def encodeDate(day, month, year):
    date = str(year) + str(month) + str(day)
    return date

def getPriceGold(day, month, year):
    list = {}
    list["buy"] = []
    list["sell"] = []
    list["type"] = []
    try:
        date = encodeDate(day, month, year)
        url = URL + "=" + date
        response = requests.get(url)
        response.encoding = 'utf-8-sig'
        content = response.text.encode().decode('utf-8-sig')
        Data = json.loads(content)
        object1 = Data["golds"]
        object2 = object1[0]
        object3 = object2['value']
        j = 0
        for i in object3:
            list["buy"].append(i["buy"])
            list["sell"].append(i["sell"])
            list["type"].append(i["type"] + " " + i["brand"])
            j += 1
            if (j == 65):
                break
    except:
        list["buy"].append("0.00")
        list["sell"].append("0.00")
        list["type"].append("NONE")
    return list

#luu gia vang 7 ngay gan nhat vao file json
def storePriceGold():
    for i in range(7):
        date = datetime.date.today() - datetime.timedelta(i)
        filename = ("{}-{}-{}.json".format(date.day,date.month,date.year))
        data = getPriceGold(date.day, date.month, date.year)
        with open(filename, "w") as file:
            json.dump(data, file, indent = 4)

def controlLoginSignUp(connector,addr):
    date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    flag = FALSE
    # Nhan thong tin dang dang nhap hay dang ky
    option = connector.recv(1024).decode(FORMAT)
    connector.sendall(bytes(POINTLESS_MESSAGE, FORMAT))
    # Nhan account
    AccountClient = pickle.loads(connector.recv(1024))
    # Check account
    ListAccounts = getListAccounts()
    if option == LOGIN:
        flag = clientLogIn(ListAccounts, AccountClient["username"], AccountClient["password"])
    elif option == SIGNUP:
        flag = clientSignUp(ListAccounts, AccountClient["username"], AccountClient["password"])
    # Gui lai server thanh cong hoac that bai
    connector.sendall(bytes(flag, FORMAT))
    if (option == LOGIN and flag == TRUE):
        msg_list.insert(tkinter.END, f"{date}: {str(addr)} has logged in successfully with username: '{AccountClient['username']}'")
    # dky thanh cong thi cap nhat lai database
    if (option == LOGIN and flag == FALSE):
        msg_list.insert(tkinter.END, f"{date}: {str(addr)} has failed to login an account with username: '{AccountClient['username']}'")
    if (option == SIGNUP and flag == FALSE):
        msg_list.insert(tkinter.END, f"{date}: {str(addr)} has failed to create an account with username: '{AccountClient['username']}'")
    if (option == SIGNUP and flag == TRUE): 
        updateListAccounts(ListAccounts)
        msg_list.insert(tkinter.END, f"{date}: {str(addr)} has created an account successfully with username: '{AccountClient['username']}'")
        #Chi cho Flag = true khi nguoi dung dang nhap thanh cong
        flag = FALSE
    print(option)
    print(AccountClient["username"])
    print(AccountClient["password"])
    return flag

def controlSearchGold(connector):
    #nhan ngay tu client
    date = pickle.loads(connector.recv(1024))
    Data = {}
    Data["buy"] = []
    Data["sell"] = []
    Data["type"] = []
    try:
        filename = ("{}-{}-{}.json".format(date["day"], date["month"], date["year"]))
        with open(filename, "r") as file:
            Data = json.load(file)
    except FileNotFoundError:
        today = datetime.date.today()
        if filename == ("{}-{}-{}.json".format(today.day, today.month, today.year)):
            Data = getPriceGoldToDay()
        else:
            Data["buy"].append("0.00")
            Data["sell"].append("0.00")
            Data["type"].append("NONE")
    #gui thong tin gia vang ngay client muon tra cuu
    connector.sendall(pickle.dumps(Data))
    print(date)
    return FALSE

#Lay gia vang hom nay va cache lai vao file json
def getPriceGoldToDay():
    Data = {}
    Data["buy"] = []
    Data["sell"] = []
    Data["type"] = []
    today = datetime.date.today()
    filename = ("{}-{}-{}.json".format(today.day, today.month, today.year))
    Data = getPriceGold(today.day, today.month, today.year)
    with open(filename, "w") as file:
        json.dump(Data, file, indent = 4)
    return Data

#cap nhat gia vang hom nay
def updatePriceGold():
    flag = TRUE
    Data = {}
    Data["buy"] = []
    Data["sell"] = []
    Data["type"] = []
    today = datetime.date.today()
    filename = ("{}-{}-{}.json".format(today.day, today.month, today.year))
    #kiem tra co file cua ngay hom nay hay khong
    try:
        with open(filename, "r") as file:
            Data = json.load(file)
    except FileNotFoundError:
        flag = FALSE
    #neu co file cua ngay hom nay thi moi cap nhat
    if flag == TRUE:
        getPriceGoldToDay()

def updateEvery30Minutes():
    while True:
        updatePriceGold()
        print("Gold price today has been updated.")
        time.sleep(1800)

def acceptConnection():
    date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    try:
        while True:
            connector, address = ServerSocket.accept()
            print("%s has connected!" % str(address))
            msg_list.insert(tkinter.END, f"{date}: {str(address)} has connected" )

            threading.Thread(target=handlerClient, args=(connector, address, ), daemon = True).start()
    except:
        print("Server is shutting down")
    finally:
        ServerSocket.close()
        
def handlerClient(connector,addr):
    try:
        flag = FALSE
        # Step LogIn
        while (flag == FALSE):
            flag = controlLoginSignUp(connector,addr)
        # Step Search for Gold Infomation
        flag = FALSE
        while(flag == FALSE):
            flag = controlSearchGold(connector)
    except:
        date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        connector.close()
        print("Client disconnected: " + str(addr))
        msg_list.insert(tkinter.END, f"{date}: {str(addr)} has disconnected")

def startServer(host,port):
    ServerSocket.bind((host, int(port)))
    try:
        ServerSocket.listen(1)
        print("Socket is successfully created!")
        msg_list.insert(tkinter.END, f"Server start at: {str(host)}:{str(port)}")
        msg_list.insert(tkinter.END,f"Server is waiting for connection")
    except:
        print("ERROR: CREATING SOCKET IS FAILED!")
        ServerSocket.close()
        input("Press any key to quit....")
        return
    storePriceGold()
    UPDATE_THREAD = Thread(target=updateEvery30Minutes, daemon=True)
    UPDATE_THREAD.start()
    print("%s: Waiting for client....." % HOST)
    ACCEPT_THREAD = Thread(target=acceptConnection)
    ACCEPT_THREAD.start()


# -------------------------------------GUI----------------------------------
window = Tk()
window.title("Server Dialog")
window.columnconfigure(0,weight=1)
window.rowconfigure(0,weight=1)

frame_connect = tkinter.Frame(window, background="#ffffff")
frame_dialog = tkinter.Frame(window, background="#ffffff")

def show_frame(frame):
    frame.tkraise()

for frame in (frame_connect,frame_dialog):
    frame.grid(row=0, column= 0, sticky='nsew')
show_frame(frame_connect)



lbl = Label(frame_dialog, text="Dialog")
lbl.grid(column=0, row=0)
msg_list = tkinter.Listbox(frame_dialog,height=25, width=100)
msg_list.grid(column=0, row=1)
def on_close():
    ServerSocket.close()
    window.quit()

window.protocol("WM_DELETE_WINDOW", on_close)

def clear_msg(msg):
    msg.set("")

    # headding
frame1_connect = tkinter.Frame(frame_connect, bg="#ffffff")
frame1_connect.pack(pady=60, padx=80, fill='both')

    # Input
label_connect = tkinter.Label(frame1_connect, text="Start Server", font=('Roboto',20, 'bold'), bg='#ffffff')
label_connect.pack(fill= 'both')

label_host = tkinter.Label(frame1_connect, text='HOST: ', bg="#ffffff", font=('Roboto',10), fg="#000000", anchor='w')
label_host.pack(fill="both")
host = tkinter.StringVar()
entry_host = ttk.Entry(frame1_connect,textvariable=host)
entry_host.pack(fill = 'both',pady=5, ipady=3)
entry_host.bind('<FocusIn>',lambda event:clear_msg(connect_msg))
host.set("127.0.0.1")

label_port = tkinter.Label(frame1_connect, text='PORT: ', bg="#ffffff", font=('Roboto',10), fg="#000000", anchor='w')
label_port.pack(fill="both")
port = tkinter.StringVar()
entry_port = ttk.Entry(frame1_connect,textvariable=port)
entry_port.pack(fill = 'both',pady=5, ipady=3, expand=1)
port.set("65432")
entry_port.bind('<FocusIn>',lambda event:clear_msg(connect_msg))


    # message
connect_msg = tkinter.StringVar()
label_connect_msg = tkinter.Label(frame1_connect, textvariable=connect_msg, font=("Roboto, 10"), bg="#ffffff", fg="#E15139", anchor='w')
connect_msg.set("")
label_connect_msg.pack(fill='both')

    #Button start   1/Connect Client to server with host and port in the entry. Show Fail msg
btn_start = tkinter.Button(frame1_connect,text="START",font=('Roboto', 12, "bold"), background="#000000", fg='#ffffff',command=lambda:[show_frame(frame_dialog), startServer(host.get(),port.get())])
btn_start.pack(ipadx=20, fill='x')



# --------------------------------------------------------------------------------------

clients = {}
addresses = {}

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def main():
    tkinter.mainloop()

main()