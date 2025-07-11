# configure.py
import pymysql

def get_db_connection():
    return pymysql.connect(
        host="employee.c2rsg2uwe0k9.us-east-1.rds.amazonaws.com",
        user="amitverma",
        password="Rajesh1234",
        database="employee"
    )
