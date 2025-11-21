Cecchelani Diego - 386276
# Ghosts And Goblins - Progetto python per il corso di informatica e laboratorio di programmazione (2025/2026)

Questo progetto è un gioco 2D ispirato a Ghosts 'n Goblins, scritto in Python.
Utilizza una libreria grafica basata su `pygame` (wrapper interno `g2d`) e una architettura ad entità (player, nemici, piattaforme, porte, ecc.).

Il codice è organizzato in modo modulare e in grado di separare del tutto logica di gioco e rendering grafico, con particolare attenzione alla leggibilità: classi come `Arthur`, `Zombie`, `Plant`, `Flame`, `Door`, `Platform`, `Game`, `Camera`, `GraphicalInterface` e `MenuManager` sono documentate con docstring in italiano.


## Requisiti
I principali requisiti Python sono elencati in `requirements.txt`.  
Al minimo, il progetto usa:
```text
pygame==2.6.1
Pillow==11.3.0
```

(Anche se Pillow non è obbligatorio in quanto è presente un sistema di fallback)
