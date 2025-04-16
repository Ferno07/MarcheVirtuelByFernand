from flask import Flask, session, Response, request, redirect, url_for, render_template
import data_modelM as model 
from functools import wraps
import create_dbM
import os
from werkzeug.security import generate_password_hash, check_password_hash


from werkzeug.utils import secure_filename




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key =b'17405ad09042ab795a552694984386f25209562b31cfc6c6dda33055e716d516'


# Routes des pages principales du site #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not('id' in session):
            return "accès non autorisé"
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.get('/demander_entrepreneuriat')
def demande():
   return render_template('demande_entrepreneur.html')

@app.post('/demander_entrepreneuriat')
@login_required
def demander_entrepreneuriat():
    motivation=request.form['motivation']
    experience = request.form['experience']
    user_id = session.get('id')
    if not user_id:
        return "Accès non autorisé", 403
    
    # Mettre à jour le champ entrepreneur_status dans la base de données
    query = "UPDATE user SET entrepreneur_status = ? WHERE id = ?"
    query1 = "UPDATE user SET motivation = ? WHERE id = ?"
    query2 = "UPDATE user SET experience = ? WHERE id = ?"
    model.db_run(query, ("en attente", user_id))
    model.db_run(query1, (motivation, user_id))
    model.db_run(query2, (experience, user_id))
    
    # Mettre à jour la session pour refléter ce changement
    session['entrepreneur_status'] = "en attente"
    
    # Rediriger l'utilisateur vers l'accueil
    return redirect(url_for('home'))


@app.get('/admin/demandes')
@login_required
def consulter_demandes():
    if session.get('role') != 'admin':
        return "Accès interdit", 403
    query = "SELECT * FROM user WHERE entrepreneur_status = ?"
    demandes = model.db_fetch(query, ("en attente",), all=True)
    return render_template('admin_voir_demande.html', demandes=demandes)


@app.post('/admin/demandes/<int:demande_id>/traiter')
@login_required
def traiter_demande(demande_id):
  
    if session.get('role') != 'admin':
        return "Accès interdit", 403

    # Récupérer la décision envoyée par le formulaire ('valider' ou 'refuser')
    decision = request.form.get('decision')
    if decision not in ['valider', 'refuser']:
        return "Décision invalide", 400

    if decision == 'valider':
        # Approuver la demande : on met à jour le statut et on change éventuellement le rôle en 'entrepreneur'
        query = "UPDATE user SET entrepreneur_status = ?, role = ? WHERE id = ?"
        model.db_run(query, ("validé", "entrepreneur", demande_id))
    else:
        # Refuser la demande : on met à jour le statut en 'refusé'
        query = "UPDATE user SET entrepreneur_status = ? WHERE id = ?"
        model.db_run(query, ("refusé", demande_id))
        
    return redirect(url_for('consulter_demandes'))


@app.get('/VoirMonEntreprise')
def voir_entreprise():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('Seloger'))  
    entreprise = model.get_enterprise_by_user_id(user_id)
    if not entreprise:
        return "Vous n'avez pas encore créé d'entreprise."
    return render_template('VoirMonEntreprise.html',isLogin=True, entreprise=entreprise)

def login(name, password):
  if not (create_dbM.VerifiUserName(name)) :
    return -1
  elif not (create_dbM.VerifiPassword(name,password)):
    return -1
  else :
    return True

@app.post('/login')
def login_route():
    name = request.form['name']
    password = request.form['password']

    user = model.get_user_by_name(name)
    if user is None or not check_password_hash(user['mot_de_passe'], password):
        return redirect(url_for('Seloger'))
    session.clear()
    session['id'] = user['id']
    session['name'] = user['nom']
    session['role'] = user['role']
    session['entrepreneur_status'] = user.get('entrepreneur_status', 'non demandé')
    return redirect(url_for('home'))


@app.post('/logout')
def logout():
  session.clear()
  return redirect('/')

@app.get('/login')
def Seloger():
    if 'name' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.get('/new_user')
def nouvelUtilisateur():
  return render_template('new_user.html')

@app.post('/new_user')
def ajout():
  name = request.form['name']
  mail = request.form['mail']
  password1= request.form['password1']
  password2 = request.form['password2']
  
  if(create_dbM.VerifiUserName(name)==True):
    return "Veuillez changer de nom svp"
  elif(password1!=password2):
    return "Veuillez revoir vos mots de passe, "
  else :
    password_hash = generate_password_hash(password1)
    ok = model.new_user(name,mail,password_hash)
    if ok==ok:
      return redirect('/')
    else:
      return render_template('new_user.html')


# Retourne une page principale
@app.get('/')
def home():
    if 'name' in session:
        name = session['name']
        user_id = session.get('id')
        # Si l'utilisateur est admin, on définit role True
        Ok = model.get_enterprise_by_user_id(user_id) and session.get('entrepreneur_status') == 'validé'
       
        if session.get('role') == 'admin':
            return render_template('index.html',
                                   isLogin=True, name=name, status= Ok,
                                   role=True)
        # Pour les autres utilisateurs, on conserve la vérification entrepreneur_status
        elif session.get('entrepreneur_status') == 'validé':
            return render_template('index.html',
                                   isLogin=True, name=name, status=True, role=False)
        else:
            return render_template('index.html',
                                   isLogin=True, name=name, status=False, role=False)
    else:
        return render_template('index.html', isLogin=False)


# Retourne les résultats de la recherche à partir de la requête "query"
@app.get('/search')
def search():
  if 'page' in request.args:
    page = int(request.args["page"])
  else:
    page = 1
  if 'query' in request.args:
    query = request.args["query"]
  else:
    query = ""
  found = model.search(query, page)
  if 'name' in session :
     name=session['name']
     return render_template('search.html', found=found, isLogin=True, name = name)
  return render_template('search.html', found=found)

# Retourne le contenu d'une recette d'identifiant "id"
@app.get('/read/<id>')
def read(id):
  entreprise = model.read(int(id))

  if(session.get('role') == "admin"):
     admin=True
  
  else :
     admin=False

  return render_template('read.html',isLogin=True, entreprise=entreprise, admin=admin)


@app.get('/create')
def create_form():
  return render_template('create.html')

@app.get('/update/<id>')
def update_form(id):
  entreprise = model.read(int(id))
  return render_template('update.html', isLogin=True, entreprise=entreprise)


@app.get('/delete/<id>')
def delete_form(id):
  entry = model.read(int(id))
  return render_template('delete.html', id=id, nom_entreprise=entry['nom_entreprise'])





def parse_user_list(user_list):
    
    l = user_list.strip().split("-")
    l = [e.strip() for e in l]
    l = [e for e in l if len(e) > 0]
    return l

def post_data_to_entreprise(form_data, file_data):
    """
    form_data : request.form (données texte)
    file_data : request.files (fichier image)
    """
    services = parse_user_list(form_data['services']) if 'services' in form_data else []

  
    logo_file = file_data.get('logo')
    if logo_file and logo_file.filename != '':
        filename = secure_filename(logo_file.filename)
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logo_file.save(logo_path)
    else:
        logo_path = ''  

    return {
        'nom_entreprise': form_data['nom_entreprise'],
        'adresse': form_data['adresse'],
        'telephone': form_data['telephone'],
        'description': form_data['description'],
        'logo': logo_path,  # Chemin relatif sauvegardé
        'user_id': session['id'],
        'services': services
    }



@app.post('/create')
@login_required
def create_post():
    user_id = session.get('id')
    existing = model.get_enterprise_by_user_id(user_id)
    if existing:
        return "Vous avez déjà créé une entreprise. Veuillez utiliser la page de modification pour la mettre à jour."

    # Utilise la fonction corrigée avec form ET files
    enterprise_data = post_data_to_entreprise(request.form, request.files)
    
    id = model.create(enterprise_data)
    return redirect(url_for('read', id=str(id)))




@app.post('/update/<id>')
@login_required
def update_post(id):
    id = int(id)

    # Correction : ajout de request.files pour gérer l'image
    entreprise_data = post_data_to_entreprise(request.form, request.files)

    model.update_enterprise(id, entreprise_data)
    return redirect(url_for('read', id=str(id)))


@app.post('/delete/<id>')
def delete_post(id):
  query ="select user_id from entreprise where id = ?"
  user_id = model.db_fetch(query, (id))
  user_id1 = user_id['user_id']
  query = "UPDATE user SET entrepreneur_status = ?, role = ? WHERE id = ?"
  model.db_run(query, ("non demandé", "client", user_id1))
  model.delete(int(id))
  return redirect(url_for('home'))


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)
