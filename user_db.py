import json
import threading

class UserDb:

    def __init__(self):
        self.fileName = r'.\DB\usersDB.json'
        self.lock = threading.Lock()
        self.sem = threading.Semaphore(10)
        f = open(self.fileName, "r+")
        self.database = json.load(f)
        f.close()


    def read_user(self, key):
        self.lock.acquire()
        self.sem.acquire()
        self.lock.release()
        try:
            value = self.database[key]
        except KeyError:
            value = None
        self.sem.release()
        return value

    def update_database(self, data):
        self.lock.acquire()
        self.sem.acquire()
        self.lock.release()
        with open(self.fileName, "w") as jsonFile:
            json.dump(data, jsonFile)
        self.sem.release()

    def __update_database(self):
        # jsonFile = open(self.fileName, "r+")
        # jsonFile.write(json.dumps(data))
        # jsonFile.close()
        with open(self.fileName, "w") as jsonFile:
            json.dump(self.database, jsonFile)

    def add_to_user_score(self, key, amount):
        self.lock.acquire()
        self.sem.acquire()
        self.lock.release()
        try:
            userData = self.database[key]
            userData['score'] = userData['score'] + amount
            self.__update_database()
        except ValueError:
            pass
        self.sem.release()

    def get_user_trivia_repository(self, key):
        try:
            userData = self.database[key]
            tr = userData['triviaRepository']
            self.__update_database()
        except ValueError:
            tr = None
        return tr


    def update_user_trivia_repository(self, key, repository):
        self.lock.acquire()
        self.sem.acquire()
        self.lock.release()
        try:
            userData = self.database[key]
            userData['triviaRepository'] = repository
            self.__update_database()
        except ValueError:
            pass
        self.sem.release()


    def clean_user_used_questions(self, key):
        self.lock.acquire()
        self.sem.acquire()
        self.lock.release()
        try:
            userData = self.database[key]
            userData['questions_asked'] = []
            self.__update_database()
        except ValueError:
            pass
        self.sem.release()


    def update_user_used_questions(self, key, question):
        self.lock.acquire()
        self.sem.acquire()
        self.lock.release()
        try:
            userData = self.database[key]
            questions_asked = userData['questions_asked']
            exist = False
            for q in questions_asked:
                if q == question:
                    exist = True
            if not exist:
                questions_asked.append(question)
                self.__update_database()
        except ValueError:
            pass
        self.sem.release()


    def is_user_use_question(self, key, question):
        try:
            exist = False
            userData = self.database[key]
            questions_asked = userData['questions_asked']
            for q in questions_asked:
                if q == question:
                    exist = True
        except ValueError:
            exist = False

        return exist


def main():
    x = UserDb()
    print(x.database["admin"])
    x.add_to_user_score('admin', 10)
    print(x.database["admin"])
    data = x.database["admin"]
    # print(x.read_user('abc'))
    # print(x.read_user('admin'))
    # print(x.read_user('Test'))
    #
    # x.add_to_user_score('abc', 5)
    # print(x.read_user('abc'))
    # print(x.read_user('admin'))
    #
    # x.update_user_trivia_repository('abc','trivia3.txt')
    # print(x.read_user('abc'))
    # # #
    # x.update_user_used_questions('abc', 1030)
    # x.update_user_used_questions('abc', 1020)
    # x.update_user_used_questions('abc', 1040)
    # print(x.read_user('abc'))
    # x.clean_user_used_questions('abc')
    # print(x.read_user('abc'))

if __name__ == '__main__':
    main()
