import mysql.connector


def conectar():

    banco = mysql.connector.connect(

        host="localhost",

        user="root",

        password="734inf0",

        database="sistema_escola"

    )

    return banco