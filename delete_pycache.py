import os
import shutil
import stat

def on_rm_error(func, path, exc_info):
    """
    Callback per shutil.rmtree:
    - se il file/cartella è sola lettura, prova a cambiare i permessi e a ripetere l'operazione
    - altrimenti stampa un messaggio di errore più chiaro
    """
    try:
        # Togli sola lettura
        os.chmod(path, stat.S_IWUSR)
        func(path)
    except PermissionError as e:
        print(f"[PERMISSION ERROR] Non riesco a eliminare: {path}")
        print(f"Dettagli: {e}")
    except Exception as e:
        print(f"[ERRORE] Non riesco a eliminare: {path}")
        print(f"Dettagli: {e}")


def trova_cartelle_pycache(radice):
    """Restituisce una lista di percorsi di cartelle chiamate '__pycache__'."""
    cartelle_trovate = []
    for percorso_corrente, sottocartelle, _ in os.walk(radice):
        if "__pycache__" in sottocartelle:
            cartella_pycache = os.path.join(percorso_corrente, "__pycache__")
            cartelle_trovate.append(cartella_pycache)
    return cartelle_trovate


def main():
    percorso = input("Inserisci il percorso della cartella di partenza: ").strip().strip('"')

    if not os.path.isdir(percorso):
        print("Percorso non valido o inesistente.")
        return

    cartelle_pycache = trova_cartelle_pycache(percorso)

    if not cartelle_pycache:
        print("Nessuna cartella '__pycache__' trovata.")
        return

    print("\nSono state trovate le seguenti cartelle '__pycache__':\n")
    for c in cartelle_pycache:
        print(c)

    scelta = input("\nVuoi eliminarle tutte? [y/N]: ").strip().lower()

    if scelta == "y":
        print("\nEliminazione in corso...\n")
        for c in cartelle_pycache:
            try:
                shutil.rmtree(c, onerror=on_rm_error)
                print(f"Eliminata (o tentata): {c}")
            except Exception as e:
                print(f"Errore eliminando {c}: {e}")
        print("\nOperazione terminata (guarda eventuali errori sopra).")
    else:
        print("\nNessuna cartella eliminata.")


if __name__ == "__main__":
    main()
