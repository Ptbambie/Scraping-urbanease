import psycopg2

#informations pour le site
SITE_URL = "https://www.cessionpme.com/annonces,location-immobilier-entreprise-locaux-activites-entrepots,53,3,L,offres.html"#l'url https://www.cessionpme.com/annonce’ n'existe plus
NUM_PAGES = 5
DEPARTMENTS = ['64','33']
CATEGORIES = [
    'Locaux, Entrepôts, Terrains',
    'Bureaux, Coworking'
]

#import des informations de la base de données
from secrets import DB_NAME, USER, PASSWORD, HOST


