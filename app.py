import sqlite3

#.schema
#CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#text TEXT NOT NULL);
#CREATE TABLE sqlite_sequence(name,seq);

dbConnection = sqlite3.connect("notes.db") # Creates a connection with the DB
with dbConnection: # with automatically commits the changes
    dbCursor = dbConnection.cursor() # Creates a cursor which is needed to manipulate the DB and execute queries
    text = input("Texto: ")
    dbCursor.execute("INSERT INTO notes (text) VALUES (?)",
                    [text])
    v = dbCursor.execute("SELECT * FROM notes")
    for r in v:
        print(r[1]) # Tuple uses int indexes, not keys.
    dbCursor.close