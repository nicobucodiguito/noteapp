import sqlite3
import os
import sys
import signal
import time
from pick import pick # https://github.com/wong2/pick

# Color palettes for ANSI color coding. Inspired by wordle.c from CS50
# Read more on ANSI codes here: https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
GREEN = "\u001b[32m"
RED = "\u001b[31m"
YELLOW = "\u001b[33m"
CYAN = "\u001b[36m"
RESET = "\u001b[0m"

def cls(): # Clear console, if OS is Windows, use 'cls' else use 'clear' - https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    os.system('cls' if os.name=='nt' else 'clear')

def mainMenu(): # Main menu
    options = ["Show notes", "New note", "Modify note", "Exit"]
    option, index = pick(options, indicator="○ ", title="Manage your notes")
    cls()
    match index:
        case 0:
            id = showNotes() # This function should return an ID from the selected note, then provide another option menu to either
            subMenuNote(id)
        case 1:
            newNote()
            mainMenu()
        case 2:
            id = showNotes()
            modifyNote(id)
            mainMenu()
        case 3:
            exit()

def subMenuNote(id):
    cls()
    options = ["Mark as done/undone", "Modify this note", "Delete this note", "Back"]
    option, index = pick(options, indicator="○ ", title='Options')
    match index:
        case 0:
            markNoteDone(id)
            mainMenu()
        case 1:
            modifyNote(id)
            mainMenu()
        case 2:
            deleteNote(id)
            mainMenu()
        case 3:
            mainMenu()

def markNoteDone(id):
    s = dbCursor.execute(f"SELECT state FROM notes WHERE id = {id}")
    s = s.fetchone()[0]
    if s == 0:
        text = dbCursor.execute(f"SELECT text FROM notes WHERE id = {id}")
        text = text.fetchone()[0]
        dbCursor.execute("UPDATE notes SET text = ?, state = ? WHERE id = ?", (text, 1, id))
    elif s == 1:
        text = dbCursor.execute(f"SELECT text FROM notes WHERE id = {id}")
        text = text.fetchone()[0]
        dbCursor.execute("UPDATE notes SET text = ?, state = ? WHERE id = ?", (text, 0, id))

def returnQueryText(id): # Returns an individual string from the "text" field matching an ID.
    n = dbCursor.execute(f"SELECT text FROM notes WHERE id = {id}")
    return n.fetchone()[0]

def newNote(): # Writes a new entry with an automatically assigned ID
    text = ""
    print("Press Ctrl-C to exit the program.\n" + GREEN + "Creating new note" + RESET)
    while text == "":
        text = input("> ")
        if text == "":
            print("Note cannot be empty.")
    dbCursor.execute("INSERT INTO notes (text) VALUES (?)", [text])

def modifyNote(id): # Modifies a row's text field with a given ID
    print("Press Ctrl-C to exit the program.\n" + GREEN + f'Modifying: "{returnQueryText(id)}"' + RESET)
    newText = ""
    while newText == "":
        newText = input("> ")
        if newText == "":
            print("Note cannot be empty.")
    dbCursor.execute("UPDATE notes SET text = ?, state = ? WHERE id = ?", (newText, 0, id))

def deleteNote(id): # Removes a row matching by ID
    option = ""
    print("Are you sure you want to delete this note? [Y/N]\n", GREEN + f'"{returnQueryText(id)}"' + RESET)
    options = ["Y", "N"]
    while option not in options:
        option = input("> ").upper()
        if option not in options:
            print("Please select a valid option. [Y/N]")
    if option == "N":
        subMenuNote(id)
    elif option == "Y":
        dbCursor.execute(f"DELETE FROM notes WHERE id = {id}")

def showNotes(): # Displays all the notes available
    notas = dbCursor.execute("SELECT * FROM notes")
    options = [] # Create two lists, one with the options and another one with the DB ID so we can match indexes and get the ID data for later
    ids = [] # This is done because the pick() library can only work with lists, not dictionaries.
    for nota in notas:
        ids.append(nota[0])
        if nota[2] == 0:
            options.append(f"□ {nota[1]}")
        else:
            text = '\u0336'.join(nota[1]) + '\u0336'
            options.append(f"■ {text}")
    options.append("Back")
    option, index = pick(options, indicator="○ ", title="Showing all notes, select a note for more options")
    if option == "Back": # Adds a final item to the list with the sole purpose of going back to the menu
        mainMenu()
    else:
        return ids[index] # Returns the DB ID of the selected note for later

def exit():
    cls()
    dbConnection.commit()
    dbConnection.close()
    print("Goodbye! Thank you " + YELLOW + "CS50" + RESET + " for everything!" + RED + " <3" + RESET)
    time.sleep(1)
    sys.exit()

if __name__ == "__main__":
    dbConnection = sqlite3.connect("notes.db", timeout=5) # Connection to the DB
    sqlite_create_table_query = '''CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    text TEXT NOT NULL, state INTEGER NOT NULL DEFAULT 0);'''
    dbCursor = dbConnection.cursor() # Cursor to the connection, allows interaction with the DB
    try:
        dbCursor.execute(sqlite_create_table_query) # Try to create the tables required, in case they already exist, start executing the program.
    except sqlite3.OperationalError:
        ...
    finally:        
        try:
            signal.signal(signal.SIGTSTP, signal.SIG_IGN) # Ignores Ctrl-Z and Ctrl-D
            mainMenu()
        except KeyboardInterrupt: #Ctrl-C is handled this exception
            cls()
            print(YELLOW + "Exiting unexpectedly... Please use the main menu next time!" + RESET)
            dbConnection.commit()

