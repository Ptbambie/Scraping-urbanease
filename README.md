# Scraping de données et Base de Données PostgreSQL 

## Environnement Python

- J'ai installé Python 3.10 et pip en suivant les instructions fournies dans la documentation.

- J'ai utilisé les packages suivants :
    - `beautifulsoup4` pour analyser le HTML du site web.
    - `requests` pour effectuer des requêtes HTTP et récupérer le contenu.
    - `psycopg2-binary` pour me connecter à la base de données PostgreSQL.

## Structure du Projet

- J'ai organisé mon projet en utilisant les fichiers suivants :
    - `main.py` : Le fichier principal où j'ai écrit les étapes de scraping.
    - `conf.py` : Un fichier de configuration pour stocker des informations spécifiques au site, telles que l'URL du site, le nombre de pages à scraper, les départements à traiter, etc.
    - J'ai également créé un dossier `data` pour stocker les fichiers JSON résultants et un dossier `logs` pour les fichiers journaux.

## Collecte de Données

- J'ai identifié l'URL à requêter et généré les paramètres d'URL dynamiquement en fonction du département, de la rubrique et de la page à scraper en utilisant les informations du fichier de configuration.

- J'ai effectué des requêtes HTTP pour récupérer le contenu HTML de la page.

- J'ai utilisé BeautifulSoup pour repérer le bloc HTML contenant les annonces.

- J'ai itéré sur les annonces pour collecter les informations demandées, telles que le titre, l'URL, le prix, la surface, la ville et le code postal du bien à vendre.

## Base de Données PostgreSQL

- J'ai créé une base de données PostgreSQL locale en utilisant les commandes SQL suivantes :
    ```sql
    psql -U postgres
    CREATE DATABASE annonces_db;
    \c annonces_db
    CREATE TABLE annonces (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255),
        price INTEGER,
        url TEXT,
        city VARCHAR(255),
        surface INTEGER,
        postal_code VARCHAR(5)
    );
    \q
    ```

- J'ai connecté mon script Python à la base de données PostgreSQL et inséré les données extraites.

- J'ai mis en place une gestion des doublons d'annonces pour éviter de les insérer à nouveau.

## Output Attendu

Mon script génère plusieurs fichiers :
- `logfile.log` : Un fichier journal où je peux suivre les étapes de traitement du script, les données collectées et toute information pertinente.

- `resultats_{department}.json` : Des fichiers JSON contenant les données extraites par département.

J'ai suivi ces étapes pour accomplir cet exercice. Bonne lecture et n'hésitez pas à me contacter si vous avez des questions !
