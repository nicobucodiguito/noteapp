import sqlite3
import os
from pick import pick # https://github.com/wong2/pick

dbConnection = sqlite3.connect("notes.db", timeout=30)
dbCursor = dbConnection.cursor()

GREEN = "\u001b[32m" # ANSI Color codes, inspired by wordle.c from CS50
RESET = "\u001b[0m" # More on ANSI codes: https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html


def cls(): # Clear console, if OS is Windows, use 'cls' else use 'clear' - https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    os.system('cls' if os.name=='nt' else 'clear')

def mainMenu():
    options = ["Show notes", "Create new note", "Remove note", "Modify existing note"]
    option, index = pick(options)
    match index:
        case 0:
            mostrarNotas() # This function should return an ID from the selected note, then provide another option menu to either
            # Modify, delete (based on the ID previously collected) or go back
        case 1:
            cargarNota()
            mainMenu()

def returnQueryText(id): # Returns an individual string from the "text" field matching an ID.
    n = dbCursor.execute(f"SELECT text FROM notes WHERE id = {id}")
    return n.fetchone()[0]

def cargarNota(): # Writes a new entry with an automatically assigned ID
    text = input("New note: ")
    dbCursor.execute("INSERT INTO notes (text) VALUES (?)", [text])

def eliminarNota(): # Removes a row matching by ID
    id = int(input("ID: "))
    dbCursor.execute(f"DELETE FROM notes WHERE id = {id}")

def modificarNota(): # Modifies a row's text field with a given ID
    id = int(input("ID: "))
    print(GREEN + f'Modifying: "{returnQueryText(id)}"' + RESET)
    newText = input("New content: ")
    dbCursor.execute("UPDATE notes SET text = ? WHERE id = ?", (newText, id))

def mostrarNotas(): # Displays all the notes available
    notas = dbCursor.execute("SELECT * FROM notes")
    options = [] # Create two lists, one with the options and another one with the DB ID so we can match indexes and get the ID data for later
    ids = [] # This is done because the pick() library can only work with lists, not dictionaries.
    for nota in notas:
        options.append(nota[1])
        ids.append(nota[0])
    option, index = pick(options)
    return ids[index] # Returns the DB ID of the selected note for later

mainMenu()
dbConnection.commit()
dbConnection.close()