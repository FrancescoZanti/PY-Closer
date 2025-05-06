import tkinter as tk
import tkinter.ttk as ttk
import sys
import sqlite3
from pynput import keyboard
from tkinterweb import HtmlFrame # Assicurati di averla installata: pip install tkinterweb
import threading
import os
from dotenv import load_dotenv

### Variabili da file .env
load_dotenv()
website_url = os.environ.get("website_url")
### Fine delle variabili da file .env

print(website_url)

# ---  Variabili globali ---
buffer = ""
root = None
status_label = None
keyboard_listener = None
conn = None
db_cursor = None

# --- Setup DB---
def init_db():
    global conn, db_cursor
    conn = sqlite3.connect('PY-Closer.db')
    db_cursor = conn.cursor()
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS codici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codice TEXT NOT NULL,
            stato INTEGER NOT NULL,
            data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def execute_sql_query(code):
    global status_label, conn, db_cursor
    if not conn or not db_cursor:
        print("Connessione al database non inizializzata.")
        if status_label:
            status_label.config(text="Errore: DB non connesso", background="red", fg="white")
        return False

    print(f"Eseguo la query SQL per il codice: {code}")
    try:
        db_cursor.execute("INSERT INTO codici (codice, stato) VALUES (?, ?)", (code, 1))
        conn.commit()
        print("Query eseguita con successo")
        if status_label:
            status_label.config(text=f"Codice Inserito: {code}", background="green", fg="white")
        return True
    except sqlite3.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        if status_label:
            status_label.config(text=f"Errore DB: {str(e)[:50]}", background="red", fg="white") # Mostra solo parte dell'errore
        return False

# --- Lettura ed elaborazione barcode ---
def process_barcode(barcode_data):
    if root and status_label: # Assicurati che la GUI sia inizializzata
        print(f"Processo il codice: {barcode_data}")
        execute_sql_query(barcode_data)
        # Dopo un breve ritardo, reimposta la status bar se non ci sono stati errori recenti
        # Questo evita che un messaggio di successo venga sovrascritto troppo rapidamente
        # da "Pronto per la scansione" se un altro codice viene scansionato subito.
        # Lo stato di errore persiste finché non c'è un successo.
        if status_label.cget("background") == "green":
             root.after(2000, lambda: status_label.config(text="Pronto per la scansione...", background="lightgrey", fg="black"))


# --- Monitoraggio tastiera ---
def on_key_press(key):
    global buffer
    try:
        # Aggiungi il carattere al buffer se è un carattere stampabile
        if hasattr(key, 'char') and key.char is not None:
            buffer += key.char
    except Exception as e:
        # Gestisci altri eventuali errori durante la pressione dei tasti
        print(f"Errore in on_key_press: {e}")


def on_key_release(key):
    global buffer, keyboard_listener, root, status_label

    if key == keyboard.Key.enter:
        current_buffer = buffer
        buffer = ""  # Resetta il buffer immediatamente
        if current_buffer:
            print(f"Codice letto (Invio): {current_buffer}")
            if root:
                 # Esegui l'elaborazione del codice nel thread principale di Tkinter
                 root.after(0, lambda b=current_buffer: process_barcode(b))
        elif status_label: # Se il buffer è vuoto ma si preme invio
            if status_label.cget("background") != "red": # Non sovrascrivere errori
                status_label.config(text="Pronto per la scansione...", background="lightgrey", fg="black")


    elif key == keyboard.Key.esc:
        print("Uscita dal programma richiesta (Esc).")
        if root:
            root.after(0, on_closing) # Chiama la funzione di chiusura dal thread principale
        return False  # Ferma il listener pynput

# --- GUI ---
def on_closing():
    global keyboard_listener, conn, root
    print("Chiusura applicazione...")
    if keyboard_listener:
        print("Fermo il listener della tastiera...")
        keyboard_listener.stop()
    if conn:
        print("Chiudo la connessione al database...")
        conn.close()
    if root:
        print("Distruggo la finestra principale...")
        root.quit() # Usa quit() per terminare mainloop in modo pulito
        root.destroy()
    print("Applicazione chiusa.")
    sys.exit()

# --- Applicazione principale ---
def start_keyboard_listener_thread():
    global keyboard_listener
    # Il listener pynput viene eseguito nel suo thread.
    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    keyboard_listener.start()
    print("Listener tastiera avviato.")

def main():
    global root, status_label

    init_db() # Inizializza il database

    # --- GUI Setup ---
    root = tk.Tk()
    root.title("PY-Closer")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    # Per un vero fullscreen senza barre del titolo (può variare per OS):
    # root.attributes('-fullscreen', True)

    # Status bar in alto
    status_label = tk.Label(root, text="Pronto per la scansione...", anchor='w',
                            bg="lightgrey", fg="black", font=("Helvetica", 16),
                            padx=10, pady=5)
    status_label.pack(side=tk.TOP, fill=tk.X)

    # WebView
    # Frame contenitore per la webview per gestire meglio il layout se necessario
    webview_container = tk.Frame(root)
    webview_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    try:
        webview = HtmlFrame(webview_container, messages_enabled=False, vertical_scrollbar=True)
        webview.pack(fill=tk.BOTH, expand=True)
        webview.load_website(website_url)  # Carica il sito web specificato nel file .env
    except Exception as e:
        print(f"Errore durante l'inizializzazione della WebView: {e}")
        error_label = tk.Label(webview_container,
                               text=f"Impossibile caricare la WebView: {e}\nAssicurati che tkinterweb sia installato e funzioni correttamente.",
                               fg="red", justify=tk.LEFT)
        error_label.pack(fill=tk.BOTH, expand=True)


    # Gestione chiusura finestra
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Avvia il listener della tastiera
    start_keyboard_listener_thread()

    # --- Start GUI ---
    try:
        root.mainloop()
    except KeyboardInterrupt: # Gestisce Ctrl+C nel terminale se la GUI non ha il focus
        print("Interruzione da tastiera (Ctrl+C) ricevuta, chiusura...")
        on_closing()
    finally:
        # Assicura una pulizia finale se mainloop esce inaspettatamente
        if keyboard_listener and keyboard_listener.is_alive():
            keyboard_listener.stop()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()