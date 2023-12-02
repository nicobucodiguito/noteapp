import sqlite3
import os
import signal
from pick import pick # https://github.com/wong2/pick

dbConnection = sqlite3.connect("notes.db", timeout=5) # Connection to the DB
dbCursor = dbConnection.cursor() # Cursor to the connection, allows interaction with the DB

# Color palletes for ANSI color coding
GREEN = "\u001b[32m" # ANSI Color codes, inspired by wordle.c from CS50
RESET = "\u001b[0m" # More on ANSI codes: https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html

def cls(): # Clear console, if OS is Windows, use 'cls' else use 'clear' - https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    os.system('cls' if os.name=='nt' else 'clear')

def mainMenu(): # Main menu
    options = ["Show notes", "New note", "Modify existing note", "Exit"]
    option, index = pick(options)
    cls()
    match index:
        case 0:
            id = mostrarNotas() # This function should return an ID from the selected note, then provide another option menu to either
            subMenuNote(id)
            # TODO: Submenu for individual note to either
            # Modify, delete (based on the ID previously collected) or go back
            # Should ask for confirmation
        case 1:
            cargarNota()
            mainMenu()
        case 2:
            id = mostrarNotas()
            modificarNota(id)
            mainMenu()
        case 3:
            exit()

def subMenuNote(id):
    options = ["Modify note", "Delete note", "Back"]
    option, index = pick(options)
    match index:
        case 0:
            modificarNota(id)
            mainMenu()
        case 1:
            ...
        case 2:
            mainMenu()

def returnQueryText(id): # Returns an individual string from the "text" field matching an ID.
    n = dbCursor.execute(f"SELECT text FROM notes WHERE id = {id}")
    return n.fetchone()[0]

def cargarNota(): # Writes a new entry with an automatically assigned ID
    text = input("New note - ")
    dbCursor.execute("INSERT INTO notes (text) VALUES (?)", [text])

def eliminarNota(): # Removes a row matching by ID
    id = int(input("ID: "))
    dbCursor.execute(f"DELETE FROM notes WHERE id = {id}")

def modificarNota(id): # Modifies a row's text field with a given ID
    print(GREEN + f'Modifying: "{returnQueryText(id)}"' + RESET)
    newText = input("New content - ")
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

def handler(signum, frame):
    print('Signal handler called with signal', signum)

def exit():
    dbConnection.commit()
    dbConnection.close()

try:
    signal.signal(signal.SIGTSTP, signal.SIG_IGN) # Ignores CTRL-Z
    mainMenu()
except KeyboardInterrupt:
    print("Exiting unexpectedly... Please use the main menu next time!")
    dbConnection.commit()


