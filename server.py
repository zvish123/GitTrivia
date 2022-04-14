##############################################################################
# server.py
##############################################################################

import socket
import chatlib
import select
from user_db import UserDb
import user_db

import os
# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
is_logged_in = False
# Targil-8
messages_to_send = [] # tuple: (socket, message)
open_clients_sockets = []
current_game = chatlib.DEFAULT_GAME

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"
DEFAULT_QUESTION_FILE = r'.\TriviaFiles\\' + current_game
#QUESTION_FILE = r'C:\Users\user\trivia\Multiple_Choice_Trivia.txt'
#USERS_FILE = r'.\DB\users.txt'
DISPLAY_MSG = True
userdb = UserDb()

# HELPER SOCKET METHODS


def build_and_send_message(conn, code, msg):
    global  DISPLAY_MSG
    global messages_to_send
    full_msg = chatlib.build_message (code, msg)
    print ("[SERVER] ", full_msg)  # Debug print
    #conn.send (bytes (full_msg, 'utf-8'))
    messages_to_send.append((conn, bytes (full_msg, 'utf-8')))  # Targil-8
    if DISPLAY_MSG:
        print(f'message appended to send ({conn}), ({full_msg}')



def recv_message_and_parse(conn):
    try:
        full_msg = conn.recv (1024).decode ()
        if DISPLAY_MSG:
            print(f'recived message: {full_msg}')
    except ConnectionAbortedError:
        return None, ""
    except OSError:
        return None, ""
    if full_msg == "":  # Targil-8
        return "",""
    else:
        print ("[CLIENT] ", full_msg)  # Debug print
        cmd, msg = chatlib.parse_message (full_msg)
        return cmd, msg

#EXER-8
def print_client_sockets():
    global open_clients_sockets
    for s in open_clients_sockets:
        print(s.getpeername())

# Data Loaders #
def load_questions(trivia_game=DEFAULT_QUESTION_FILE):
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    global questions
    FIRST_QUESTION_NUMBER = 1000

    with open (trivia_game) as fp:
        for cnt, line in enumerate (fp):
            # print("Line {}: {}".format(cnt, line))
            list = line.split ('|')
            # print(list)
            inside_dict = {}
            inside_dict["question"] = list[0]
            answers = []
            for i in range (1, 5):
                answers.append (list[i])
            inside_dict["answers"] = answers
            inside_dict["correct"] = list[5].split ('\n')[0]
            questions[(FIRST_QUESTION_NUMBER + cnt)] = inside_dict
    # print(questions)
    # questions = {
    # 			2313 : {"question":"How much is 2+2","answers":["3","4","2","1"],"correct":2},
    # 			4122 : {"question":"What is the capital of France?","answers":["Lion","Marseille","Paris","Montpellier"],"correct":3}
    # 			}
    #
    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    global users
    global userdb
    # with open (USERS_FILE) as fp:
    #     for cnt, line in enumerate (fp):
    #         # print("Line {}: {}".format(cnt, line))
    #         line = line[:-1]
    #         list = line.split ('|')
    #         inside_dict = {}
    #         inside_dict["password"] = list[1]
    #         inside_dict["score"] = int (list[2])
    #         questions_asked = []
    #         if len (list) > 3:
    #             qa_list = list[3].split (',')
    #             for q in qa_list:
    #                 if q != '\n':
    #                     questions_asked.append (int (q))
    #         inside_dict["questions_asked"] = questions_asked
    #         users[list[0]] = inside_dict

    # users = {
    # 		"test"		:	{"password":"test","score":0,"questions_asked":[]},
    # 		"yossi"		:	{"password":"123","score":50,"questions_asked":[]},
    # 		"master"	:	{"password":"master","score":200,"questions_asked":[]}
    #		}
    #print (users)

    users = userdb.database

    return users


# def save_user_database():
#     """
#     Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
#     Recieves: -
#     Returns: user dictionary
#     """
#     global users
#
#     user_file = open (USERS_FILE, 'w')
#
#     for item in users.items():
#         line = item[0]+'|'
#         line += item[1]["password"]+'|'
#         line += str(item[1]["score"])+'|'
#         if len(item[1]) > 2:
#             for q in item[1]["questions_asked"]:
#                 line += str(q) + ','
#         line = line[:-1]
#         line += '\n'
#         user_file.write(line)
#     user_file.close()
#
#     # users = {
#     # 		"test"		:	{"password":"test","score":0,"questions_asked":[]},
#     # 		"yossi"		:	{"password":"123","score":50,"questions_asked":[]},
#     # 		"master"	:	{"password":"master","score":200,"questions_asked":[]}
#     #		}

# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    # Implement code ...
    server_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind ((SERVER_IP, SERVER_PORT))
    server_socket.listen ()
    print (f'server is up at port {SERVER_PORT}')

    # client_socket, client_address = server_socket.accept ()
    # print ('client connected')

    return server_socket


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    # Implement code ...
    cmd = chatlib.PROTOCOL_SERVER['error_msg']
    build_and_send_message (conn, cmd, error_msg)


##### MESSAGE HANDLING


def handle_getscore_message(conn, username):
    global users
    # Implement this in later chapters
    print (username)
    score = str (users[username]["score"])
    cmd = chatlib.PROTOCOL_SERVER['your_score_msg']
    build_and_send_message (conn, cmd, score)

def keyfunc(tup):
    key, data = tup
    return data["score"]

def handle_highscore_message(conn, username):
    global users
    # Implement this in later chapters
    print (username)
    items = sorted(users.items(), key = keyfunc, reverse=True)
    #size = min(len(users), 5)
    high_score_str = ""
    #i=1
    for item in items:
       high_score_str+=item[0]+":"+str(item[1]["score"])+"\n"

    cmd = chatlib.PROTOCOL_SERVER['all_score_msg']
    build_and_send_message (conn, cmd, high_score_str)


def handle_get_logged_users_message(conn):
    global users
    # Implement this in later chapters
    logged_users_str = ''
    for user in logged_users.values():
        logged_users_str += user + ","
    logged_users_str = logged_users_str[:-1]

    cmd = chatlib.PROTOCOL_SERVER['logged_answer_msg']
    build_and_send_message (conn, cmd, logged_users_str)



def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    global DISPLAY_MSG
    global questions
    global current_game

    # Implement code ...
    try:
        #del logged_users[conn.getpeername ()]
        logged_users.pop(conn.getpeername ())
        open_clients_sockets.remove(conn)
        questions = {}
        current_game = ''
        #if DISPLAY_MSG:
        print(logged_users)
    except KeyError:
        pass
    conn.close ()


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later
    global questions
    global userdb
    global current_game
    #global is_logged_in

    # Implement code ...
    if DISPLAY_MSG:
        print('start login checks ...')
    list = data.split (chatlib.MSG_DELIMITER)
    user = list[0]
    password = list[1]
    print (user, users)
    if user in users and users[user]['password'] == password:
        if user in logged_users.values():
            send_error (conn, 'User already logged in')
        else:
            logged_users[conn.getpeername ()] = user
            if DISPLAY_MSG:
                print(f'Login: {logged_users} ')
            cmd = chatlib.PROTOCOL_SERVER['login_ok_msg']
            current_game = userdb.get_user_trivia_repository(user)
            build_and_send_message (conn, cmd, current_game)
            file = r'.\TriviaFiles\\' + current_game
            print("loading..  " + file)
            questions = load_questions(file)
            #is_logged_in = True
    else:
        send_error (conn, 'Incorrect user or password')
        #is_logged_in = False


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users  # To be used later
    #global is_logged_in
    # if DISPLAY_MSG:
    #     print(f'is logged in: {is_logged_in}, cmd = {cmd}')
    # Implement code ...
    try:
        if DISPLAY_MSG:
            print(f'{logged_users} : {conn.getpeername()}')
        is_logged_in = len(logged_users) > 0 and logged_users[conn.getpeername()] != None
    except KeyError:
        is_logged_in =  False
    except OSError:
        return

    if is_logged_in:
        if cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
            handle_logout_message (conn)
            #is_logged_in = False
        elif cmd == chatlib.PROTOCOL_CLIENT["my_score_msg"]:
            handle_getscore_message (conn, logged_users[conn.getpeername ()])
        elif cmd == chatlib.PROTOCOL_CLIENT["get_question_msg"]:
            handle_question_message (conn, logged_users[conn.getpeername ()])
        elif cmd == chatlib.PROTOCOL_CLIENT["send_answer_msg"]:
            handle_answer_message (conn, logged_users[conn.getpeername ()], data)
        elif cmd == chatlib.PROTOCOL_CLIENT["highscore_msg"]:
            handle_highscore_message (conn, logged_users[conn.getpeername ()])
        elif cmd == chatlib.PROTOCOL_CLIENT["logged_users_msg"]:
            handle_get_logged_users_message (conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["get_games_msg"]:
            handle_get_games_message (conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["send_game_selection_msg"]:
            handle_get_game_Selection_message (conn, logged_users[conn.getpeername ()], data)
        else:
            send_error (conn, "Unknown command to server")
    else:
        if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
            handle_login_message (conn, data)
        else:
            send_error (conn, "Log in befor sending commands")


# Targil #7

def create_random_question(user):
    '''
    Return new question from dictionary that was not used by the user.
    according to: id#question#answer1#answer2#answer3#answer4
    if no question available in return None
    :param user:
    :return: YOUR_QUESTION message according to protocol
    '''
    global users
    global questions
    asked_questions = users[user]['questions_asked']

    if len(asked_questions) == len(questions.keys ()):  ###check where quwstions filled
        return None
    remaining_questions = []
    for q in questions.keys():
        if q not in asked_questions:
            remaining_questions.append (q)
    import random

    q_num = random.randint (0, len (remaining_questions)-1)
    q_num = remaining_questions[q_num]
    question_data = str (q_num)
    question_data += chatlib.MSG_DELIMITER + questions[q_num]["question"]
    answers = questions[q_num]["answers"]
    for a in answers:
        question_data += chatlib.MSG_DELIMITER + a
    qa = users[user]['questions_asked']
    qa.append(q_num)
    users[user]['questions_asked'] = qa

    return question_data


def handle_question_message(conn, user):
    '''
    Send random question from dictionary that was not used by the user or NO_QUESTIONS
    :param conn:
    :param user:
    :return:
    '''
    random_question = create_random_question(user)
    if random_question == None:
        cmd = chatlib.PROTOCOL_SERVER['no_questions_msg']
        build_and_send_message (conn, cmd, "")
    else:
        cmd = chatlib.PROTOCOL_SERVER['your_question_msg']
        build_and_send_message (conn, cmd, random_question)

def handle_get_games_message (conn):
    global games
    answer = ''
    with open (r".\TriviaFiles\TriviaFiles.txt") as fp:
        for line in fp:
            data = line.split('|')
            answer += data[0] + ": " + data[2] + " (" + data[3].split('\n')[0] + ")\n"
    cmd = chatlib.PROTOCOL_SERVER['games_list_msg']
    build_and_send_message (conn, cmd, answer)


# def clean_user_data(user):
#     global users
#     # opening the file in read mode
#     file = open(USERS_FILE, "r")
#     replacement = ""
#     # using the for loop
#     for line in file:
#         line = line.strip()
#         print(line)
#         parts = line.split('|')
#         if parts[0] == user and len(parts) > 3:
#             changes = parts[0] + '|' + parts[1] + '|' + parts[2]
#         else:
#             changes = line
#         replacement = replacement + changes + "\n"
#
#     file.close()
#     print(replacement)
#     # opening the file in write mode
#     fout = open(USERS_FILE, "w")
#     fout.write(replacement)
#     fout.close()
#     #print(users[user]['questions_asked'])
#     users[user]['questions_asked'] = []

def handle_get_game_Selection_message (conn, user, reply):
    global questions
    global current_game
    global userdb
    global users
    found = False
    with open (r".\TriviaFiles\TriviaFiles.txt") as fp:
        for line in fp:
            data = line.split('|')
            if data[0] == reply:
                current_game = data[1]
                userdb.update_user_trivia_repository(user,current_game )
                file = r'.\TriviaFiles\\' + current_game
                print("loading..  " + file)
                questions = load_questions(file)
                found = True
    if found:
        cmd = chatlib.PROTOCOL_SERVER['game_selection_ok_msg']
        build_and_send_message (conn, cmd , "OK" + chatlib.MSG_DELIMITER +current_game)
        userdb.clean_user_used_questions(user)
        users = userdb.database
        #clean_user_data(user)
    else:
        cmd = chatlib.PROTOCOL_SERVER['game_selection_not_ok_msg']
        build_and_send_message (conn, cmd , "Not OK" + chatlib.MSG_DELIMITER + "")




def handle_answer_message(conn, user, reply):
    '''
    :param conn:
    :param user:
    :param answer:
    :return:
    '''
    global users
    global userdb
    q_num , answer = reply.split(chatlib.MSG_DELIMITER)
    correct = str(questions[int(q_num)]['correct'])
    if answer == correct:
        cmd = chatlib.PROTOCOL_SERVER['correct_answer_msg']
        correct = ""
        #add score to user
        #users[user]["score"] = users[user]["score"] + 5
        userdb.add_to_user_score(user,5)
        users = userdb.database
    else:
        cmd = chatlib.PROTOCOL_SERVER['wrong_answer_msg']
    build_and_send_message (conn, cmd, correct)
    #save_user_database()

#EXER-8
def send_waiting_messages(wlist):
    global DISPLAY_MSG
    for message in messages_to_send:
        current_socket, data = message
        if current_socket in wlist:
            if type(data) is str:
                data = data.encode()
            current_socket.send(data)
            if DISPLAY_MSG:
                print(f'socket ({current_socket}) sent: {data}')
            messages_to_send.remove(message)



def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions
    global open_clients_sockets # Targil-8
    global DISPLAY_MSG # Targil-8

    print ("Welcome to Trivia Server!")
    server_socket = setup_socket()
    #questions = load_questions()
    questions = {}
    users = load_user_database()

    # Implement code ...

    while True:
        # Targil-8
        try:
            rlist, wlist, xlist = select.select( [server_socket] + open_clients_sockets, open_clients_sockets, [] )
        except ValueError:
            print(open_clients_sockets)
        for current_socket in rlist:
            if current_socket is server_socket:
                (new_socket, address) = server_socket.accept()
                print("new client connected to server: ", new_socket.getpeername())
                open_clients_sockets.append(new_socket)
                if DISPLAY_MSG:
                    print(f'New socked appended: {new_socket}')
            else:
                #print ('New data from client!')
                cmd, msg = recv_message_and_parse (current_socket)
                handle_client_message (current_socket, cmd, msg)

        send_waiting_messages(wlist)  # Targil-8

    client_socket.close ()
    server_socket.close ()


if __name__ == '__main__':
    main ()
