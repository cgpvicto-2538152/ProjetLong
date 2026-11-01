DROP DATABASE IF EXISTS projet_long;

CREATE DATABASE IF NOT EXISTS projet_long CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE projet_long;

DROP TABLE IF EXISTS Clients;

CREATE TABLE Clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL,
    num_telephone VARCHAR(25) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

DROP TABLE IF EXISTS Status_commandes;

CREATE TABLE Status_commandes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    statut_nom VARCHAR(255) NOT NULL UNIQUE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

DROP TABLE IF EXISTS Commandes;

CREATE TABLE Commandes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    statut_id INT NOT NULL,
    adresse_livraison VARCHAR(255) NOT NULL,
    date_commande DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES Clients (id) ON DELETE CASCADE,
    FOREIGN KEY (statut_id) REFERENCES Status_commandes (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

DROP TABLE IF EXISTS Type_croutes;

CREATE TABLE Type_croutes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    croute_nom VARCHAR(255) NOT NULL UNIQUE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

DROP TABLE IF EXISTS Type_sauces;

CREATE TABLE Type_sauces (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sauce_nom VARCHAR(255) NOT NULL UNIQUE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

DROP TABLE IF EXISTS Type_garnitures;

CREATE TABLE Type_garnitures (
    id INT PRIMARY KEY AUTO_INCREMENT,
    garniture_nom VARCHAR(255) NOT NULL UNIQUE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

DROP TABLE IF EXISTS Pizzas;

CREATE TABLE Pizzas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    croute_id INT NOT NULL,
    sauce_id INT NOT NULL,
    commande_id INT NOT NULL,
    FOREIGN KEY (croute_id) REFERENCES Type_croutes (id),
    FOREIGN KEY (sauce_id) REFERENCES Type_sauces (id),
    FOREIGN KEY (commande_id) REFERENCES Commandes (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

DROP TABLE IF EXISTS Pizzas_garnitures;

CREATE TABLE Pizzas_garnitures (
    pizza_id INT NOT NULL,
    garniture_id INT NOT NULL,
    PRIMARY KEY (pizza_id, garniture_id),
    FOREIGN KEY (pizza_id) REFERENCES Pizzas (id) ON DELETE CASCADE,
    FOREIGN KEY (garniture_id) REFERENCES Type_garnitures (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

DROP TRIGGER IF EXISTS trg_commandes_statut_initial;

DELIMITER $$

CREATE TRIGGER trg_commandes_statut_initial
BEFORE INSERT ON Commandes
FOR EACH ROW
BEGIN
    DECLARE _statut_id INT DEFAULT NULL;

    DECLARE CONTINUE HANDLER FOR NOT FOUND
        SET _statut_id = NULL;

    SELECT id INTO _statut_id
    FROM Status_commandes
        WHERE statut_nom = 'En attente'
    LIMIT 1;

    IF _statut_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Le statut En attente est introuvable.';
    END IF;

    SET NEW.statut_id = _statut_id;
END$$

DELIMITER;
