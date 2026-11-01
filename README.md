# Pizzeria

Projet long de gestion de pizzeria.

## Configuration

Le fichier `.env` à la racine utilise les variables suivantes :

```
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_PORT=
```

## Fonctionnement

L'application comporte deux sections :

- **Nouvelle commande** : Saisir les informations du client, vérifier s'il existe déjà dans la base de données ou en créer un nouveau, choisir les pizzas et confirmer la commande.
- **Gestion des livraisons** : Consulter les commandes en attente et marquer les livraisons comme terminées.
