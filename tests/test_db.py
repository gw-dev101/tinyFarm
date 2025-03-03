import sqlite3
import pytest
from datetime import date, datetime, timedelta

@pytest.fixture
def db_conn():
    """Créer une BDD SQLite dans la mémoire"""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

@pytest.fixture
def setup_db(db_conn):
    """Créer les différentes tables pour chaque test"""
    cur = db_conn.cursor()
    cur.execute("""
        CREATE TABLE Ferme (
            idFerme INTEGER PRIMARY KEY AUTOINCREMENT,
            nom VARCHAR(40) UNIQUE CHECK (LENGTH(nom) >= 3) NOT NULL,
            ecus DECIMAL(10,2) DEFAULT 1500 CHECK (ecus >= 0) NOT NULL,
            enHibernation DATE,
            achatRestant SMALLINT DEFAULT 12 CHECK (achatRestant >= 0) NOT NULL,
            dernierAchat DATE
        );
    """)
    cur.execute("""
        CREATE TABLE Compte (
            idCompte INTEGER PRIMARY KEY AUTOINCREMENT,
            idFerme INTEGER UNIQUE REFERENCES Ferme(idFerme),
            pseudo VARCHAR(40) UNIQUE CHECK (LENGTH(pseudo) >= 3) NOT NULL,
            derniereConnexion TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE Poule (
            idPoule INTEGER PRIMARY KEY AUTOINCREMENT,
            proprietaire INTEGER REFERENCES Ferme(idFerme),
            poids DECIMAL(5,2) DEFAULT 0.05 CHECK (poids >= 0) NOT NULL,
            age INTEGER DEFAULT 0 CHECK (age >= 0),
            sexe CHAR(1) CHECK (sexe IN ('M', 'F', 'U')) NOT NULL,   -- U pour Unknown
            nb_oeuf INTEGER DEFAULT 0 CHECK (nb_oeuf >= 0) NOT NULL,
            dernier_repas DATE,
            dernier_breuvage DATE,
            dernier_lavage DATE,
            malade_depuis DATE
        );
    """)

    cur.execute("""
        CREATE TABLE Clapier (
            proprietaire INTEGER PRIMARY KEY REFERENCES Ferme(idFerme),
            dernier_repas DATE,
            dernier_breuvage DATE,
            dernier_lavage DATE,
            malade_depuis DATE,
            nb_bebe INTEGER DEFAULT 8 CHECK (nb_bebe >= 0) NOT NULL,
            nb_petit INTEGER DEFAULT 0 CHECK (nb_petit >= 0) NOT NULL,
            nb_gros INTEGER DEFAULT 0 CHECK (nb_gros >= 0) NOT NULL,
            nb_adulte_m INTEGER DEFAULT 0 CHECK (nb_adulte_m >= 0) NOT NULL,
            nb_adulte_f INTEGER DEFAULT 0 CHECK (nb_adulte_f >= 0) NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE Vache (
            proprietaire INTEGER PRIMARY KEY REFERENCES Ferme(idFerme),
            poids INTEGER DEFAULT 1 CHECK (poids >= 0) NOT NULL,
            age INTEGER DEFAULT 0 CHECK (age >= 0) NOT NULL,
            qt_lait INTEGER DEFAULT 0 CHECK (qt_lait >= 0) NOT NULL,
            dernier_repas DATE,
            dernier_breuvage DATE,
            dernier_lavage DATE,
            malade_depuis DATE
        );
    """)
    cur.execute("""
        CREATE TABLE Produit (
            idProduit INTEGER PRIMARY KEY AUTOINCREMENT,
            nom VARCHAR(40) UNIQUE CHECK (LENGTH(nom) >= 2) NOT NULL,
            description VARCHAR(180),
            estVendable BOOLEAN NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE Commerce (
            idTransac INTEGER PRIMARY KEY AUTOINCREMENT,
            idAcheteur INTEGER REFERENCES Ferme(idFerme),
            idVendeur INTEGER REFERENCES Ferme(idFerme),
            produit INTEGER REFERENCES Produit(idProduit),
            quantite INTEGER CHECK (quantite >= 1) NOT NULL,
            prixUnitaire DECIMAL(10,2) CHECK (prixUnitaire > 0) NOT NULL,
            enVenteDepuis TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE Remise (
            idProduit INTEGER PRIMARY KEY AUTOINCREMENT,
            proprietaire INTEGER REFERENCES Ferme(idFerme),
            type INTEGER REFERENCES Produit(idProduit),
            quantite INTEGER NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE Classement (
            idFerme INTEGER PRIMARY KEY REFERENCES Ferme(idFerme),
            score DECIMAL(10,2)
        );
    """)
    db_conn.commit()
    cur.close()

@pytest.fixture
def setup_ferme(db_conn, setup_db):
    """Donnéee d'exemple pour la table Ferme"""
    # Exemple pour insérer plusieurs données
    nomFerme = ['Marguerite et Pissenlit', 'Tégrité']
    ids = []

    cur = db_conn.cursor()
    for nom in nomFerme:
        cur.execute("INSERT INTO Ferme (nom) VALUES (?) RETURNING idFerme", (nom,))
        ids.append(cur.fetchone()[0])
    
    db_conn.commit()
    cur.close()
    return ids

@pytest.fixture
def setup_poule(db_conn, setup_ferme):
    """Donnée d'exemple pour la table Poule"""
    # Exemple pour insérer une unique donnée
    cur = db_conn.cursor()
    cur.execute("""
                INSERT INTO Poule (proprietaire, poids, age, sexe, nb_oeuf, dernier_repas, dernier_breuvage, dernier_lavage)
                VALUES (?, 2.5, 5, 'F', 1, ?, ?, '2025-02-26') RETURNING idPoule
            """, (setup_ferme[0], date.today(), date.today() - timedelta(days=1)))
    pouleId = cur.fetchone()[0]
    db_conn.commit()
    cur.close()
    return pouleId

@pytest.fixture
def setup_vache(db_conn, setup_ferme):
    """Donnée d'exemple pour la table Vache"""
    # Exemple pour insérer une unique donnée
    cur = db_conn.cursor()
    cur.execute("""
                INSERT INTO Vache (proprietaire, poids, age, qt_lait, dernier_repas, dernier_breuvage, dernier_lavage)
                VALUES (?, 1, 1, 0, ?, ?, ?)
            """, (setup_ferme[0], date.today(), date.today(), date.today()))
    cur.execute("""
                INSERT INTO Vache (proprietaire, poids, age, qt_lait, dernier_repas, dernier_breuvage, dernier_lavage)
                VALUES (?, 100, 19, 8, ?, ?, ?)
            """, (setup_ferme[1], date.today(), date.today(), date.today()))
    db_conn.commit()
    cur.close()

@pytest.fixture
def setup_clapier(db_conn, setup_ferme):
    """Donnée d'exemple pour la table Clapier"""
    # Exemple pour insérer une unique donnée
    cur = db_conn.cursor()
    cur.execute("""
                INSERT INTO Clapier (proprietaire, dernier_repas, dernier_breuvage, dernier_lavage, nb_bebe, nb_petit, nb_gros, nb_adulte_m, nb_adulte_f)
                VALUES (?, ?, ?, ?, 20, 14, 6, 5, 25)
            """, (setup_ferme[0], date.today(), date.today() - timedelta(days=1),  date.today()))
    cur.execute("""
                INSERT INTO Clapier (proprietaire, dernier_repas, dernier_breuvage, dernier_lavage, nb_bebe, nb_petit, nb_gros, nb_adulte_m, nb_adulte_f)
                VALUES (?, ?, ?, ?, 20, 20, 0, 0, 10)
            """, (setup_ferme[1], date.today(), date.today() - timedelta(days=1),  date.today()))
    db_conn.commit()
    cur.close()





def test_creation_ferme(db_conn, setup_db):
    cur = db_conn.cursor()
    cur.execute("INSERT INTO Ferme (nom) VALUES ('Test')")
    ferme_id = cur.lastrowid

    cur.execute("SELECT nom, ecus, enHibernation, achatRestant, dernierAchat FROM Ferme WHERE idFerme = ?;", (ferme_id,))
    result = cur.fetchone()

    cur.close()
    assert result == ("Test", 1500, None, 12, None)
""""""""""""""""""""""""""""""""#partie 2


def test_creation_produit(db_conn, setup_db):
    cur = db_conn.cursor()
    cur.execute("INSERT INTO Produit (nom, description, estVendable) VALUES ('Laine', 'La laine de mouton', 1)")
    produit_id = cur.lastrowid
    
    cur.execute("SELECT nom, description, estVendable FROM Produit WHERE idProduit = ?;", (produit_id,))
    result = cur.fetchone()
    
    cur.close()
    assert result == ("Laine", "La laine de mouton", 1)#le produit est bien créé

def test_creation_remise(db_conn, setup_db, setup_ferme):
    """Test de la création d'une remise associée à un produit et une ferme"""
    cur = db_conn.cursor()
    
    # Créer un produit
    cur.execute("INSERT INTO Produit (nom, description, estVendable) VALUES ('Maïs', 'Maïs biologique', 1)")
    produit_id = cur.lastrowid
    
    # Associer une remise à la ferme
    cur.execute("INSERT INTO Remise (proprietaire, type, quantite) VALUES (?, ?, 100)", (setup_ferme[0], produit_id))
    
    cur.execute("SELECT proprietaire, type, quantite FROM Remise WHERE proprietaire = ?", (setup_ferme[0],))
    result = cur.fetchone()
    
    cur.close()
    assert result == (setup_ferme[0], produit_id, 100)


def test_creation_commerce(db_conn, setup_db, setup_ferme):
    """Test de la création d'une transaction de commerce entre fermes"""
    cur = db_conn.cursor()
    
    # Créer un produit
    cur.execute("INSERT INTO Produit (nom, description, estVendable) VALUES ('Blé', 'Blé de qualité supérieure', 1)")
    produit_id = cur.lastrowid

    # Créer une transaction de commerce
    cur.execute("INSERT INTO Commerce (idAcheteur, idVendeur, produit, quantite, prixUnitaire, enVenteDepuis) VALUES (?, ?, ?, ?, ?, ?)",
                (setup_ferme[0], setup_ferme[1], produit_id, 50, 10.5, datetime.now()))
    
    cur.execute("SELECT idAcheteur, idVendeur, produit, quantite, prixUnitaire FROM Commerce WHERE idAcheteur = ?", (setup_ferme[0],))
    result = cur.fetchone()
    
    cur.close()
    assert result == (setup_ferme[0], setup_ferme[1], produit_id, 50, 10.5)


def test_creation_classement(db_conn, setup_db, setup_ferme):
    """Test de l'ajout d'un score dans le classement"""
    cur = db_conn.cursor()
    
    # Ajouter une ferme au classement
    cur.execute("INSERT INTO Classement (idFerme, score) VALUES (?, 98.5)", (setup_ferme[0],))
    
    cur.execute("SELECT idFerme, score FROM Classement WHERE idFerme = ?", (setup_ferme[0],))
    result = cur.fetchone()
    
    cur.close()
    assert result == (setup_ferme[0], 98.5)

if __name__ == "__main__":
    pytest.main(['-v', 'test.py'])