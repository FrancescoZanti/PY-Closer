import tkinter as tk
import tkinter.ttk as ttk
import sys
import sqlite3

import dotenv
import os
from evdev import InputDevice, InputEvent, ecodes

dotenv.load_dotenv()
# Carica le variabili d'ambiente
device_x = os.path.join('/dev/input/event', os.getenv('device_x'))

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


## Definisco una funzione che mi permetta di leggere continnuamente da /dev/events
def read_events():
    """
    Leggi continuamente gli eventi da /dev/input/eventX.
    """
    # Apri il dispositivo di input
    device = InputDevice(device_x)  # Sostituisci con il tuo dispositivo
    # Inizializza il dispositivo
    device.grab()
    # Inizializza il ciclo di lettura degli eventi: se viene inserito un codice aggiungo il record a database
    while True:
        # Leggi gli eventi dal dispositivo
        events = device.read()
        for event in events:
            if event.type == ecodes.EV_KEY and event.value == 1:  # Se è un tasto premuto
                key_code = ecodes.KEY[event.code]
                print(f"Tasto premuto: {key_code}")
                # Qui puoi implementare la logica per gestire il codice inserito
                # Ad esempio, puoi chiamare la funzione on_submit() quando un codice è completo
                if key_code == 'ENTER':
                     on_submit()

    #pass  # Da implementare in base alla tua logica di lettura degli eventi

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
# Posizioni in alto in centro l'area di teso
#root.geometry(f"400x200+{int((screen_width - 400) / 2)}+{int((screen_height - 200) / 2)}") # Centro la finestra


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