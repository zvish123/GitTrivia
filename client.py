import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678

DISPLAY_MSG = False

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

def logout(conn):
    # Implement code
    build_and_send_message (conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")


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

def get_highscore(socket):
    cmd, msg = build_send_recv_parse(socket, chatlib.PROTOCOL_CLIENT["highscore_msg"], '' )
    if cmd == chatlib.PROTOCOL_SERVER["all_score_msg"]:
        score = msg.split('\n')[0]
    else:
        print('Problem in getting score')
        score = "Empty list"
    return score

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


if __name__ == '__main__':
    main ()
