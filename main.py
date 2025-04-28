import tkinter as tk


import tkinter.ttk as ttk
import sqlite3

## Inzializzo il database
conn = sqlite3.connect('PY-Closer.db')

cursor = conn.cursor()
# Crea una tabella se non esiste già
cursor.execute('''
    CREATE TABLE IF NOT EXISTS codici (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice TEXT NOT NULL,
        stato integer NOT NULL,
        data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()



def execute_sql_query(code):
    """
    Esegui la query SQL fornita.
    """
    print(f"Eseguo la query SQL: {code}")
    ## Query
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO codici (codice, stato) VALUES (?, ?)", (code, 1))
        conn.commit()
        print("Query eseguita con successo")
    except sqlite3.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")



    #pass # Da rimuovere quando si usa un database

def on_submit():
    """
    Gestisci l'evento di invio del codice SQL.
    """
    code = code_entry.get()
    if code:
        execute_sql_query(code)
        # Pulisco il campo se ho inviato il codice
        code_entry.delete(0, tk.END)
        # Coloro la finestra di verde per indicare che è andato tutto bene
        root.configure(bg='green')
        root.after(200, lambda: root.configure(bg='lightgrey'))
        
    else:
        ## Pulisco il campo a prescindere per essere pronto alla prossima operazione
        code_entry.delete(0, tk.END)
        # Coloro la finestra di rosso per indicare che qualcosa è andato storto
        root.configure(bg='red')
        root.after(200, lambda: root.configure(bg='lightgrey'))
        print("Per piacere inserisci un codice")

# --- GUI Setup ---
root = tk.Tk()
root.title("PY-Closer")
## Ricava le dimensioni dello schermo
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# Eseui l'applicazione a tutto schermo
# root.attributes('-fullscreen', True) # mposto fullscreen
root.configure(bg='lightgrey') # Imposto il colore di sfondo come standard in grigio chiaro
# Centro la finestra
root.geometry(f"{screen_width}x{screen_height}+0+0") # Fullscreen


# formattazione della cella
content_frame = ttk.Frame(root)
content_frame.pack(expand=True)

# Inserimento del codice in maschera tramite pistola
code_entry = ttk.Entry(content_frame, width=30)
code_entry.pack(side=tk.LEFT, padx=5, pady=10)

## invio del codice al database
code_entry.bind("<Return>", lambda event: on_submit())
submit_button = ttk.Button(content_frame, text="Invio", command=on_submit)
submit_button.pack(side=tk.LEFT, padx=5, pady=10)

# --- Start GUI ---
root.mainloop()