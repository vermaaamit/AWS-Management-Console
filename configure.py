# configure.py
import pymysql

def get_db_connection():
    return pymysql.connect(
        host="employ-database.c2rsg2uwe0k9.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Rajesh1234",
        database="employee"
    )
