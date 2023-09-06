import os
import requests
import logging
from bs4 import BeautifulSoup
import psycopg2
import json
from urllib.parse import urlparse
from conf import DB_NAME, USER, PASSWORD, HOST, SITE_URL, NUM_PAGES, DEPARTMENTS, CATEGORIES


import time 

# Configuration du dossier pour les fichiers JSON
data_folder = os.path.join(os.path.dirname(__file__), 'data')

# Création du dossier data
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Configuration du dossier pour les fichiers logs
logs_folder = os.path.join(os.path.dirname(__file__), 'logs')

# Création du dossier logs
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)

# Configuration du journal
logging.basicConfig(filename=os.path.join(logs_folder, 'logfile.log'), level=logging.INFO)
logger = logging.getLogger()

# Définissez les informations de connexion à la base de données (à partir du fichier conf.py)
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST
)

# curseur pour exécuter des requêtes SQL
cur = conn.cursor()

# Fonction pour insérer une annonce dans la base de données
def insert_announcement(data):
    try:
        cur.execute("""
            INSERT INTO annonces (title, price, url, city, surface, postal_code)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['title'], data['price'], data['url'], data['city'], data['surface'], data['postal_code']))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Erreur lors de l'insertion de l'annonce : {str(e)}")

# Fonction pour générer l'URL
def generate_url(department, category, page):
    category = category.replace(' ', '-')
    return f"{SITE_URL}/?page={page}&dpt={department}&cat={category}"

# Fonction pour récupérer le contenu de la page HTML
def get_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f'Erreur {response.status_code} lors de la requête sur l\'url {url}')
        return None

# Fonction pour nettoyer le prix en tant qu'entier
def clean_price(price_str):
    try:
        # Supprime les caractères non numériques de la chaîne
        cleaned_price = ''.join(filter(str.isdigit, price_str))
        # Converti la chaîne nettoyée en entier
        price_int = int(cleaned_price)
        return price_int
    except ValueError:
        return None  # En cas d'erreur de conversion, retourner None

# Fonction pour valider l'URL
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])  # Vérifie que le schéma et le netloc (hôte) sont présents
    except ValueError:
        return False

# Fonction pour scraper les informations des annonces
def scrape_online_announcements(department, category, num_pages):
    department_data = []  # Structure de données pour stocker les données collectées

    for page in range(1, num_pages + 1):
        url = generate_url(department, category, page)
        html = get_html(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            announcements = soup.find_all("div", {"class": "map-layout__col map-layout__col--content"})  # On récupère les annonces
            if announcements:  # Si il y a des annonces
                for announcement in announcements:  # Pour chaque annonce
                    try:
                        data = extract_announcement_data(announcement)  # On extrait les données
                        if data['price'] is not None and data['url'] is not None:
                            # Valider l'URL
                            if is_valid_url(data['url']):
                                # Nettoyer le prix
                                cleaned_price = clean_price(data['price'])
                                if cleaned_price is not None:
                                    # Vérifier si l'annonce existe déjà dans la base de données
                                    cur.execute("SELECT url FROM annonces WHERE url = %s", (data['url'],))
                                    existing_url = cur.fetchone()
                                    if existing_url is None:
                                        # Traitement de l'annonce pour l'ajouter à la structure de données
                                        department_data.append(data)
                                        # Insérer l'annonce dans la base de données
                                        insert_announcement(data)
                                    else:
                                        logger.info(f"Annonce en double trouvée pour l'URL : {data['url']}")
                    except Exception as e:  # Si il y a une erreur
                        logger.error(f"Erreur lors du traitement de l'annonce sur la page {page}: {str(e)}")
        else:
            print(f'Erreur lors de la requête sur l\'url {url}')
        
        # Ajoutez une pause d'une seconde avant de faire la prochaine requête
        time.sleep(1)

    # Sauvegarde des données au format JSON
    save_data_to_json(department_data, department)

# Fonction pour extraire les données d'une annonce
def extract_announcement_data(announcement):
    data = {
        'title': '',         # Titre de l'annonce
        'price': None,       # Prix de l'annonce
        'url': '',           # URL de l'annonce
        'city': '',          # Ville de l'annonce
        'surface': None,     # Surface de l'annonce
        'postal_code': None  # Code postal de l'annonce
    }

    # Extraction des données
    try:
        # Extraction des données de l'annonce
        title_elem = announcement.find("h2", {"class": "offer-card__header__title"})
        if title_elem:
            data['title'] = title_elem.text.strip()
        # Extraction du prix de l'annonce
        price_elem = announcement.find("span", {"class": "badge_content"})
        if price_elem:
            data['price'] = price_elem.text.strip()
        # Extraction de l'URL de l'annonce
        url_elem = announcement.find("a", {"class": "list_item"})
        if url_elem and 'href' in url_elem.attrs:
            data['url'] = url_elem['href']
        # Extraction de la ville de l'annonce
        city_elem = announcement.find("div", {"class": "collapsed-text__content collapsed-text__content--collapsed"})
        if city_elem:
            data['city'] = city_elem.text.strip()
        # Extraction de la surface de l'annonce
        surface_elem = announcement.find("span", {"class": "badge__content__inner"})
        if surface_elem:
            surface_text = surface_elem.text.strip()
            # Extraction de la surface (en m²) en tant qu'entier
            surface_value = ''.join(filter(str.isdigit, surface_text))
            if surface_value:
                data['surface'] = int(surface_value)
        # Extraction du code postal de l'annonce
        postal_code_elem = announcement.find("h2", {"class": "offer-card__header__title"})
        if postal_code_elem:
            # Extraction du code postal en tant qu'entier
            postal_code_value = ''.join(filter(str.isdigit, postal_code_elem.text.strip()))
            if postal_code_value:
                data['postal_code'] = int(postal_code_value)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des données de l'annonce : {str(e)}")

    return data

# Fonction pour sauvegarder les données au format JSON
def save_data_to_json(data, department):
    filename = f"{department}_data.json"
    filepath = os.path.join(data_folder, filename)
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Exemple d'ajout de messages INFO dans le script
def main():
    for department in DEPARTMENTS:
        for category in CATEGORIES:
            logger.info(f"Début du scraping pour le département {department} et la catégorie {category}.")
            print(f"Scraping des annonces pour le département {department} et la catégorie {category}...")
            scrape_online_announcements(department, category, NUM_PAGES)
            print(f"Scraping terminé pour le département {department} et la catégorie {category}.")
            logger.info(f"Fin du scraping pour le département {department} et la catégorie {category}.")

logging.basicConfig(filename=os.path.join(logs_folder, 'logfile.log'), level=logging.INFO)


# Fermez le curseur et la connexion à la base de données à la fin du script
cur.close()
conn.close()

if __name__ == "__main__":
    main()
