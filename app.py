import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request
import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

os.system("cls")

load_dotenv()

app = Flask(__name__)

# region Fonctions

def connection_bd() -> Any:
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=os.getenv('DB_PORT')
    )

# region Fonction récupération des données

def recuperer_croutes(connection: MySQLConnection) -> dict:
    croutes = {}
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete: str = """
            SELECT id, croute_nom FROM Type_croutes ORDER BY croute_nom
        """
        cursor.execute(requete)

        for id_croute, nom_croute in cursor.fetchall():
            croutes[id_croute] = nom_croute

    except mysql.connector.Error:
        raise

    finally:
        if cursor is not None:
            cursor.close()

    return croutes


def recuperer_sauces(connection: MySQLConnection) -> dict:
    sauces = {}
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete: str = """
            SELECT id, sauce_nom FROM Type_sauces ORDER BY sauce_nom
        """
        cursor.execute(requete)

        for id_sauce, nom_sauce in cursor.fetchall():
            sauces[id_sauce] = nom_sauce

    except mysql.connector.Error:
        raise

    finally:
        if cursor is not None:
            cursor.close()

    return sauces


def recuperer_garnitures(connection: MySQLConnection) -> dict:
    garnitures = {}
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete: str = """
            SELECT id, garniture_nom FROM Type_garnitures ORDER BY garniture_nom
        """
        cursor.execute(requete)

        for id_garniture, nom_garniture in cursor.fetchall():
            garnitures[id_garniture] = nom_garniture

    except mysql.connector.Error:
        raise

    finally:
        if cursor is not None:
            cursor.close()

    return garnitures


def recuperer_client(connection: MySQLConnection, nom: str, telephone: str) -> dict | None:

    client = None
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete: str = """
            SELECT id, nom, num_telephone
            FROM Clients
            WHERE nom = %(nom)s AND num_telephone = %(telephone)s
            LIMIT 1
        """

        cursor.execute(requete, {'nom': nom,'telephone': telephone})

        resultat = cursor.fetchone()

        if resultat:
            client = {
                "id": resultat[0],
                "nom": resultat[1],
                "telephone": resultat[2]
            }

    except mysql.connector.Error:
        raise

    finally:
        if cursor is not None:
            cursor.close()

    return client


def recuperer_commandes_par_statut(connection: MySQLConnection) -> dict[str, list[dict]]:
    commandes = {}
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete: str = """
            SELECT Status_commandes.statut_nom, Commandes.id, Clients.nom, Clients.num_telephone, Commandes.adresse_livraison, Commandes.date_commande
            FROM Commandes
                INNER JOIN Clients ON Commandes.client_id = Clients.id
                INNER JOIN Status_commandes ON Commandes.statut_id = Status_commandes.id
            ORDER BY statut_nom, date_commande ASC, Commandes.id ASC
        """

        cursor.execute(requete)

        for statut, id_commande, nom, telephone, adresse, date_commande in cursor.fetchall():

            # Créer le statut seulement s'il n'existe pas déjà.
            if statut not in commandes:
                commandes[statut] = []

            commandes[statut].append({
                "id": id_commande,
                "nom": nom,
                "telephone": telephone,
                "adresse": adresse,
                "date": date_commande
            })

    except mysql.connector.Error:
        raise

    finally:
        if cursor is not None:
            cursor.close()

    return commandes


def recuperer_details_commande(connection: MySQLConnection, id_commande: int) -> dict | None:

    commande = None
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete: str = """
            SELECT Commandes.id, Clients.nom, Clients.num_telephone, Commandes.adresse_livraison, Commandes.date_commande, Status_commandes.statut_nom
            FROM Commandes
                INNER JOIN Clients ON Commandes.client_id = Clients.id
                INNER JOIN Status_commandes ON Commandes.statut_id = Status_commandes.id
            WHERE Commandes.id = %(id_commande)s
        """

        cursor.execute(requete, {'id_commande': id_commande})

        resultat = cursor.fetchone()

        if resultat:
            commande = {
                "id": resultat[0],
                "nom": resultat[1],
                "telephone": resultat[2],
                "adresse": resultat[3],
                "date": resultat[4],
                "statut": resultat[5]
            }

    except mysql.connector.Error:
        raise

    finally:
        if cursor is not None:
            cursor.close()

    return commande


def recuperer_pizzas_commande(connection: MySQLConnection, id_commande: int) -> list[dict]:

    pizzas = {}
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete: str = """
            SELECT Pizzas.id, Type_croutes.croute_nom, Type_sauces.sauce_nom, Type_garnitures.garniture_nom
            FROM Pizzas
                INNER JOIN Type_croutes ON Pizzas.croute_id = Type_croutes.id
                INNER JOIN Type_sauces ON Pizzas.sauce_id = Type_sauces.id
                LEFT JOIN Pizzas_garnitures ON Pizzas.id = Pizzas_garnitures.pizza_id
                LEFT JOIN Type_garnitures ON Pizzas_garnitures.garniture_id = Type_garnitures.id
            WHERE Pizzas.commande_id = %(id_commande)s
            ORDER BY Pizzas.id, Type_garnitures.garniture_nom
        """

        cursor.execute(requete, {'id_commande': id_commande})

        for id_pizza, croute, sauce, garniture in cursor.fetchall():

            # Ajoute la pizza seulement si n'est pas dans le dict.
            if id_pizza not in pizzas:
                pizzas[id_pizza] = {
                    "id": id_pizza,
                    "croute": croute,
                    "sauce": sauce,
                    "garnitures": []
                }

            # Ajoute la garniture seulement si existe.
            if garniture is not None:
                pizzas[id_pizza]["garnitures"].append(garniture)

    except mysql.connector.Error:
        raise

    finally:
        if cursor is not None:
            cursor.close()

    return list(pizzas.values())

# endregion Fonction récupration des données


# region Fonction insertion des données

def ajouter_client(connection: MySQLConnection, nom: str, telephone: str) -> int:
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete = """
            INSERT INTO Clients (nom, num_telephone)
            VALUES (%(nom)s, %(telephone)s)
        """

        cursor.execute(requete, {'nom': nom, 'telephone': telephone})

        id_client = cursor.lastrowid

        if id_client is None:
            raise Exception("Impossible de récupérer l'identifiant du client.")

        return id_client

    finally:
        if cursor is not None:
            cursor.close()


def ajouter_commande(connection: MySQLConnection, id_client: int, adresse: str) -> int:
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete = """
            INSERT INTO Commandes (client_id, adresse_livraison)
            VALUES (%(id_client)s, %(adresse)s)
        """

        cursor.execute(requete, {'id_client': id_client,'adresse': adresse})

        id_commande = cursor.lastrowid

        if id_commande is None:
            raise Exception("Impossible de récupérer l'identifiant de la commande.")

        return id_commande

    finally:
        if cursor is not None:
            cursor.close()


def ajouter_pizza(connection: MySQLConnection, id_commande: int, id_croute: int, id_sauce: int) -> int:
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete = """
            INSERT INTO Pizzas (commande_id, croute_id, sauce_id)
            VALUES (%(id_commande)s, %(id_croute)s, %(id_sauce)s)
        """

        cursor.execute(requete, {'id_commande': id_commande,'id_croute': id_croute,'id_sauce': id_sauce})

        id_pizza = cursor.lastrowid

        if id_pizza is None:
            raise Exception("Impossible de récupérer l'identifiant de la pizza.")

        return id_pizza

    finally:
        if cursor is not None:
            cursor.close()


def ajouter_garnitures(connection: MySQLConnection, id_pizza: int, id_garnitures: list[int] ) -> None:
    if len(id_garnitures) > 4:
        raise ValueError("Une pizza ne peut pas avoir plus de quatre garnitures.")

    # set garde se qui est unique, vérifie tout est unique et donc meme longueur apres le set()
    if len(id_garnitures) != len(set(id_garnitures)):
        raise ValueError("Une garniture ne peut pas être ajoutée plusieurs fois.")

    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete = """
            INSERT INTO Pizzas_garnitures (pizza_id, garniture_id)
            VALUES (%(id_pizza)s, %(id_garniture)s)
        """

        for id_garniture in id_garnitures:
            cursor.execute(requete, {'id_pizza': id_pizza,'id_garniture': id_garniture})

    finally:
        if cursor is not None:
            cursor.close()


def ajouter_commande_complete(connection: MySQLConnection, nom: str, telephone: str, adresse: str, pizzas: list[dict] ) -> int:

    try:
        connection.start_transaction()

        client = recuperer_client(connection, nom, telephone)

        if client is None:
            id_client = ajouter_client(connection, nom, telephone)
        else:
            id_client = client['id']

        id_commande = ajouter_commande(connection, id_client, adresse)

        for pizza in pizzas:
            id_pizza = ajouter_pizza(
                connection,
                id_commande,
                pizza['id_croute'],
                pizza['id_sauce']
            )

            ajouter_garnitures(
                connection,
                id_pizza,
                pizza.get('garnitures', [])
            )

        connection.commit()

        return id_commande

    except Exception:
        connection.rollback()
        raise

# endregion Fonction insertion des données


# region Fonction update de données

def completer_livraison(connection: MySQLConnection, id_commande: int) -> None:
    cursor: MySQLCursor | None = None

    try:
        cursor = connection.cursor()

        requete = """
            UPDATE Commandes
            SET statut_id = (
                SELECT id
                FROM Status_commandes
                WHERE statut_nom = 'Livrée'
            )
            WHERE id = %(id_commande)s
        """

        cursor.execute(requete, {'id_commande': id_commande})

        if cursor.rowcount == 0:
            # valide si sa fonctionne, sinon crée une erreur
            raise ValueError("Commande introuvable.")

    finally:
        if cursor is not None:
            cursor.close()

# endregion Fonction update de données

# endregion Fonctions


# region Routes

@app.route('/')
def afficher_index() -> str:
    return render_template('index.html')


# region Commandes

def recuperer_commande_formulaire(formulaire) -> dict:
    nom = formulaire.get('nom', '').strip()
    telephone = formulaire.get('telephone', '').strip()
    adresse = formulaire.get('adresse', '').strip()

    if not nom or not telephone:
        raise ValueError("Informations du client invalides.")

    try:
        nombre_pizzas = int(formulaire.get('nombre_pizzas', 0))

        if nombre_pizzas < 1:
            raise ValueError("La commande doit contenir au moins une pizza.")

        pizzas = []

        for i in range(nombre_pizzas):

            id_croute = int(formulaire[f'pizzas[{i}][croute]'])
            id_sauce = int(formulaire[f'pizzas[{i}][sauce]'])

            id_garnitures = [
                int(id) for id in formulaire.getlist(f'pizzas[{i}][garnitures]')
            ]

            if len(id_garnitures) > 4:
                raise ValueError("Maximum de 4 garnitures par pizza.")

            if len(id_garnitures) != len(set(id_garnitures)):
                raise ValueError("Garnitures en double.")

            pizzas.append({
                'id_croute': id_croute,
                'id_sauce': id_sauce,
                'garnitures': id_garnitures
            })

    except (ValueError, TypeError, KeyError) as erreur:
        raise ValueError("Données de commande invalides.") from erreur

    return {
        'nom': nom,
        'telephone': telephone,
        'adresse': adresse,
        'pizzas': pizzas
    }


@app.route('/commande', methods=['GET', 'POST'])
def afficher_commande():

    if request.method == 'GET':
        connection = connection_bd()

        try:
            croutes = recuperer_croutes(connection)
            sauces = recuperer_sauces(connection)
            garnitures = recuperer_garnitures(connection)

        finally:
            connection.close()

        return render_template('commande.html', croutes=croutes, sauces=sauces, garnitures=garnitures, erreur=request.args.get('erreur'))

    try:
        commande = recuperer_commande_formulaire(request.form)

    except ValueError:
        return redirect('/commande?erreur=1')

    connection = connection_bd()

    try:
        croutes = recuperer_croutes(connection)
        sauces = recuperer_sauces(connection)
        garnitures = recuperer_garnitures(connection)

    finally:
        connection.close()

    return render_template('resume_commande.html', commande=commande, croutes=croutes, sauces=sauces, garnitures=garnitures)

@app.route('/commande/confirmer', methods=['POST'])
def confirmer_commande():

    try:
        commande = recuperer_commande_formulaire(request.form)

    except ValueError:
        return redirect('/commande?erreur=1')

    connection = None

    try:
        connection = connection_bd()

        ajouter_commande_complete(
            connection,
            commande['nom'],
            commande['telephone'],
            commande['adresse'],
            commande['pizzas']
        )

    except Exception as erreur:
        print(f"Erreur lors de la création de la commande : {erreur}")
        return redirect('/commande?erreur=1')

    finally:
        if connection is not None:
            connection.close()

    return redirect('/?commande=confirmee')

# endregion Commandes

# region Livraisons

@app.route('/livraisons', methods=['GET'])
def afficher_livraisons():

    connection = None
    commandes = {}
    erreur = request.args.get('erreur')

    try:
        connection = connection_bd()
        commandes = recuperer_commandes_par_statut(connection)

    except Exception as erreur:
        print(f"Erreur lors de la récupération des livraisons : {erreur}")
        erreur = True

    finally:
        if connection is not None:
            connection.close()

    return render_template(
        'livraisons.html',
        commandes_attente=commandes.get('En attente', []),
        commandes_terminees=commandes.get('Livrée', []),
        erreur=erreur,
        terminee=request.args.get('terminee')
    )


@app.route('/livraison/terminer/<int:id_commande>', methods=['POST'])
def terminer_livraison(id_commande):
    connection = None
    try:
        connection = connection_bd()
        completer_livraison(connection, id_commande)
        connection.commit()

    except Exception as erreur:
        print(f"Erreur lors de la finalisation de la livraison : {erreur}")

        if connection is not None:
            connection.rollback()

        return redirect('/livraisons?erreur=1')

    finally:
        if connection is not None:
            connection.close()

    return redirect('/livraisons?terminee=1')

# endregion Livraisons

# endregion Routes

print("http://127.0.0.1:5000/")

if __name__ == '__main__':
    app.run(debug=True)


# Tests
# connection: MySQLConnection = connection_bd()
# resultat = recuperer_croutes(connection)
# print(resultat)

# connection: MySQLConnection = connection_bd()
# resultat = recuperer_sauces(connection)
# print(resultat)

# connection: MySQLConnection = connection_bd()
# resultat = recuperer_garnitures(connection)
# print(resultat)

# connection = connection_bd()
# print(recuperer_details_commande(connection, 1))

# connection = connection_bd()
# print(recuperer_pizzas_commande(connection, 1))

# connection = connection_bd()
# print(recuperer_commandes_par_statut(connection))
