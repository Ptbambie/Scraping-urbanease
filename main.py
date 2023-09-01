import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from conf import DB_NAME, USER, PASSWORD, HOST, SITE_URL, NUM_PAGES, DEPARTMENTS, CATEGORIES
from urllib.parse import urlparse

# Utilisation des variables d'environnement
print(f"SITE_URL: {SITE_URL}")
print(f"NUM_PAGES: {NUM_PAGES}")
print(f"DEPARTMENTS: {DEPARTMENTS}")
print(f"CATEGORIES: {CATEGORIES}")
print(f"DB_NAME: {DB_NAME}")
print(f"USER: {USER}")
print(f"HOST: {HOST}")
print(f"PASSWORD: {PASSWORD}")

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
        # Supprimer les caractères non numériques de la chaîne
        cleaned_price = ''.join(filter(str.isdigit, price_str))
        # Convertir la chaîne nettoyée en entier
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
def scrape_online_annoucements(department, category, num_pages):
    for page in range(1, num_pages + 1):
        url = generate_url(department, category, page)
        html = get_html(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            annoucements = soup.find_all("div", {"class": "annonce"})  # on récupère les annonces
            if annoucements:  # si il y a des annonces
                for annoucement in annoucements:  # pour chaque annonce
                    try:
                        data = extract_annoucement_data(annoucement)  # on extrait les données
                        if data['price'] is not None and data['url'] is not None:
                            # Valider l'URL
                            if is_valid_url(data['url']):
                                # Nettoyer le prix
                                cleaned_price = clean_price(data['price'])
                                if cleaned_price is not None:
                                    # traitement de l'annonce pour l'ajouter à la base de données
                                    logfile.write(f'Annonce{data["title"]}\n')
                                    logfile.write(f'Prix: {cleaned_price}\n')
                                    logfile.write(f'Url: {data["url"]}\n')
                                    logfile.write(f'Ville: {data["city"]}\n')
                                    logfile.write(f'surface: {data["surface"]}\n')
                                    logfile.write(f'code postal: {data["postal_code"]}\n')
                                    logfile.write(f'------------------------\n')  # séparateur
                    except Exception as e:  # si il y a une erreur
                        logfile.write(f"Erreur lors du traitement de l'annonce sur la page {page}: {str(e)}\n")
        else:
            print(f'Erreur lors de la requête sur l\'url {url}')

# Boucle de pagination
def scrape_all_pages(department, category, max_pages):
    page = 1
    while page <= max_pages:
        url = generate_url(department, category, page)
        html = get_html(url)
        if html:
            try:
                soup = BeautifulSoup(html, 'html.parser')  # on récupère le contenu de la page
                annoucements = soup.find_all("div", {"class": "annonce"})  # on récupère les annonces
                if annoucements:
                    with open('logfile.txt', 'a') as logfile:
                        for annoucement in annoucements:
                            try:
                                data = extract_annoucement_data(annoucement)  # on extrait les données
                                if data['price'] is not None and data['url'] is not None:
                                    # Valider l'URL
                                    if is_valid_url(data['url']):
                                        # Nettoyer le prix
                                        cleaned_price = clean_price(data['price'])
                                        if cleaned_price is not None:
                                            # traitement de l'annonce pour l'ajouter à la base de données
                                            logfile.write(f'Annonce{data["title"]}\n')
                                            logfile.write(f'Prix: {cleaned_price}\n')
                                            logfile.write(f'Url: {data["url"]}\n')
                                            logfile.write(f'Ville: {data["city"]}\n')
                                            logfile.write(f'surface: {data["surface"]}\n')
                                            logfile.write(f'code postal: {data["postal_code"]}\n')
                                            logfile.write(f'------------------------\n')  # séparateur
                            except Exception as e:  # si il y a une erreur
                                logfile.write(f"Erreur lors du traitement de l'annonce sur la page {page}: {str(e)}\n")
            except Exception as e:  # si il y a une erreur
                print(f'Erreur lors du scraping de la page {page}: {str(e)}')
        else:
            print(f'Erreur lors de la requête sur l\'url {url}')
        page += 1

# exemple d'annonce
SITE_URL = "https://www.cessionpme.com/"
scrape_online_annoucements('64', 'Locaux, Entrepôts, Terrains', 1)

# import de la fonction is_valid_url
from main import is_valid_url

#exemple d'URL 
valid_url1 = "https://www.cessionpme.com/annonce,acheter-affaire-bar-tabac-loto-fdj-pmu-bien-placee-seine-saint-denis-93,2219145,A,offre.html"
valid_url2 = "https://www.cessionpme.com/index.php?action=affichage&annonce=offre&moteur=OUI&type_moteur=fdc&nature_fdc=V&rubrique_fdc=&region_fdc=2&departement_fdc=93&commune_fdc=64%29&trap_fdc=&secteur_activite_fdc=local&ou_fdc=Pyr%E9n%E9es+Atlantiques+%2864%29&entre=&et=&motcle_fdc=locaux&numero_fdc="
invalid_url = " www.example.com/annonce123"

# Test des urls
print(f"Est-ce que {valid_url1} est une URL valide ? {is_valid_url(valid_url1)}")
print(f"Est-ce que {valid_url2} est une URL valide ? {is_valid_url(valid_url2)}")
print(f"Est-ce que {invalid_url} est une URL valide ? {is_valid_url(invalid_url)}")
