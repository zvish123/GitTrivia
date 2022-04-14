# Protocol Constants

CMD_FIELD_LENGTH = 16	# Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10**LENGTH_FIELD_LENGTH-1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
MSG_DELIMITER = "#"

# Protocol Messages 
# In this dictionary we will have all the client and server command names
COMMAND_ADDITIONAL_DATA = {
    "LOGIN" : (2,'#'),
    "SEND_ANSWER" : (2,'#'),
    "LOGGED_ANSWER" : (None,','),
    "YOUR_QUESTION" : (6, '#'),
    "WRONG_ANSWER" : (1, None),
    "YOUR_SCORE" : (1, None),
    "ALL_SCORE" : (None, '\n'),
    "ERROR" : (1, None),
    "GAMES_LIST" : (None, '\n'),
    "GAME_SELECT_OK" : (2, '#'),
    "GAME_SELECT_NOT_OK" : (2, '#'),
    "SEND_GAME" : (1, None),
    "LOGIN_OK" : (1, None)
}

PROTOCOL_CLIENT = {
    "login_msg" : "LOGIN",
    "logout_msg" : "LOGOUT",
    'get_question_msg' : 'GET_QUESTION',
    'send_answer_msg' : 'SEND_ANSWER',
    'my_score_msg' : 'MY_SCORE',
    'highscore_msg' : 'HIGHSCORE',
    'logged_users_msg' : 'LOGGED',
    'get_games_msg' : 'GET_GAMES',
    'send_game_selection_msg' : 'SEND_GAME'
}

PROTOCOL_SERVER = {
    "login_ok_msg" : "LOGIN_OK",
    "login_failed_msg" : "ERROR",
    'logged_answer_msg' : "LOGGED_ANSWER",
    "your_question_msg" : "YOUR_QUESTION",
    "correct_answer_msg" : "CORRECT_ANSWER",
    "wrong_answer_msg" : "WRONG_ANSWER",
    "your_score_msg" : "YOUR_SCORE",
    "all_score_msg" : "ALL_SCORE",
    "error_msg" : "ERROR",
    "no_questions_msg" : "NO_QUESTIONS",
    "games_list_msg" : "GAMES_LIST",
    "game_selection_ok_msg" : "GAME_SELECT_OK",
    "game_selection_not_ok_msg" : "GAME_SELECT_NOT_OK"
}

# Other constants
ERROR_RETURN = None  # What is returned in case of an error

DEFAULT_GAME = 'questions.txt'

def is_valid(cmd, data):
    """
    check if valid command and if it meet the protocal format
    :param cmd: command
    :param data:
    :return: True if fit to protocol format, False if not according to protocol format
    """
    if cmd in PROTOCOL_CLIENT.values() or cmd in PROTOCOL_SERVER.values():
        if cmd in COMMAND_ADDITIONAL_DATA.keys():
            num_params, delimeter = COMMAND_ADDITIONAL_DATA[cmd]
            if (num_params is not None) and delimeter is not None and len(data.split(delimeter))!= num_params:
                return False
        elif data != '':	#no parameter expected if no entry in COMMAND_ADDITIONAL_DATA
            return False
    else:
        return False
    return True

def build_message(cmd, data):
    """
    Gets command name and data field and creates a valid protocol message
    Returns: str, or None if error occured
    """
    # Implement code ...
    full_msg = ""
    if is_valid(cmd, data):
        full_msg += cmd.ljust(CMD_FIELD_LENGTH , ' ') + DELIMITER
        data_len = str(len(data))
        full_msg += data_len.rjust(LENGTH_FIELD_LENGTH , '0') + DELIMITER
        full_msg += data
        return full_msg

    return None



def parse_message(msg):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    parts = msg.split(DELIMITER)
    if len(parts) == 3:
        cmd = parts[0].strip()
        data_length = None
        if parts[1].strip().isnumeric():
            data_length = int(parts[1].strip())
            data = parts[2]
            if data_length == len(data):
                return cmd, data

    return None, None


def split_msg(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's delimiter (|) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    # Implement code ...
    list = []
    if expected_fields >= 1:
        list = msg.split(MSG_DELIMITER)
        if expected_fields == len(list):
            return list

    return None


def join_msg(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the delimiter.
    Returns: string that looks like cell1|cell2|cell3
    """
    # Implement code ...
    msg = ''
    if len(msg_fields) == 0:
        return None
    elif len(msg_fields) == 1:
        return msg_fields[0]
    else:
        for field in msg_fields:
            if msg != '':
                msg += MSG_DELIMITER
            msg +=  field
    return  msg


