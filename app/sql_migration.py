import sqlite3
import json

# Connect to the database (or create it)
conn = sqlite3.connect("data.db")
cursor = conn.cursor()


# Drop existing tables if they exist
cursor.execute('''
    DROP TABLE IF EXISTS Users
''')

cursor.execute('''
    DROP TABLE IF EXISTS Requests
''')

# Define the Users table structure
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        phone TEXT,
        longitude REAL,
        latitude REAL
    )
''')

# Define the Requests table structure
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        longitude REAL,
        latitude REAL,
        address TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES Users(id)
    )
''')


# Insert mock data into Users table
users = [
    ("user1", "password1", "1234567890", -97.0985, 40.9072),
    ("user2", "password2", "0987654321", -97.0985, 40.9072),
    ("user3", "password3", "1122334455", -97.0985, 40.9072)
]

cursor.executemany('''
    INSERT INTO Users (username, password, phone, longitude, latitude)
    VALUES (?, ?, ?, ?, ?)
''', users)

# Insert mock data into Requests table
# Insert mock data into Requests table with the new address field
requests = [
]

cursor.executemany('''
    INSERT INTO Requests (user_id, description, status, timestamp, longitude, latitude , address)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', requests)

conn.commit()

# Query the Users table
cursor.execute('''
    SELECT * FROM Users
''')
users = cursor.fetchall()
print("Users:")
for user in users:
    print(user)

# Query the Requests table
cursor.execute('''
    SELECT * FROM Requests
''')
requests = cursor.fetchall()
print("\nRequests:")
for request in requests:
    print(request)

# Close the connection


conn.close()
