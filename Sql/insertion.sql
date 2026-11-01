USE projet_long;

INSERT INTO
    Status_commandes (statut_nom)
VALUES ('En attente'),
    ('Livrée');

INSERT INTO
    Type_croutes (croute_nom)
VALUES ('Classique'),
    ('Mince'),
    ('Épaisse');

INSERT INTO
    Type_sauces (sauce_nom)
VALUES ('Tomate'),
    ('Spaghetti'),
    ('Alfredo');

INSERT INTO
    Type_garnitures (garniture_nom)
VALUES ('Pepperoni'),
    ('Champignons'),
    ('Oignons'),
    ('Poivrons'),
    ('Olives'),
    ('Anchois'),
    ('Bacon'),
    ('Poulet'),
    ('Maïs'),
    ('Fromage'),
    ('Piments forts');

-- pour test

INSERT INTO
    Clients (nom, num_telephone)
VALUES (
        'Jean Tremblay',
        '819-555-0101'
    ),
    (
        'Marie Gagnon',
        '819-555-0102'
    ),
    ('Alex Roy', '819-555-0103');

-- Statut 1 = En attente
-- Statut 2 = Livrée
-- Commandes
INSERT INTO
    Commandes (client_id, adresse_livraison)
VALUES (
        1,
        '123 Rue Principale, Victoriaville'
    ),
    (
        2,
        '456 Rue Notre-Dame, Victoriaville'
    ),
    (
        3,
        '789 Boulevard des Bois-Francs, Victoriaville'
    );
-- Croûte : 1 = Classique, 2 = Mince, 3 = Épaisse
-- Sauce : 1 = Tomate, 2 = Spaghetti, 3 = Alfredo
INSERT INTO
    Pizzas (
        croute_id,
        sauce_id,
        commande_id
    )
VALUES (1, 1, 1),
    (2, 3, 1),
    (3, 1, 2),
    (1, 2, 3);

UPDATE Commandes
SET
    statut_id = (
        SELECT id
        FROM Status_commandes
        WHERE
            statut_nom = 'Livrée'
    )
WHERE
    id = 3;
-- Pizza 1 : Pepperoni, Champignons, Oignons
-- Pizza 2 : Poulet, Bacon, Fromage, Maïs
-- Pizza 3 : Pepperoni, Poivrons
-- Pizza 4 : Olives, Anchois, Piments forts
INSERT INTO
    Pizzas_garnitures (pizza_id, garniture_id)
VALUES
    --
    (1, 1),
    (1, 2),
    (1, 3),
    --
    (2, 7),
    (2, 8),
    (2, 9),
    (2, 10),
    --
    (3, 1),
    (3, 4),
    --
    (4, 5),
    (4, 6),
    (4, 11);
