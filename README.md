# EpicEvent

Python version 3.12.6

Poetry version 2.0.1

PostgreSQL 17

# C'est quoi
Epic Event est une application en ligne de commande (CLI) développée en Python pour gérer les clients, les contrats et les événements d'une entreprise organisatrice d'événements.

# Installation
Vous aurez besoin d'avoir PostgreSQL installé sur votre machine.
1. Clonez le dépôt ou télécharger une archive.
2. Rendez-vous depuis un terminal dans la racine du répertoire
   - Sur windows : clic-droit puis ouvrir dans le terminal.
   - Sur Mac : ouvrir un terminal puis glisser-déposer le dossier directement dans le terminal.
3. Installer poetry si vous le n'avez pas ```pip install poetry```
4. Créer l'environnement virtuel et installer les dépendances avec ```poetry install```
5. Activez l'environnement virtuel avec ```.venv\Scripts\activate.bat``` sous windows ou ```eval $(poetry env activate)``` sous macos ou linux. (au besoin https://python-poetry.org/docs/managing-environments/#activating-the-environment)
6. Remplissez le fichier .env vierge fourni
7. Tapez la commande ```epicevent init``` et suivez les instructions afin de paramètrer l'application.

# Commandes disponibles
Tout se faisant en ligne de commande il faudra toujours commencer par taper ```epicevent nomdelacommande```.

## Commandes CLI de `epicevent`

Cette section documente les commandes disponibles via la ligne de commande `epicevent`. Chaque commande est accompagnée d'une description et d'un exemple d'utilisation.

---

### `init`
Gère la clé secrète JWT, crée la base de données et les tables.

```bash
epicevent init
```

---

### `login`
Connecte l'utilisateur à l'application.

```bash
epicevent login
```

---

### `logout`
Déconnecte l'utilisateur.

```bash
epicevent logout
```

---

### `create-collaborator`
Crée un nouveau collaborateur.

```bash
epicevent create-collaborator
```

---

### `delete-collaborator`
Supprime un collaborateur existant.

```bash
epicevent delete-collaborator
```

---

### `create-client`
Crée un nouveau client.

```bash
epicevent create-client
```

---

### `get-clients`
Affiche tous les clients.

```bash
epicevent get-clients [OPTIONS]
```

**Options :**
- `--assigned` : Affiche uniquement les clients assignés à l'utilisateur connecté.

---

### `get-events`
Affiche tous les événements.

```bash
epicevent get-events [OPTIONS]
```

**Options :**
- `--assign [all|assigned|no-contact]` : Filtre les événements selon leur assignation.

---

### `get-contracts`
Affiche tous les contrats.

```bash
epicevent get-contracts [OPTIONS]
```

**Options :**
- `--status [signed|pending|cancelled]` : Filtre les contrats par statut.
- `--remaining-amount` : Affiche uniquement les contrats avec un montant restant.
- `--assigned` : Affiche uniquement les contrats assignés à l'utilisateur.

---

### `create-contract`
Crée un nouveau contrat.

```bash
epicevent create-contract
```

---

### `create-event`
Crée un nouvel événement.

```bash
epicevent create-event
```

---

### `update-client`
Met à jour les informations d'un client existant.

```bash
epicevent update-client
```

---

### `update-collaborator`
Met à jour les informations d'un collaborateur existant.

```bash
epicevent update-collaborator
```

---

### `update-contract`
Met à jour les informations d'un contrat existant.

```bash
epicevent update-contract
```

---

### `update-event`
Met à jour les informations d'un événement existant.

```bash
epicevent update-event
```


# Schéma base de données
![Database schema](assets/bdd_schema.png)
