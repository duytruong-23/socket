import socket
import pickle
import datetime
from threading import Thread
import tkinter
from tkinter import PhotoImage, StringVar, Text, ttk
from tkinter.constants import CENTER, LEFT
PORT = 65432
FORMAT = "utf8"

LOGIN = "Log in"
SIGNUP = "Sign up"
TRUE = "True"
FALSE = "False"
POINTLESS_MESSAGE = "Socket"
YES = "Yes"
NO = "No"

def checkSyntax(s):
    if (s == ""): 
        return FALSE
    for i in s:
        if ('0' <= i <= '9' or 'A' <= i <='Z' or 'a' <= i <='z'):
            continue
        else:
            return FALSE
    return TRUE

def connect(host,port):
    try:
        ServerAddress = (host, int(port))
        print("connect")
        ClientSocket.connect(ServerAddress)
        show_frame(frame_login)  
        # QuitThread.start()  
    except:
        connect_msg.set("Failed to connect to server")

def sendAccount(option, username, password):
    try:
        if (checkSyntax(username) == FALSE or checkSyntax(password) == FALSE):
            if(option == LOGIN):
                error_msg.set("Invalid syntax!!! Username or password must not contain special character")
            if(option == SIGNUP):
                notification_msg_register.set("Invalid syntax!!! Username or password must not contain special character")
                label_notification_register["fg"] = "red"
            return
        if (option == SIGNUP and confirm_register.get() != password_register.get()):
            notification_msg_register.set("Please check your password again")
            label_notification_register["fg"] = "red"
            return
        # Gui qua cho server biet la dang gui thong tin dang nhap hay dang ky
        ClientSocket.sendall(bytes(option, FORMAT))
        ClientSocket.recv(1024).decode(FORMAT)
        account = {"username": username, "password": password}
        # Gui tai khoan qua server
        ClientSocket.sendall(pickle.dumps(account))
        # Nhan lai thanh cong hoac that bai
        flag = ClientSocket.recv(1024).decode(FORMAT)
        # Neu dang nhap thanh cong thi cho qua trang tim kiem
        if (option == LOGIN and flag == TRUE): 
            show_frame(frame_search)
            window.geometry("1000x500")
            sendDate(dateValue.get())
            comboBox2.current(0)

        # Neu dang ky thanh cong thi thong bao qua msg
        if (option == SIGNUP and flag == TRUE):
            label_notification_register["fg"] = "green"
            notification_msg_register.set("Account create successfully")

        # Neu dang nhap, dang ky that bai thi thong bao qua msg
        if (option == LOGIN and flag == FALSE):
            error_msg.set("Wrong password or username !!! Please try again")
            
        if (option == SIGNUP and flag == FALSE):
            notification_msg_register.set("Your username is taken please try another one")
            label_notification_register["fg"] = "red"


        print("send")
    except:
        show_frame(frame_error)
        window.geometry("800x600")

def getListDate():
    ListDate = []
    for i in range(30):
        date = datetime.date.today() - datetime.timedelta(i)
        ListDate.append("{}-{}-{}".format(date.day,date.month,date.year))
    return ListDate

def sendDate(dateStr):
    try:
        listDate = dateStr.split("-")
        date = {"day": listDate[0], "month": listDate[1], "year": listDate[2]}
        ClientSocket.sendall(pickle.dumps(date))
        global Data
        Data = pickle.loads(ClientSocket.recv(20480)) #20KB
        goldType = []
        clear_tree(table)
        for i in range(len(Data["type"])):
            goldType.append(Data["type"][i])
            table.insert(parent="", index='end', iid=i, text="parent", values=(Data["type"][i], Data["buy"][i], Data["sell"][i]))
        comboBox2["value"] = goldType
    except:
        show_frame(frame_error)
        window.geometry("800x600")


def getGoldPrice(index, type, date):
    global Data
    resultSell["text"] = Data["sell"][index]
    resultBuy["text"] = Data["buy"][index]
    typeLabel["text"] = type
    dateLabel["text"] = date




# GUI--------------------------------------------------------------------------------------------------
# INITIAL KHOI TAO UI
window = tkinter.Tk()
window.geometry('600x600')
window.title("Vietnam Gold Price")
window.columnconfigure(0,weight=1)
window.rowconfigure(0,weight=1)
style = ttk.Style(window)
style.configure('padded.TEntry', padding=[5, 3, 5, 3], foreground='#778289', font=('Roboto', 10))

s = ttk.Style()
s.configure('Treeview', rowheight=30)


frame_login = tkinter.Frame(window, background='#ffffff')
frame_register = tkinter.Frame(window,background='#ffffff')
frame_search = tkinter.Frame(window, background='#ffffff')
frame_connect = tkinter.Frame(window, bg='#ffffff')
frame_error = tkinter.Frame(window,bg ="red")
def show_frame(frame):
    frame.tkraise()

def clear_holder(stringVar,entry, msg, entryType = "password"):
    stringVar.set("")
    clear_msg(msg)
    entry.unbind('<FocusIn>')
    entry.bind('<FocusIn>',lambda event:clear_msg(msg))
    if (entryType == "password"):
        entry.config(show="*")

def clear_msg(msg):
    msg.set("")

def hide_password(entry_password):
    entry_password.configure(show="*")

def on_close():
    ClientSocket.close()
    window.quit()

def clear_tree(tree):
   for item in tree.get_children():
      tree.delete(item)


window.protocol("WM_DELETE_WINDOW", on_close)

for frame in (frame_login, frame_register, frame_search, frame_connect,frame_error):
    frame.grid(row=0, column= 0, sticky='nsew')
show_frame(frame_connect)

# -------------------------------------------------------------------------------------------------
#                                          CODE Connect to server
    # headding
frame1_connect = tkinter.Frame(frame_connect, bg="#ffffff")
frame1_connect.pack(pady=60, padx=80, fill='both')

    # Input
label_connect = tkinter.Label(frame1_connect, text="Connect to server", font=('Roboto',20, 'bold'), bg='#ffffff')
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

    #Button connect   1/Connect Client to server with host and port in the entry. Show Fail msg
btn_connect = tkinter.Button(frame1_connect,text="CONNECT",font=('Roboto', 12, "bold"), background="#000000", fg='#ffffff', command=lambda:connect(host.get(), port.get()))
btn_connect.pack(ipadx=20, fill='x')


# -----------------------------------------------------------------------------------------------------------
#                                                   CODE LOGIN
frame1_login = tkinter.Frame(frame_login, bg="#ffffff")
frame1_login.pack(pady=60, padx=80, fill='both')
    # Heading
label_login = tkinter.Label(frame1_login, text="WELCOME", font=('Roboto',20, 'bold'), bg='#ffffff', anchor='w')
label_login.pack(fill= 'both')
label1_login = tkinter.Label(frame1_login, text="Welcome to Vietnam Gold Price Application", font=('Roboto',10), bg='#ffffff', anchor='w', fg= "#CD9900")
label1_login.pack(fill= 'both', pady=(0,10))
label2_login = tkinter.Label(frame1_login, text="LOG IN", font=('Roboto',20, 'bold'), bg='#ffffff')
label2_login.pack(fill = 'both')

    # Input Username
label_username_login = tkinter.Label(frame1_login, text='Username', bg="#ffffff", font=('Roboto',10), fg="#000000", anchor='w')
label_username_login.pack(fill="both")
username = tkinter.StringVar()
entry_username_login = ttk.Entry(frame1_login,textvariable=username, style='padded.TEntry')
entry_username_login.insert(0, "Enter your username")
entry_username_login.pack(fill='both', pady=5, ipady=3)
entry_username_login.bind('<FocusIn>', lambda event:clear_holder(username, entry_username_login, error_msg, "username"))
    # Input password
label_password_login = tkinter.Label(frame1_login, text='Password', bg="#ffffff", font=('Roboto',10), fg="#000000", anchor='w')
label_password_login.pack(fill="both")
password = tkinter.StringVar()
entry_password_login = ttk.Entry(frame1_login,textvariable=password, style='padded.TEntry')
entry_password_login.insert(0, "Enter your password")
entry_password_login.pack(fill='both', pady=5, ipady=3)
entry_password_login.bind('<FocusIn>', lambda event:clear_holder(password, entry_password_login, error_msg))

    # Notification: Username used or wrong password, Please try again
error_msg = tkinter.StringVar()
label_notification_login = tkinter.Label(frame1_login, textvariable=error_msg, font=("Roboto, 10"), bg="#ffffff", fg="#E15139", anchor='w')

label_notification_login.pack(fill="both")
    # Button  send data to server
btn_login = tkinter.Button(frame1_login,text="LOGIN",font=('Roboto', 12, "bold"), background="#000000", fg='#ffffff', command=lambda:sendAccount(LOGIN, username.get(), password.get()))
btn_login.pack(ipadx=20, fill='x')
label3_login = tkinter.Label(frame1_login, text="Do not have an account yet ?", font=('Roboto',10, 'bold'), bg='#ffffff', anchor='w')
label3_login.pack(fill = 'both', side= LEFT, pady=(20,0))

    # Button toggle Option from login to sign up
btn_register_login = tkinter.Button(frame1_login, text="SIGN UP", background="#272935", fg='#ffffff', command=lambda:show_frame(frame_register))

btn_register_login.pack(side= LEFT, pady=(20,0))
# ------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
#                                                   CODE REGISTER
frame1_register = tkinter.Frame(frame_register, bg="#ffffff")
frame1_register.pack(pady=60, padx=80, fill='both')

label2_register = tkinter.Label(frame1_register, text="REGISTER", font=('Roboto',20, 'bold'), bg='#ffffff')
label2_register.pack(fill = 'both')

    # Input Username
label_username_register = tkinter.Label(frame1_register, text='Username', bg="#ffffff", font=('Roboto',10), fg="#000000", anchor='w')
label_username_register.pack(fill="both")
username_register = tkinter.StringVar()
entry_username_register = ttk.Entry(frame1_register,textvariable=username_register, style='padded.TEntry')
entry_username_register.insert(0, "Enter your username")
entry_username_register.pack(fill='both', pady=5, ipady=3)
entry_username_register.bind('<FocusIn>', lambda event:clear_holder(username_register, entry_username_register,notification_msg_register, "username"))
    # Input password
label_password_register = tkinter.Label(frame1_register, text='Password', bg="#ffffff", font=('Roboto',10), fg="#000000", anchor='w')
label_password_register.pack(fill="both")
password_register = tkinter.StringVar()
entry_password_register = ttk.Entry(frame1_register,textvariable=password_register, style='padded.TEntry')
entry_password_register.insert(0, "Enter your password")
entry_password_register.pack(fill='both', pady=5, ipady=3)
entry_password_register.bind('<FocusIn>', lambda event:clear_holder(password_register, entry_password_register,notification_msg_register))

    #Comfirm Password
label_confirm_register = tkinter.Label(frame1_register, text='Confirm Password', bg="#ffffff", font=('Roboto',10), fg="#000000", anchor='w')
label_confirm_register.pack(fill="both")
confirm_register = tkinter.StringVar()
entry_confirm_register = ttk.Entry(frame1_register,textvariable=confirm_register, style='padded.TEntry')
entry_confirm_register.insert(0, "Enter your password")
entry_confirm_register.pack(fill='both', pady=5, ipady=3)
entry_confirm_register.bind('<FocusIn>', lambda event:clear_holder(confirm_register, entry_confirm_register,notification_msg_register))


    # Error message
notification_msg_register = tkinter.StringVar()
label_notification_register = tkinter.Label(frame1_register, textvariable=notification_msg_register, font=("Roboto, 10"), bg="#ffffff", fg="#E15139", anchor='w')
label_notification_register.pack(fill="both")
    #Success message

    # Button send account to server
btn_register = tkinter.Button(frame1_register,text="REGISTER",font=('Roboto', 12, "bold"), background="#000000", fg='#ffffff', command=lambda:sendAccount(SIGNUP, username_register.get(), password_register.get()))
btn_register.pack(ipadx=20, fill='x')

label3_register = tkinter.Label(frame1_register, text="Already have an account ?", font=('Roboto',10, 'bold'), bg='#ffffff', anchor='w')
label3_register.pack(fill = 'both', side= LEFT, pady=(20,0))

    # Button toggle option 
btn_register_login = tkinter.Button(frame1_register, text="LOG IN", background="#272935", fg='#ffffff', command=lambda:show_frame(frame_login))
btn_register_login.pack(side= LEFT, pady=(20,0))

# CODE search
frame_search.grid_rowconfigure(0,weight=1)
frame_search.grid_columnconfigure(1,weight=1)
dateValue = tkinter.StringVar()

# -------------------------------Bảng
frame1_search = tkinter.Frame(frame_search, background="white")
frame1_search.grid(column=0, row=0, sticky='nsew')
table = ttk.Treeview(frame1_search)
table['columns'] = ("Brand", "Sell", "Buy")
tableLabel1 = tkinter.Label(frame1_search, text="Bảng giá vàng", background="white", font=20, fg="black")
tableLabel1.pack(anchor='n', pady=(30, 0))
tableLabel = tkinter.Label(frame1_search, textvariable=dateValue, background="white", font=20, fg="black")
tableLabel.pack(anchor='n')
# Table setup
table.column("#0", anchor='w', width=0, stretch=NO)
table.column("Brand", anchor='w', width=220)
table.column("Sell", anchor=CENTER, width=120)
table.column("Buy", anchor=CENTER, width=120)

# create heading
table.heading("#0", text="Parent", anchor="w")
table.heading("Brand", text="Brand", anchor="w")
table.heading("Sell", text='Sell', anchor=CENTER )
table.heading("Buy", text="Buy", anchor=CENTER)

table.pack(pady=20, padx=20, anchor='n')


# ------------------------------Filter
frame2_search = tkinter.Frame(frame_search, background="white")
frame2_search.grid(column=1, row=0, sticky='nsew')

heading_search = tkinter.Label(frame2_search, text="ENTER DETAIL HERE", bg="white", fg="black", font=("Roboto", 28,"bold"))
heading_search.pack(pady=(40,10))
# Bộ lọc
frameFilter_search = tkinter.Frame(frame2_search,background="white")
frameFilter_search.pack()
searchBtn = tkinter.Button(frame2_search, text="SEARCH", bg="white", fg="black", font=("Roboto", 12, "bold"), command=lambda:getGoldPrice(comboBox2.current(),typeValue.get(), dateValue.get()))
searchBtn.pack(ipady=3,ipadx=4,pady=20)
typeLabel = tkinter.Label(frame2_search, bg="white", fg="black", font=("Roboto", 15,"bold"))
typeLabel.pack()

dateLabel = tkinter.Label(frame2_search, bg="white", fg="black", font=("Roboto", 15,"bold"))
dateLabel.pack()


labelCombo1 = tkinter.Label(frameFilter_search, text="Date: ", bg="white", font=("Roboto", 12), fg="black")
labelCombo1.grid(row=0,column=0,sticky='w')

comboBox1 = ttk.Combobox(frameFilter_search, state="readonly", textvariable=dateValue)
comboBox1["value"] = getListDate()
comboBox1.bind("<<ComboboxSelected>>", lambda event: sendDate(dateValue.get()))
comboBox1.current(0)
comboBox1.grid(row=1, column=0, padx=(0,100), ipady=4)

labelCombo2 = tkinter.Label(frameFilter_search, text="Brand: ", bg="white", font=("Roboto", 12), fg="black")
labelCombo2.grid(row=0,column=1,sticky='w')
typeValue = tkinter.StringVar()
comboBox2 = ttk.Combobox(frameFilter_search, state="readonly", textvariable=typeValue)
comboBox2.grid(row=1, column=1, ipadx=20, ipady=4)

# Hiển thị kết quả
frameResult_search = tkinter.Frame(frame2_search,background="white")
frameResult_search.pack()
sellLabel = tkinter.Label(frameResult_search, text="Sell: ", bg="white", font=("Roboto", 12,"bold"), fg="black")
sellLabel.grid(row=0,column=0, sticky='w')
buyLabel = tkinter.Label(frameResult_search, text="Buy: ", bg="white", font=("Roboto", 12,"bold"), fg="black")
buyLabel.grid(row=0,column=1,sticky='w')
resultSell = tkinter.Label(frameResult_search,text="                   ", bg="black", font=("Roboto", 12,"bold"), fg="white")
resultSell.grid(row=1,column=0,padx=(0,100), ipadx=20, ipady=3, pady=10)
resultBuy = tkinter.Label(frameResult_search,text="                   ", bg="black", font=("Roboto", 12, "bold"), fg="white")
resultBuy.grid(row=1,column=1, ipadx=20, ipady=3, pady=10)

unitLabel = tkinter.Label(frame2_search, text="ĐVT: 1000Đ", font=("bold",14), background="white", foreground="black")
unitLabel.pack(pady=20)
Data = []

# -----------------------------------------ERROR FRAME--------------------------------------------
bg1 = PhotoImage(file = "error.png")
# window.geometry("800x600")
canvas2 = tkinter.Canvas(frame_error, width=800, height=600)
canvas2.pack(fill='both', expand= True)
canvas2.create_image(0,0,image = bg1, anchor = "nw")

if __name__ == "__main__":
    # MAIN_THREAD = Thread(target=main)
    # MAIN_THREAD.start()
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tkinter.mainloop()
    



