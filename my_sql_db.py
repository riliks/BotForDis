import mysql.connector as connector
from config import user,password,host,database
def mysql(command):
  mydb = connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
  )

  mycursor = mydb.cursor()

  mycursor.execute(command)

  return mycursor.fetchall()

#"SELECT discipline FROM directs"