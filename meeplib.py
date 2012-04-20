#import pickle
import os.path
import _mysql
import sys
import MySQLdb
"""
meeplib - A simple message board back-end implementation.

Functions and classes:

 * u = User(username, password) - creates & saves a User object.  u.id
     is a guaranteed unique integer reference.

 * m = Message(title, post, author) - creates & saves a Message object.
     'author' must be a User object.  'm.id' guaranteed unique integer.

 * get_all_messages() - returns a list of all Message objects.

 * get_all_users() - returns a list of all User objects.

 * delete_message(m) - deletes Message object 'm' from internal lists.

 * delete_user(u) - deletes User object 'u' from internal lists.

 * get_user(username) - retrieves User object for user 'username'.

 * get_message(msg_id) - retrieves Message object for message with id msg_id.

"""

__all__ = ['Message', 'get_all_messages', 'get_message', 'delete_message',
           'User', 'get_user', 'get_all_users', 'delete_user']


###
# internal data structures & functions; please don't access these
# directly from outside the module.  Note, I'm not responsible for
# what happens to you if you do access them directly.  CTB

# a dictionary, storing all messages by a (unique, int) ID -> Message object.
_messages = {}

def _get_next_message_id():
    if _messages:
        return max(_messages.keys()) + 1
    return 0

# a dictionary, storing all users by a (unique, int) ID -> User object.
_user_ids = {}

# a dictionary, storing all users by username
_users = {}

#_filename = 'save.pickle'

def initialize():
    try:
        load_data()

        # create a default user
        if(len(get_all_users()) == 0):
            u = User('test', 'foo')
        else:
            u = get_user('test')
##        print 'loading'
##        print _filename
##        fp = open(_filename)
##        # load data
##        obj = pickle.load(fp)
##        fp.close()
##        print 'file retrieved'
##        global _users, _user_ids, _messages
##        _users = obj[0]
##        _user_ids = obj[1]
##        _messages = obj[2]
##        print "number of users: %d" %(len(_users),)
##        print "most current user: %s" %(_users[max(_users.keys())].username,)
##        print 'successfully loaded data'
    except:  # file does not exist/cannot be opened
        print 'error loading. loading defaults'
        # create a default user
        u = User('foo', 'bar')
        # create a single message
        Message('my title', 'This is my message!', u)

##def _save():
##    obj = []
##    obj.append(_users)
##    obj.append(_user_ids)
##    obj.append(_messages)
##    try:
##        print 'saving'
##        fp = open(_filename, 'w')
##        pickle.dump(obj, fp)
##        fp.close()
##        print 'successful'
##    except IOError:
##        pass

def _get_next_user_id():
    if _users:
        return max(_user_ids.keys()) + 1
    return 0

def _reset():
    """
    Clean out all persistent data structures, for testing purposes.
    """
    global _messages, _users, _user_ids
    _messages = {}
    _users = {}
    _user_ids = {}

###  

class Message(object):
    """
    Simple "Message" object, containing title/post/author.

    'author' must be an object of type 'User'.

    """
    def __init__(self, title, post, author):
        self.title = title
        self.post = post

        assert isinstance(author, User)
        self.author = author
        #adding another property to the Message object for replies
        self.replies = []
        self._save_message()

    def _save_message(self):
        self.id = _get_next_message_id()


        # register this new message with the messages list:
        _messages[self.id] = self
        #_save()
        
    #addReply will add the reply paramter to the self.replies string array
    def add_reply(self, reply):
        self.replies.append(str(reply))
        #_save()

def get_all_messages(sort_by='id'):
    return _messages.values()

def get_message(id):
    return _messages[id]

def delete_message(msg):
    assert isinstance(msg, Message)
    del _messages[msg.id]
    #_save()

###

class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self._save_user()

    def _save_user(self):
        self.id = _get_next_user_id()

        # register new user ID with the users list:
        _user_ids[self.id] = self
        _users[self.username] = self
       # _save()

def get_user(username):
    return _users.get(username)         # return None if no such user

def get_all_users():
    return _users.values()

def delete_user(user):
    del _users[user.username]
    del _user_ids[user.id]
    #_save()


##########################################
#       Database Stuff
##########################################





def find_db(con):
    con.query("""SHOW DATABASES""")
    db_results = con.store_result()

    db = db_results.fetch_row()

    while db != ():
        if db == (('test',),):
            break;
        db = db_results.fetch_row()


    return db

#
# Function: create_users_table
# Description: Creates the user table - durp
#
def create_users_table(con):
    con.query("CREATE TABLE users (id INT, username VARCHAR(255), password VARCHAR(255));")

#
# Function: creates_messages_table
# Description: Creates the messages table - another durp
#
def create_messages_table(con):
    con.query("CREATE TABLE messages (id INT, title VARCHAR(255), post VARCHAR(255), author_id INT);")

#
# Function - create_replies_table
# Description:  Creates the replies table - durp durp
#
def create_replies_table(con):
    con.query("CREATE TABLE replies (message_id INT, post VARCHAR(255));")

#
# Function: table_exists
# Defintion: sees if the incoming table exists
#
def table_exists(con, table_name):
    con.query("SELECT table_name " +
        "FROM information_schema.tables " +
        "WHERE table_schema = 'test' " +
        "AND table_name = '%s';"%table_name)

    result = con.store_result()
    return result.fetch_row() != ()

#
# Function load_messages
# Definition: puts messages in db into cache
#
def load_messages(con):
    con.query("""SELECT * FROM messages""")

    r = con.use_result()
    t = r.fetch_row()
    while t != ():
        record = t[0]
        message_key = int(record[0])
        author_key = int(record[3])
        _messages[message_key] = Message(record[1], record[2], _users[author_key])
        _messages[message_key].new = False
        t = r.fetch_row()

#
# Function: load_users
# Definition: puts users from db into cache
#
def load_users(con):
    con.query("""SELECT * FROM users""")

    r = con.use_result()
    t = r.fetch_row()
    while t != ():
        record = t[0]
        key = int(record[0])
        _users[key] = User(record[1], record[2])
        _users[key].new = False
        t = r.fetch_row()

#
# Function load_replies
# Definition: puts replies from db into cache
#
def load_replies(con):
    con.query("""SELECT * FROM replies""")

    r = con.use_result()
    t = r.fetch_row()
    while t != ():
        record = t[0]
        message_key = int(record[0])

        if not _replies.get(message_key):
            _replies[message_key] = []
             
        _replies[message_key].append(record[1])
        t = r.fetch_row()

#
# Function: save_messages
# Definition: puts messages from cache into db
#
def save_messages(con):
    for key in _messages.iterkeys():
        if _messages[key].new:
            q = ("""INSERT INTO messages (id, title, post, author) VALUES ({0}, '{1}', '{2}', {3})""".format(
                key, 
                _messages[key].title, 
                _messages[key].post, 
                _messages[key].author.id))
            con.query(q)

            if _replies.get(key) is not None:
                for reply in _replies.get(key):
                    save_reply(con, key, reply)

#
# Function save_reply
# Definition: puts reply from cache into db
#
def save_reply(con, key, reply):
    q = ("""INSERT INTO replies (message_id, post) VALUES ({0}, '{1}')""".format(
        key, 
        reply))
    con.query(q)

#
# Function: save_users
# Definition: puts users from cache into db
#
def save_users(con):
    for user in _users.itervalues():
        if user.new:
            q = ("""INSERT INTO users (id, username, password) VALUES ({0}, '{1}', '{2}')""".format(
                user.id, 
                user.username, 
                user.password))
            con.query(q)

def load_data():
    try:
        global con
        con = _mysql.connect()
        db = find_db(con)

        if db == ():
            print "could not find database test"
            sys.exit(1)

        con.query("USE test")
        if not table_exists(con, "users"):
            print "creating table users"
            create_users_table(con)
        if  not table_exists(con, "messages"):
            print "creating table messages"
            create_messages_table(con)
        if not table_exists(con, "replies"):
            print 'creating replies table'
            create_replies_table(con)

        load_users(con)
        load_messages(con)
        load_replies(con)
        
    except _mysql.Error, e:
        print "MySql Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

def save_data():
    try:
        save_users(con)
        save_messages(con)

    except _mysql.Error, e:
        print "MySql Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)



#edited meeplib for reply functionality 11/23/12



