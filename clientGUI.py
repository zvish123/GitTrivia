import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****
from tkinter import *


SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678

DISPLAY_MSG = False
last_command = ''
client_socket = None
userE = None    # user entry
user = ''       # user name
question_id = -1
answered = False

# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg, display=False):
    """
	Builds a new message using chatlib, wanted code and message. 
	Prints debug info, then sends it to the given socket.
	Paramaters: conn (socket object), code (str), msg (str)
	Returns: Nothing
    """
    global DISPLAY_MSG
    full_message = chatlib.build_message (code, msg)
    if display or DISPLAY_MSG:
        print(full_message)
    conn.send(bytes (full_message, 'utf-8'))


def recv_message_and_parse(conn, display=False):
    """
	Receives a new message from given socket.
	Prints debug info, then parses the message using chatlib.
	Paramaters: conn (socket object)
	Returns: cmd (str) and data (str) of the received message. 
	If error occured, will return None, None
	"""
    global  DISPLAY_MSG
    data = conn.recv (1024).decode ()
    if display or DISPLAY_MSG:
        print("Recieved: " + data)
    cmd, msg = chatlib.parse_message (data)
    return cmd, msg


def connect():
    # Implement Code
    my_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect ((SERVER_IP, SERVER_PORT))
    return my_socket


def error_and_exit(msg):
    # Implement code
    print (msg)
    exit (1)


def login(conn):
    cmd = 'ERROR'
    while cmd == 'ERROR':
        username = input ("Please enter username: \n")
        password = input ("Please enter password: \n")
        msg = username + chatlib.MSG_DELIMITER + password
        # Implement code
        cmd, msg = build_send_recv_parse (conn, chatlib.PROTOCOL_CLIENT["login_msg"], msg)
        if DISPLAY_MSG:
            print(cmd, msg)
        if cmd == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            print('You have logged in')
        else:
            print('Error in user or password')
        return cmd
    return cmd

def message(text):
    rootm = Tk()
    rootm.title("Notification")
    msgL = Label(rootm, text=text)
    msgL.grid(sticky=E)

    okbtn = Button(rootm, text='Ok', command=lambda : rootm.destroy())
    okbtn.grid(sticky=W)
    rootm.mainloop()


def updateUserEntry(username):
    global userE
    global user
    userE.configure(state='normal')
    userE.delete(0,"end")
    userE.insert(0, username)
    userE.configure(state='disabled')
    user = username

def updateUserScore(sock):
    global scoreE
    score = str(get_score(sock))
    scoreE.configure(state='normal')
    scoreE.delete(0,"end")
    scoreE.insert(0, score)
    scoreE.configure(state='disabled')

def check_login():
    global client_socket
    global unameE
    global passwordE
    global userE
    global user

    username = unameE.get()
    password = passwordE.get()
    #print(client_socket)
    if client_socket == None:
        client_socket = connect ()
    print(username, password)
    msg = username + chatlib.MSG_DELIMITER + password
    # Implement code
    cmd, msg = build_send_recv_parse (client_socket, chatlib.PROTOCOL_CLIENT["login_msg"], msg)

    if cmd == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
        print(f'{username}  You have logged in')
        login_check = True
        #userE.configure(text=username)
        updateUserEntry(username)
        updateUserScore(client_socket)
    else:
        print('Error in user or password')
        login_check = False
    roota.destroy()



def login():
    global client_socket
    global last_command
    global user
    global unameE
    global passwordE
    global roota
    print('user',user)
    if user != '':
        message("Logout before performing login")
    else:
        roota = Tk()
        roota.title("Login")
        instruct1 = Label(roota, text="Login\n")
        instruct1.grid(sticky=E)
        unameL = Label(roota, text='User name')
        passwordL = Label(roota, text='Password')
        unameL.grid(row=1, sticky=W)
        passwordL.grid(row=2, sticky=W)
        unameE = Entry(roota)
        passwordE = Entry(roota, show='*')
        unameE.grid(row=1, column=1)
        passwordE.grid(row=2, column=1)

        loginbtn = Button(roota, text='Login', command=check_login)
        loginbtn.grid(column=2, sticky=W)

        roota.mainloop()


def logout(conn):
    # Implement code
    build_and_send_message (conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")

def logout():
    global client_socket
    global user
    #print('logout', client_socket)
    if client_socket is not None:
        build_and_send_message (client_socket, chatlib.PROTOCOL_CLIENT["logout_msg"], "")
        user = ''
        updateUserEntry("")
        client_socket=None



#Targil 3
def build_send_recv_parse(conn, cmd, data, display=False):
    build_and_send_message (conn, cmd, data, display)
    cmd, msg = recv_message_and_parse(conn)
    return cmd, msg

def get_score(conn):

    cmd, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["my_score_msg"], '' )
    if cmd == chatlib.PROTOCOL_SERVER["your_score_msg"]:
        score = int(msg)
    else:
        print('Problem in getting score')
        score = -1
    return score

#Targil 4
def play_question(socket):
    question, question_id = get_question(socket)
    if question is None or question==-1:
        logout (socket)
        return  False
    else:
        print(question)

    answer = send_answer(socket, question_id)
    print(answer)
    return True

def updateButtonText(btn, text):
    btn.config(text=text, bg='gainsboro')   #gray


def play():
    global questionL
    global clickL
    global answerB1
    global answerB2
    global answerB3
    global answerB4
    global client_socket
    global question_id
    global answered
    question, question_id = get_question(client_socket)
    if question is None or question==-1:
        message("No more questions")
        return  False
    else:
        r = question.split('\n')
        updateButtonText(questionL, r[1])
        updateButtonText(answerB1, r[2])
        updateButtonText(answerB2, r[3])
        updateButtonText(answerB3, r[4])
        updateButtonText(answerB4, r[5])
        answered=False




def get_highscore(socket):
    cmd, msg = build_send_recv_parse(socket, chatlib.PROTOCOL_CLIENT["highscore_msg"], '' )
    if cmd == chatlib.PROTOCOL_SERVER["all_score_msg"]:
        score = msg.split('\n')[0]
    else:
        print('Problem in getting score')
        score = "Empty list"
    return score


def highScore():
    global client_socket
    highscore=0
    if client_socket != None:
        cmd, msg = build_send_recv_parse(client_socket, chatlib.PROTOCOL_CLIENT["highscore_msg"], '' )
        if cmd == chatlib.PROTOCOL_SERVER["all_score_msg"]:
            highscore = msg.split('\n')[0]
        rootm = Tk()
        rootm.title("High score")
        msgL = Label(rootm, text=str(highscore), font=("Courier", 30))
        msgL.grid(sticky=E)

        okbtn = Button(rootm, text='Ok', command=lambda : rootm.destroy())
        okbtn.grid(sticky=W)
        rootm.mainloop()

def get_logged_users(socket):
    cmd, msg = build_send_recv_parse(socket, chatlib.PROTOCOL_CLIENT["logged_users_msg"], '' )
    if cmd == chatlib.PROTOCOL_SERVER["logged_answer_msg"]:
        users = msg
    else:
        print('Problem in getting users')
        users = "Empty list"
    return users

def format_question(msg):
    list = chatlib.split_msg(msg, 6)
    result = f'Question: {list[0]}' + '\n'
    result += list[1] + '\n'
    for i in range(4):
        result += f'{i+1}. {list[i+2]}\n'
    return result, list[0]

def get_question(conn):
    #print('socket:', conn)
    cmd, msg = build_send_recv_parse (conn, chatlib.PROTOCOL_CLIENT["get_question_msg"], "", True)
    if cmd == chatlib.PROTOCOL_SERVER["your_question_msg"]:
        question, question_id = format_question(msg)
    elif cmd == chatlib.PROTOCOL_SERVER["no_questions_msg"]:
        print("No more questions")
        question = None
        question_id = -1
    else:
        print('Problem in getting question')
        question = -1
        question_id = -1
    return question, question_id

def send_answer(conn, question_id):
    answer = input("Enter your answer: ")
    msg = str(question_id)+chatlib.MSG_DELIMITER+answer
    cmd, msg = build_send_recv_parse (conn, chatlib.PROTOCOL_CLIENT["send_answer_msg"], msg, False)
    if cmd == chatlib.PROTOCOL_SERVER["correct_answer_msg"]:
        answer = "correct " + msg
    elif cmd == chatlib.PROTOCOL_SERVER["wrong_answer_msg"]:
        answer = "wrong\nCorrect answer: " + msg
    else:
        print('Problem in getting answer')
        answer = 'no answer'
    return answer


def updateButtonColor(btn, color):
    btn.config(bg=color)

def sendAnswer(answer):
    global question_id
    global client_socket
    global answerB1
    global answerB2
    global answerB3
    global answerB4
    global answered
    if question_id != -1 and not answered:
        answered=True
        msg = str(question_id)+chatlib.MSG_DELIMITER+str(answer)
        cmd, msg = build_send_recv_parse (client_socket, chatlib.PROTOCOL_CLIENT["send_answer_msg"], msg, False)
        correctBtn = None
        if cmd == chatlib.PROTOCOL_SERVER["correct_answer_msg"]:
            reply = "correct " + msg
            if answer==1:
                correctBtn = answerB1
            elif answer==2:
                correctBtn = answerB2
            elif answer==3:
                correctBtn = answerB3
            else:
                correctBtn = answerB4
            updateButtonColor(correctBtn, 'green')
            updateUserScore(client_socket)

        elif cmd == chatlib.PROTOCOL_SERVER["wrong_answer_msg"]:
            reply = "wrong\nCorrect answer: " + msg
            wrongBtn = None
            if answer==1:
                wrongBtn = answerB1
            elif answer==2:
                wrongBtn = answerB2
            elif answer==3:
                wrongBtn = answerB3
            elif answer==4:
                wrongBtn = answerB4
            if msg=="1":
                correctBtn = answerB1
            elif msg=="2":
                correctBtn = answerB2
            elif msg=="3":
                correctBtn = answerB3
            else:
                correctBtn = answerB4

            updateButtonColor(wrongBtn, 'red')
            updateButtonColor(correctBtn, 'green')
    else:
        print('Problem in getting answer')
        reply = 'no answer'
    print(reply)

def sendAnswer1():
    sendAnswer(1)
def sendAnswer2():
    sendAnswer(2)
def sendAnswer3():
    sendAnswer(3)
def sendAnswer4():
    sendAnswer(4)


def dict_to_str(dict):
    result = ""
    for item in dict.items():
        #print(item)
        result += str(item[0]) + ': ' + str(item[1]) + ' '
    return result


def main():
    # Implement code
    client_socket = connect ()

    dict = {0:'Login',1:'Get score', 2:'Get Question', 3:'Send Answer',4:'Get High score',5: 'Logged users',6:"Play Question", 8:'Logout', 9:'Exit'}
    menu_str = "Select menu option:\n " + dict_to_str(dict) + '\n'

    is_logged_in = False
    flag = True
    last_question_id = -1
    option = 0
    #"Select menu option: 0. login 1. Get Score  8. Logout 9.Exit"
    while flag:
        try:
            option = int(input(menu_str))
            if option==0:
                if not is_logged_in:
                    if client_socket == None:
                        client_socket = connect ()
                    cmd = login(client_socket)
                    is_logged_in = cmd==chatlib.PROTOCOL_SERVER["login_ok_msg"]
                else:
                    print("Log out before re-login")
            elif option==1:
                if is_logged_in:
                    print("Your score: " + str(get_score(client_socket)))
                else:
                    print("Log in in order to get score")
            elif option==2:
                if is_logged_in:
                    question, last_question_id =  get_question(client_socket)
                    if question is None or question==-1:
                        logout (client_socket)
                        is_logged_in = False
                        client_socket=None
                        flag=False
                    else:
                        print(question)
                else:
                    print("Log in in order to get question")
            elif option==3:
                if is_logged_in:
                    answer =  send_answer(client_socket, last_question_id)
                    print(answer)
                else:
                    print("Loging in order to get answer")
            elif option==4:
                if is_logged_in:
                    high_scores =  get_highscore(client_socket)
                    print(high_scores)
                else:
                    print("Loging in order to get high score")
            elif option==5:
                if is_logged_in:
                    users =  get_logged_users(client_socket)
                    print(users)
                else:
                    print("Loging in order to get logged users")
            elif option==6:
                if is_logged_in:
                    flag =  play_question(client_socket)
                    if flag==False:
                        is_logged_in = False
                        client_socket=None
                        flag=False

                else:
                    print("Loging in order to play question")
            elif option==8:
                if is_logged_in:
                    logout (client_socket)
                    is_logged_in = False
                    client_socket=None
                else:
                    print('You should be logged in in order to logout')
            elif option==9:
                if client_socket is not None:
                    logout (client_socket)
                    is_logged_in = False
                    client_socket=None
                flag=False
        except ValueError:
            print('Incorrect value')
    print("bye")

def goodBye(*args):
    logout()

def goodByeWindow():
    global root
    logout()
    root.destroy()

def mainGUI():
    global userE
    global scoreE
    global questionL
    global clickL
    global answerB1
    global answerB2
    global answerB3
    global answerB4
    global root
    root = Tk()
    root.geometry("600x300")
    root.title('Multi players Trivia')
    root.bind('<Destroy>', goodBye)
    l1 = Label(root, text="User")
    l1.grid(row=1, column=1, sticky='e' + 'w', padx=2, pady=2)
    userE = Entry(root, state='disabled')
    userE.grid(row=1, column=2, sticky='e' + 'w', padx=2, pady=2)
    l2 = Label(root, text="Score")
    l2.grid(row=1, column=3, sticky='e' + 'w', padx=2, pady=2)
    scoreE = Entry(root, state='disabled')
    scoreE.grid(row=1, column=4, sticky='e' + 'w', padx=2, pady=2)
    b1 = Button(root, text="Login", command=login)
    b1.grid(row=2, column=0, sticky='e' + 'w', padx=2, pady=2)
    b2 = Button(root, text="Play", command=play)
    b2.grid(row=3, column=0, sticky='e' + 'w', padx=2, pady=2)
    b3 = Button(root, text="High score", command=highScore)
    b3.grid(row=4, column=0, sticky='e' + 'w', padx=2, pady=2)
    b4 = Button(root, text="Logout", command=logout)
    b4.grid(row=5, column=0, sticky='e' + 'w', padx=2, pady=2)
    b5 = Button(root, text="Exit", command=goodByeWindow)
    b5.grid(row=6, column=0, sticky='e' + 'w', padx=2, pady=2)

    questionL = Label(root, text="question", justify=LEFT, anchor="w")
    questionL.grid(row=2, column=2, sticky='e' + 'w', padx=2, pady=2)
    clickL = Label(root, text="Click on the correct answer", fg='blue', justify=LEFT, anchor="w")
    clickL.grid(row=3, column=2, sticky='e' + 'w', padx=2, pady=2)
    answerB1 = Button(root, text="Answer1", justify=LEFT, anchor="w", command=sendAnswer1 )
    answerB1.grid(row=4, column=2, sticky='e' + 'w', padx=2, pady=2, columnspan=10)
    answerB2 = Button(root, text="Answer2", justify=LEFT, anchor="w", command=sendAnswer2 )
    answerB2.grid(row=5, column=2, sticky='e' + 'w', padx=2, pady=2, columnspan=10)
    answerB3 = Button(root, text="Answer3", justify=LEFT, anchor="w", command=sendAnswer3 )
    answerB3.grid(row=6, column=2, sticky='e' + 'w', padx=2, pady=2, columnspan=10)
    answerB4 = Button(root, text="Answer4", justify=LEFT, anchor="w", command=sendAnswer4 )
    answerB4.grid(row=7, column=2, sticky='e' + 'w', padx=2, pady=2, columnspan=10)
    root.mainloop()



if __name__ == '__main__':
    mainGUI ()
