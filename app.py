import sqlite3
import os
import sys
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
    options = ["Show all notes", "New note", "Modify existing note", "Exit"]
    option, index = pick(options, indicator="> ")
    cls()
    match index:
        case 0:
            id = mostrarNotas() # This function should return an ID from the selected note, then provide another option menu to either
            subMenuNote(id)
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
    option, index = pick(options, indicator="> ")
    match index:
        case 0:
            modificarNota(id)
            mainMenu()
        case 1:
            eliminarNota(id)
            mainMenu()
        case 2:
            mainMenu()

def returnQueryText(id): # Returns an individual string from the "text" field matching an ID.
    n = dbCursor.execute(f"SELECT text FROM notes WHERE id = {id}")
    return n.fetchone()[0]

def cargarNota(): # Writes a new entry with an automatically assigned ID
    text = input("New note - ")
    dbCursor.execute("INSERT INTO notes (text) VALUES (?)", [text])

def modificarNota(id): # Modifies a row's text field with a given ID
    print(GREEN + f'Modifying: "{returnQueryText(id)}"' + RESET)
    newText = input("New content - ")
    dbCursor.execute("UPDATE notes SET text = ? WHERE id = ?", (newText, id))

def eliminarNota(id): # Removes a row matching by ID
    option = ""
    print("Are you sure you want to delete this note? [Y/N]\n", GREEN + f'"{returnQueryText(id)}"' + RESET)
    options = ["Y", "N"]
    #while option != "N" and option != "Y":
    while option not in options:
        option = input("> ").upper()
        if option != "N" and option != "Y":
            print("Please choose [Y/N]")
    if option == "N":
        subMenuNote(id)
    elif option == "Y":
        dbCursor.execute(f"DELETE FROM notes WHERE id = {id}")

def mostrarNotas(): # Displays all the notes available
    notas = dbCursor.execute("SELECT * FROM notes")
    options = [] # Create two lists, one with the options and another one with the DB ID so we can match indexes and get the ID data for later
    ids = [] # This is done because the pick() library can only work with lists, not dictionaries.
    for nota in notas:
        ids.append(nota[0])
        options.append(f"- {nota[1]}")
    options.append("Go to Main Menu")
    option, index = pick(options, indicator="> ")
    if option == "Go to Main Menu":
        mainMenu()
    else:
        return ids[index] # Returns the DB ID of the selected note for later

def handler(signum, frame):
    print('Signal handler called with signal', signum)

def exit():
    dbConnection.commit()
    dbConnection.close()
    sys.exit()

try:
    signal.signal(signal.SIGTSTP, signal.SIG_IGN) # Ignores CTRL-Z
    mainMenu()
except KeyboardInterrupt:
    print("Exiting unexpectedly... Please use the main menu next time!")
    dbConnection.commit()


