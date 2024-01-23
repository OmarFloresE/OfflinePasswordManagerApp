import sqlite3
from user import User

# For using a fresh DATABASE that lives on the RAM
# conn = sqlite3.connect(':memory:')


conn = sqlite3.connect('pm.db')

c = conn.cursor()

c.execute("""CREATE TABLE users (
    username text,
    email text,
    userID INTEGER
    )""" )

c.execute("""CREATE TABLE people (
    username text,
    email text,
    userID INTEGER
    )""" )


# c.execute("INSERT INTO users VALUES ('NoeMeow', 'floresNoe114@gmail.com', 6489803)")

def insert_user(u):
    with conn:
        c.execute("INSERT INTO users VALUES (:username, :email, :userID)",
        {'username':u.username, 'email':u.email, 'userID':u.userID})

def get_user_by_name(username):
    c.execute("SELECT * FROM users where username=:username", {'username': username}) # Search from username that gets passed in to the function
    return c.fetchall() # Instead of returning one, returns all


def update_email(u, email):
    with conn:
        c.execute("""UPDATE users SET email = :email
                    WHERE username = :username AND userID = :userID""",
                    {'username': u.username, 'userID': u.userID, 'email':email})

def remove_user(u):
    with conn:
        c.execute("DELETE from users WHERE username = :username", {'username': u.username}) 

user_1 = User("meowMix", "Cat@catmail.com", 696969)
user_2 = User("NoemeowMix", "Meow@catmail.com", 696968)

insert_user(user_1)
insert_user(user_2)

u = get_user_by_name('meowMix')
print(u)

update_email(user_1, 'Tiger@catmail.com')

u = get_user_by_name('meowMix')
print(u)



conn.close()



# # First Proper way to insert values into table
# c.execute("INSERT INTO users VALUES (?, ?, ?)", (user_1.username, user_1.email, user_1.userID))

# #Second Proper Way to Insert Values into table
# c.execute("INSERT INTO users VALUES (:username, :email, :userID)",
#     {'username':user_2.username, 'email':user_2.email, 'userID':user_2.userID})


# print(user_1.username)
# print(user_1.email)
# print(user_1.userID)


# c.execute("SELECT * FROM users where username=?", ('meowMix',))
# print(c.fetchall())

# print(c.fetchone())

# print(c.fetchmany())

# c.execute("SELECT * FROM users where username=:username", {'username':'NoemeowMix'})

# print(c.fetchall())



# if __name__ == "__main__":
#     main()