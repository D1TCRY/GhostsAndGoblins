_386276 - Cecchelani Diego_
# Ghosts and Goblins – Clone 2D

Progetto di gioco 2D ispirato a **Ghosts 'n Goblins**, realizzato come esercitazione per il primo anno del corso di **Ingegneria delle Tecnologie Informatiche** (Università di Parma).

L’obiettivo è implementare un videogame a scorrimento orizzontale con:
- gestione di **entità** (giocatore, nemici, piattaforme, scale, proiettili…),
- **fisica semplificata** (gravità, salti, caduta),
- **collisioni** e gestione dei danni,
- **camera** che segue il giocatore,
- **interfaccia grafica** con barre vita/cooldown,
- **menu principale** e schermate di vittoria/sconfitta.

---

## Indice

- [Requisiti](#requisiti)
- [Esecuzione](#esecuzione)
- [Comandi di gioco](#comandi-di-gioco)
- [Regole di gioco](#regole-di-gioco)
- [Struttura del progetto](#struttura-del-progetto)
  - [Core](#core)
  - [Entities](#entities)
  - [GUI](#gui)
  - [State](#state)
  - [Dati e configurazione](#dati-e-configurazione)
- [Dettagli di implementazione](#dettagli-di-implementazione)
  - [Gestione delle collisioni](#gestione-delle-collisioni)
  - [Camera e rendering](#camera-e-rendering)
  - [Spawn dei nemici](#spawn-dei-nemici)
- [Testing](#testing)
- [Possibili estensioni future](#possibili-estensioni-future)
- [Autore](#autore)

---

## Requisiti

- **Python** ≥ 3.10  
- Librerie Python:
  - `g2d` (fornita a lezione / in `src/g2d_lib`)
  - `Pillow` (per gestire alcuni effetti di luminosità sugli sprite – opzionale: il gioco funziona anche senza)
- Sistema operativo: qualunque (Windows, Linux, macOS) su cui giri Python e la libreria grafica usata da `g2d`.

---

## Esecuzione

Dalla cartella principale del progetto:

```bash
python -m src.main
```

oppure, se il file di avvio è diverso, eseguire il modulo che richiama la funzione:

La funzione di ingresso del gioco è infatti `game.core.app.main()`, che:

* crea un oggetto `App`,
* inizializza il canvas tramite `init_canvas(...)`,
* avvia il loop principale di `g2d`.

---

## Comandi di gioco

**Tastiera**

* `←` / `→` – Muovi Arthur a sinistra/destra
* `↑` – Salto (se a terra) / Sali sulle scale
* `↓` – Abbassati / Scendi dalle scale
* `1` – Lancia la torcia (attacco principale)
* `Esc` – Torna al menu principale durante la partita

**Mouse**

* `Click sinistro` – Seleziona i pulsanti del menu (Play, Quit)

---

## Regole di gioco

* Controlli **Arthur**, il cavaliere protagonista.
* Il mondo di gioco è una **mappa orizzontale** con:
  * piattaforme,
  * scale,
  * lapidi,
  * acqua (zone dannose),
  * una porta finale.
* Se raggiungi la **porta** alla fine del livello, la partita è **vinta** (fase `GAME_WON`).
* Se la vita di Arthur scende a zero o esce fuori dall’arena, la partita è **persa** (`GAME_OVER`).
* I nemici principali sono:
  * **Zombie**: emergono dal terreno, camminano e infliggono danni a contatto;
  * **Plant**: pianta fissa che spara proiettili (EyeBall);
  * **EyeBall**: proiettile lanciato dalle piante.
* Arthur può:
  * saltare tra piattaforme,
  * salire/scendere dalle scale,
  * abbassarsi,
  * lanciare torce per eliminare i nemici (con cooldown).

A schermo sono visibili:
* barra della **vita**,
* barra del **tempo di invincibilità** (quando attivo),
* barra del **cooldown d’attacco**.
* barra dell'**attraversamento** della porta finale.

---

## Struttura del progetto

La struttura semplificata è la seguente:

```text
data/
  textures/ ...
  settings.json
src/
  game/
    core/
      app.py
      game.py
      camera.py
      graphical_interface.py
      menu_manager.py
      file_management.py
    entities/
      actor.py
      player/arthur.py
      enemies/zombie.py, plant.py, ...
      objects/platform.py, ladder.py, gravestone.py, flame.py, door.py, ...
      weapons/torch.py, eyeball.py, ...
    gui/
      gui_component.py
      button.py
      bar.py
      text.py
      color.py
    state/
      sprite.py
      sprite_collection.py
      entity_state.py
      states.py
  main.py
tests/
  ...
```

### Core
* **`App` (`core/app.py`)**
  * Gestisce lo stato globale dell’applicazione (`Phase`: MENU, START_GAME, PLAYING, GAME_WON, GAME_OVER, QUIT…).
  * Tiene il riferimento a:
    * `MenuManager` (menu),
    * `Game` (logica di gioco),
    * `GraphicalInterface` (rendering).
  * Il metodo `tick()` smista il flusso:
    * al menu,
    * alla creazione di una nuova partita (`load_game`),
    * all’aggiornamento della partita (`play_game`),
    * alle schermate di vittoria/sconfitta.
* **`Game` (`core/game.py`)**
  * Estende `Arena` e rappresenta il **mondo di gioco**.
  * Contiene:
    * lo **sfondo** (`Sprite`),
    * la **lista degli attori**,
    * il **giocatore** (`player`),
    * la **coda di spawn** iniziale (`spawn_queue`),
    * la **fase di gioco** (`game_phase`).
  * Si occupa di:
    * tick di tutti gli attori,
    * controlli su vittoria/sconfitta,
    * gestione e registrazione di **collision handler**,
    * spawn casuale di **Zombie** e **Plant** (in base a parametri di configurazione).
* **`Camera` (`core/camera.py`)**
  * Segue il giocatore mantenendolo approssimativamente al centro/sinistra dello schermo.
  * Limita la vista ai bordi dell’arena.
* **`GraphicalInterface` (`core/graphical_interface.py`)**
  * Gestisce il **rendering**:
    * sfondo del mondo (`render_background`),
    * sprite di tutti gli attori (`render_sprites`),
    * componenti GUI (`render_guis`).
  * Usa `g2d` per disegnare immagini, rettangoli e testi.
  * Supporta lo “**sprite blinking**” quando Arthur è invincibile (con o senza `Pillow`).
* **`MenuManager` (`core/menu_manager.py`)**
  * Gestisce il **menu principale** e le schermate:
    * `MAIN` (Play/Quit),
    * `GAME_WON`,
    * `GAME_OVER`.
  * Per ogni fase associa una `GraphicalInterface` diversa.
  * Gestisce la durata delle schermate di vittoria/sconfitta con un **countdown**.

### Entities
* **Gerarchia di base**
  * `Actor`: interfaccia per tutti gli attori del gioco.
  * `Arena`: gestisce la collezione di attori e il loro aggiornamento.
* **Giocatore**
  * `Arthur`:
    * Stati: IDLE, WALKING, JUMPING, CROUCHING, CLIMBING, ATTACKING, ATTACKING_CROUCHED, DEAD…
    * Gestisce:
      * movimento con gravità,
      * salti,
      * scale,
      * invincibilità temporanea,
      * lancio di `Torch`.
* **Nemici**
  * `Zombie`:
    * stato EMERGING → WALKING → IMMERSING → DEAD,
    * spawna su piattaforme “valide” con `auto_init`,
    * infligge danno a contatto con Arthur,
    * ha una barra della vita disegnata sopra la testa.
  * `Plant`:
    * compare dal terreno (SPAWNING),
    * in IDLE carica l’attacco, poi passa ad ATTACKING,
    * spara proiettili `EyeBall` verso Arthur tramite `_shoot_eyeball`.
* **Oggetti e piattaforme**
  * `Platform`: blocchi statici su cui si cammina / si collide.
  * `Ladder`: scale utilizzate da Arthur per salire/scendere.
  * `GraveStone`: ostacoli sul terreno.
  * `Door`: porta finale; al passaggio di Arthur imposta lo stato di **vittoria**.
* **Armi / proiettili**
  * `Torch`: arma principale del giocatore.
  * `Flame`: effetto/arma collegata alla torcia.
  * `EyeBall`: proiettile lanciato dalla pianta.

### GUI
* `GUIComponent`: classe base per elementi di interfaccia.
* `Button`: pulsante con gestore di evento, stato hover/pressed e attivazione anche da mouse.
* `Bar`: barra generica parametrizzabile (colore, testo, valore, max, padding…).
  * Usata per:
    * barra della vita di Arthur,
    * barra di invincibilità,
    * barra del cooldown d’attacco,
    * barra dell'attraversamento della porta.
    * barre della vita di Zombie e Plant.
* `Text`, `Color`: supporto per testi e colori RGBA.

### State
* `Sprite`: rappresenta un riquadro in una texture (path, x, y, width, height, blinking…).
* `SpriteCollection`: mappa `(Action, Direction) → [Sprite]`, con metodi di utilità.
* `EntityState`: incapsula `Action` e `Direction`.
* `states.py`:
  * `Action`: enum delle azioni (WALKING, JUMPING, ATTACKING, SPAWNING, DEAD, …).
  * `Direction`: LEFT, RIGHT, UP, DOWN.
  * `Phase`: fasi dell’app (MENU, PLAYING, GAME_WON, GAME_OVER…).
  * `MenuPhase`: sotto-fasi del menu (MAIN, GAME_WON, GAME_OVER).

---

## Dati e configurazione
I parametri di gioco sono caricati tramite `file_management.read_settings()`, da un file di configurazione (es. JSON), che contiene:
* Parametri globali:
  * `camera_width`, `camera_height`
  * `scale`
  * `fps`
* Parametri per singole entità, ad esempio:
  * `Arthur.defaults` (velocità, gravità, vita massima, tempo di invincibilità, ecc.)
  * `Zombie.defaults` (vita, danni, probabilità di spawn, intervalli, ecc.)
  * `Plant.defaults` (vita, danni, probabilità di spawn, velocità dei proiettili…)
  * `EyeBall.defaults` (dimensioni, velocità, ecc.)

Questo approccio permette di modificare il bilanciamento del gioco senza cambiare il codice Python.

---

## Dettagli di implementazione
### Gestione delle collisioni
Nel `Game` sono registrati dizionari di **handler**:
* `_collision_handlers[(Tipo1, Tipo2)] = funzione`
* `_collision_free_handlers[(Tipo1, Tipo2)] = funzione`

La funzione `_handle_collisions()`:
1. Scorre tutte le coppie di attori.
2. Se c’è collisione:
   * cerca un handler registrato e lo invoca,
   * segna che per quella coppia di tipi è avvenuta una collisione.
3. Se **non** c’è collisione:
   * memorizza una coppia “esempio” per le non-collisioni, da usare poi una sola volta per frame.

Gli handler gestiscono logiche specifiche, ad esempio:
* `Arthur`–`Platform` → clamp della posizione, attivazione di `grounded`.
* `Arthur`–`Ladder` → abilita la salita/discesa e cambia lo stato in CLIMBING.
* `Arthur`–`Door` → vittoria.
* `Zombie`–`Platform` → gestione della camminata e cambi di direzione.
* `Torch`–nemici → applica danno e distrugge la torcia.
* `Flame`–nemici → applica danno.
* `Plant`–Arthur → danni a contatto con cooldown.

### Camera e rendering
* La `Camera` tiene traccia di `view_x`, `view_y` e dimensioni.
* `GraphicalInterface.render(game)`:
  1. pulisce il canvas (se richiesto),
  2. aggiorna la camera (`camera.tick(game)`),
  3. **disegna lo sfondo** in base alla posizione della camera,
  4. disegna gli **attori**:
     * Arthur è disegnato per ultimo, così rimane “sopra” agli altri sprite,
     * gestisce sprite “blinking” con o senza `Pillow`.
  5. disegna le **GUI** (sia globali che associate agli attori).

### Spawn dei nemici
* All’inizio, `spawn_queue` è riempita con:
  * Arthur,
  * piattaforme,
  * tombini, scale, acqua, porta, ecc.
* `Game.empty_queue()` spawna tutti gli attori, assicurandosi che Arthur sia in posizione 0.
* Ad ogni `tick`, con una certa probabilità (dal file di configurazione), vengono generati:
  * `Zombie` → tramite `Zombie.auto_init(player, game)` che:
    * trova piattaforme valide,
    * calcola range di spawn laterali rispetto ad Arthur,
    * sceglie casualmente un candidato tra quelli possibili.
  * `Plant` → tramite `Plant.auto_init(player, game, ...)` con logica simile.

Per motivi di performance, il gioco elimina:
* attori morti o fuori dall’arena,
* attori troppo lontani da Arthur (oltre una certa distanza).

---

## Testing
Il progetto include circa **5000 righe di codice** (esclusi i test) e una sezione dedicata ai test automatici con unittest.

I test verificano soprattutto:
* **GameTest**
  * stato iniziale del `Game` (fase, background, handler di collisione);
  * corretto comportamento di metodi di utilità (`inside_arena`, `distance`, `empty_queue`);
  * registrazione simmetrica di collision e collision-free handler;
  * logica generica del danno (`_generic_damage`);
  * gestione delle collisioni specifiche (Arthur-Platform, Arthur-Ladder, Arthur-Door);
  * orchestrazione delle collisioni tramite `_handle_collisions`.

* **GraphicalInterfaceTest**
  * creazione e validazione della `Camera` di default;
  * gestione della lista di componenti GUI (add/remove/insert, controlli di tipo);
  * rendering del background (colore o sprite);
  * raccolta e rendering dei componenti GUI legati agli attori;
  * pipeline di rendering completa (`render` → `camera.tick`, `render_background`, `render_sprites`, `render_guis`).

* **PlantTest**
  * inizializzazione di `Plant` (vita, danno, cooldown, stato, sprite);
  * clamp della salute e gestione dello stato `DEAD`;
  * macchina a stati di `move` (SPAWNING → IDLE → ATTACKING, gestione cooldown, direzione verso il player, sparo del proiettile);
  * gestione di `hit`, collisioni con Arthur e con le piattaforme;
  * generazione della barra vita (`gui`);
  * funzionamento di `_shoot_eyeball` e posizionamento corretto del proiettile;
  * logica di `auto_init` (scelta della piattaforma e del candidato di spawn).

* **ZombieTest**
  * inizializzazione di `Zombie` e del suo `EntityState`;
  * gestione della salute (clamp, passaggio a `DEAD`, reset distanza di cammino);
  * GUI (barra vita);
  * posizione e dimensioni (`pos`, `size`);
  * macchina a stati di `move` (EMERGING → WALKING → IMMERSING → DEAD);
  * sprite visibile solo negli stati vivi;
  * collisioni con Arthur (in base allo stato e al cooldown di attacco);
  * collisioni con le piattaforme (aggiornamento posizione, direzione, grounded);
  * logica di `auto_init` analoga a quella del `Plant`.

* **PlatformTest**
  * inizializzazione di `Platform` (posizione, dimensione, superfici di contatto di default);
  * validazione dei tipi per tutte le proprietà;
  * implementazione dell’interfaccia `Actor` (`pos`, `size`, `move`, `sprite`);
  * rilevamento collisioni (`check_collision`) e casi limite (solo bordo);
  * logica di `clamp` (direzione di collisione, rispetto delle `contact_surfaces`).

* **ArthurTest**
  * inizializzazione di `Arthur` e utilizzo dei valori di default;
  * clamp della salute, controlli di tipo su coordinate e health;
  * metodi di posizione/dimensione;
  * logica di `move` in diversi casi:
    * personaggio morto (nessun movimento),
    * movimento orizzontale (ArrowRight),
    * salto (ArrowUp),
    * combinazioni ArrowRight + ArrowUp in differenti stati (terra, aria, scala);
  * lancio della `Torch` (uso del tasto `1`, cooldown, impossibilità di lancio su scala);
  * gestione sprite e blinking in base all’invincibilità;
  * barra della vita (`gui`) collegata dinamicamente alla salute;
  * `hit` (danno e invincibilità);
  * collisioni con piattaforme (grounded, laddered, velocità orizzontale/verticale);
  * interazione con le scale (entrata/uscita dallo stato `laddered`);
  * metodi di supporto per il ciclo sprite.

* **EyeBallTest**
  * inizializzazione di `EyeBall` (stato ATTACKING, direzione, sprite, dimensioni);
  * movimento verso destra/sinistra e accumulo di `travelled_distance`;
  * passaggio allo stato `DEAD` superata la distanza massima;
  * nessun movimento quando è `DEAD`;
  * sprite nullo in stato `DEAD`;
  * `hit` che porta sempre a `DEAD`;
  * validazione dei tipi per le proprietà (`x`, `damage`, distanze).

* **TorchTest**
  * inizializzazione di `Torch` (danno, velocità, gravità, stato, direzione, velocità iniziali);
  * movimento balistico (velocità orizzontale + gravità);
  * nessun movimento in stato `DEAD`;
  * sprite nullo in stato `DEAD`;
  * collisioni con le piattaforme:
    * da sopra (UP): clamp, spawn della `Flame`, morte della Torch;
    * laterali: solo morte della Torch, senza spawn di `Flame`;
  * `hit` che imposta sempre lo stato a `DEAD`;
  * controlli di tipo per `x`, `y_step`, `damage`.

### Come eseguire i test
Dalla root del progetto:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
