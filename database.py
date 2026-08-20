"""
database.py
Handles the single shared connection to MySQL.
Every other module imports get_connection() from here instead of
opening its own connection.
"""

import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self, host="localhost", user="root", password="your_password",
                 database="StudentRegistrationDB"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                use_pure=True
            )
            return self.connection
        except Error as e:
            print(f"Database connection failed: {e}")
            raise

    def get_cursor(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()
        return self.connection.cursor(dictionary=True)

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()


# Single shared instance used across the whole app.
# Change the password here once instead of in every file.
db = Database(password="your_password")