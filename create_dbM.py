from flask import Flask, session, render_template, redirect, url_for

import sqlite3
import json
import data_modelM
from werkzeug.security import generate_password_hash, check_password_hash

JSONFILENAME = 'recipes.json'
DBFILENAME = 'marche.sqlite'


app = Flask(__name__)
app.secret_key =b'17405ad09042ab795a552694984386f25209562b31cfc6c6dda33055e716d516'

  

# Utility function
def db_run(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()

db_run("UPDATE user SET role = ? WHERE nom = ?", ('admin', 'Marina'))


def load(fname=JSONFILENAME, db_name=DBFILENAME):

  db_run('DROP TABLE IF EXISTS user')
  db_run('DROP TABLE IF EXISTS entreprise')

  db_run('CREATE TABLE user ( id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL, email TEXT NOT NULL, mot_de_passe TEXT NOT NULL, role TEXT NOT NULL DEFAULT "client", entrepreneur_status TEXT NOT NULL DEFAULT "non demandé", motivation TEXT DEFAULT "null", experience TEXT DEFAULT "null")')
  

  db_run('CREATE TABLE entreprise (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_entreprise TEXT NOT NULL, adresse TEXT, telephone TEXT, description TEXT, logo TEXT, services TEXT, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES user(id))')

##load() 
def VerifiUserName(name):
    query = "SELECT nom FROM user WHERE nom = ?"
    str=""+name
    result = data_modelM.db_fetch(query, (str,))
    return result is not None

def VerifiPassword(name, password):
    query = "SELECT mot_de_passe FROM user WHERE nom = ?"
    row = data_modelM.db_fetch(query, (name,))
    if row is None:
        return False

    password_hash = row["mot_de_passe"]  
    return check_password_hash(password_hash, password)


