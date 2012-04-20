import _mysql
import sys

#
# Function: find_db
# Description: finds a database within our default connection named 'Meep', returns empty tuple if not exists
#
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
def create_users_table(db):
    db.query("CREATE TABLE users (username VARCHAR(255), password VARCHAR(255));")

#
# Function: creates_messages_table
# Description: Creates the messages table - another durp
#
def create_messages_table(db):
    db.query("CREATE TABLE messages (id INT, title VARCHAR(255), post VARCHAR(255), author VARCHAR(255));")

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

con = None

try:
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

except _mysql.Error, e:
    print "MySql Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)
except:
    print "Unexpected Error"
    sys.exit(2)

finally:
    if con:
        con.close()
