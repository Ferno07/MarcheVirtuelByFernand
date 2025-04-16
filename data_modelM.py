import sqlite3
import math
from werkzeug.security import generate_password_hash, check_password_hash

DBFILENAME = 'marche.sqlite'

# Utility functions
def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    # to allow access to columns by name in res
    conn.row_factory = sqlite3.Row 
    cur = conn.execute(query, args)
    # convert to a python dictionary for convenience
    if all:
      res = cur.fetchall()
      if res:
        res = [dict(e) for e in res]
      else:
        res = []
    else:
      res = cur.fetchone()
      if res:
        res = dict(res)
  return res

def db_insert(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()
    return cur.lastrowid


def db_run(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()
    return True


def db_update(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()
    return cur.rowcount




##Lire l'entreprise avec son identifiant , renvoie None si rien n'est trouvé
def read(id):
  found = db_fetch('SELECT * FROM entreprise WHERE id = ?', (id,))

  return found


##Fonction pour créer une nouvelle entreprise dans  dans la base.
def create(entreprise):
 
 if isinstance(entreprise.get('services'), list):
    entreprise['services'] = " - ".join(entreprise['services'])
  

    id = db_insert(
    'INSERT INTO entreprise (nom_entreprise, adresse, telephone, description, logo, services, user_id) VALUES (:nom_entreprise, :adresse, :telephone, :description, :logo, :services, :user_id)',
    entreprise)
 return id

##Fonction pour mettre à jour une recette de la base.

def update_enterprise(id, enterprise):
    # Si 'services' de l'entreprise  sont fournis sous forme de liste, on la transforme en chaîne de caractères séparée par des tirets
    if 'services' in enterprise and isinstance(enterprise['services'], list):
        enterprise['services'] = " - ".join(enterprise['services']) 
    # On construit le dictionnaire des paramètres à partir du dictionnaire 'enterprise'
    params = {key: enterprise[key] for key in enterprise}
    params['id'] = id
    # Requête SQL pour mettre à jour l'entreprise
    result = db_update(
        'UPDATE entreprise SET nom_entreprise = :nom_entreprise, adresse = :adresse, telephone = :telephone, description = :description, logo = :logo, services = :services WHERE id = :id',
        params
    )
    return result == 1


##fonction pour supprimer une entreprise dans la base de données
def delete(id):
  db_run('DELETE FROM entreprise WHERE id = ?', (id,))


## Recherche d'une recette par requête, avec pagination des résultats .
# Cette fonction prend en argument la requête sous forme d'une chaîne de caractères
#et le numéro de la page de résultats.
#Cette fonction retourne un dictionnaire contenant les champs suivants :nom entreprise et logo
def search(query="", page=1):
  num_per_page = 32
  # on utiliser l'opérateur SQL LIKE pour rechercher dans le titre 
  res = db_fetch('SELECT count(*) FROM entreprise WHERE nom_entreprise LIKE ?',
                       ('%' + query + '%',))
  num_found = res['count(*)']
  results = db_fetch('SELECT id as entry, nom_entreprise, logo FROM entreprise WHERE nom_entreprise LIKE ? ORDER BY id LIMIT ? OFFSET ?',
                     ('%' + query + '%', num_per_page, (page - 1) * num_per_page), all=True)
  return {
    'results': results,
    'num_found': num_found, 
    'query': query,
    'next_page': page + 1,
    'page': page,
    'num_pages': math.ceil(float(num_found) / float(num_per_page))
  }


def new_user(name,mail,password):
  ##password_hashed = generate_password_hash(password)
  query = "INSERT INTO user (nom,email,mot_de_passe) Values (?,?,?)"
  ok = db_insert(query, (name,mail,password,), DBFILENAME)
  return ok 

def get_user_by_name(name):
    query = "SELECT * FROM user WHERE nom = ?"
    return db_fetch(query, (name,))

def get_enterprise_by_user_id(user_id):
    query = "SELECT * FROM entreprise WHERE user_id = ?"
    return db_fetch(query, (user_id,))


