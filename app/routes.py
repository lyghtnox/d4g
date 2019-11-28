from flask import render_template, request, session, send_from_directory, send_file, redirect, flash
from app import app
from itsdangerous import TimestampSigner, SignatureExpired
import os
import hashlib
import sqlite3
import re
import smtplib
import base64
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from .secrets import SMTP_PASS, SMTP_USER


DB_FILE = 'app/cnl.db'
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg'])


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def req_moyenne(data):
    last_day=31
    prefix_col_jour= "con_j"
    requete_string = "SELECT con_foyer,("
    try:
        if data['croissant']:
            tri_str = " ORDER BY con_moyenne ASC"
    except KeyError:
        tri_str = " ORDER BY con_moyenne DESC"

    duree = int(data['nbJour'])
    if duree>=last_day:
        duree = last_day-1;
    for i in range(last_day-duree, last_day+1):
        requete_string+="{}{}+".format(prefix_col_jour, i)


    return "{})/{} AS  con_moyenne FROM cn_consommation {} LIMIT {}".format(requete_string[:-1], duree, tri_str, data['nbLogements'])




@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('loggedIn'):
        return redirect('/dashboard', 302)

    elif request.method == 'GET':
        return render_template('indexLourd.jinja2')

    elif request.method == 'POST':
        data = request.form.to_dict()

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT acc_foyer, acc_password, acc_activated, acc_admin FROM cn_access \
                   WHERE acc_identifiant=:login", data)
        resp = c.fetchone()
        if not resp:
            flash("Mauvaise authentification.")
            return render_template('indexLourd.jinja2')
        hash = resp[1].lower()
        if resp[2] != 1:
            flash("Veuillez activer votre compte.")
        elif hash == hashlib.sha256(data['mdp'].encode('utf-8')).hexdigest():
            session['user'] = data['login']
            session['foyer'] = resp[0]
            session['loggedIn'] = True
            if resp[3] == 1:
                session['admin'] = True
                session['foyer'] = ''
            return redirect('/dashboard', 302)
        else:
            flash("Mauvaise authentification.")
        return render_template('indexLourd.jinja2')


@app.route('/dashboard')
def dashboard():
    if not session.get('loggedIn'):
        return redirect('/login')
    elif session.get('admin'):
        return redirect('/admin')

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT * FROM cn_consommation WHERE con_foyer=?",
              (session.get('foyer'),))
    try:
        data = list(c.fetchone())[2:]
    except:
        data = ()
    month = '01/19'
    dict = {"{}/{}".format(i+1, month):j for i,j in enumerate(data)}
    dates = ["{}/{}".format(i+1, month) for i in range(31)]
    val = sorted(dict.items(), key=lambda x: datetime.strptime(x[0], "%d/%m/%y"))
    c.execute("SELECT loc_nom, loc_prenom FROM cn_locataire WHERE loc_foyer=?",
              (session.get('foyer'),))
    loc = c.fetchone()
    c.execute("SELECT pro_nom, pro_prenom, pro_societe, pro_adresse FROM cn_proprietaire WHERE pro_foyer=?",
              (session.get('foyer'),))
    pro = c.fetchone()
    c.execute("SELECT * FROM cn_logement WHERE log_foyer=?",
              (session.get('foyer'),))
    log = c.fetchone()
    return render_template("dashboard.jinja2", dict=dict, labels=dates, data=val,loc=loc, pro=pro, log=log)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect('/dashboard')
    if request.method == 'GET':
        return render_template('dashboardAdmin.jinja2')
    elif request.method == 'POST':
        data = request.form.to_dict()
        req = req_moyenne(data)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(req)
        try:
            results = list(c.fetchall())
        except:
            results = ()
        labels = [i for (i,_) in results]
        return render_template('dashboardAdmin.jinja2',labels=labels, data=results)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        data = request.form.to_dict()
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

        if(re.search(regex,data['mail'])):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT acc_identifiant FROM cn_access WHERE acc_identifiant=:mail",
                      data)
            if c.fetchone():    # If user exists
                s = TimestampSigner(app.secret_key)     # Create signed token
                token = base64.b64encode(s.sign(data['mail']))

                smtp = smtplib.SMTP_SSL('smtp.gmail.com',465)
                smtp.login(SMTP_USER, SMTP_PASS)
                msg = """Subject: Reinitialiser le mot de passe

                Pour reinitialiser votre mot de passe, suivez le lien suivant:
                http://vps753617.ovh.net/pass_reset/{}""".format(token.decode('utf-8'))
                smtp.sendmail("admin@vps753617.ovh.net",data['mail'],msg)
            flash('Message envoyé! Vérifiez vos mails.')
        else:
            flash("Désolé, votre nom d'utilisateur n'est pas une adresse email valide.")
    return render_template('forgot_pass.jinja2')

@app.route('/pass_reset/<token>', methods=['GET', 'POST'])
@app.route('/pass_reset', methods=['POST'])
def pass_reset(token=None):
    if request.method == 'GET':
        s = TimestampSigner(app.secret_key)
        try:
            user = s.unsign(base64.b64decode(token).decode('utf-8'), max_age=86400)
            session['user'] = user.decode('utf-8')
        except SignatureExpired:
            flash("Lien expiré.")
            return render_template('flash.jinja2')
        return render_template('reset_pass.jinja2')

    if request.method == 'POST':
        data = request.form.to_dict()
        hash = hashlib.sha256(data['pass'].encode('utf-8')).hexdigest().upper()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE cn_access SET acc_password=? WHERE acc_identifiant=?", (hash, session.get('user')))
        conn.commit()
        flash("Mot de passe mis à jour!")
        return render_template('flash.jinja2')

@app.route('/confirm_mail/<token>', methods=['GET'])
def confirm_mail(token):
    s = TimestampSigner(app.secret_key)
    try:
        user = s.unsign(base64.b64decode(token).decode('utf-8'), max_age=86400).decode('utf-8')
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE cn_access SET acc_activated=1 WHERE acc_identifiant=?", (user,))
        conn.commit()
        flash("Mail confirmé")
    except SignatureExpired:
        flash("Lien expiré.")
    return render_template('flash.jinja2')

@app.route('/account', methods=['GET', 'POST'])
def add_account():
    if not session.get('admin'):
        return redirect('/dashboard')
    elif request.method == 'GET':
        return render_template('addCompte.jinja2')
    elif request.method == 'POST':
        data = request.form.to_dict()
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO cn_logement VALUES(:foyerArea,:textArea,:surfaceArea,:piecesArea,:chauffageArea,:anneeConstruArea,:numVoieArea,:rueArea,:cpArea,:villeArea)", data)
            c.execute("INSERT INTO cn_proprietaire(pro_nom, pro_prenom,pro_societe,pro_adresse,pro_foyer) \
                      VALUES(:nomProArea, :prenomProArea, :societeArea, :adresseArea, :foyerArea)", data)
            c.execute("INSERT INTO cn_locataire(loc_foyer, loc_nom, loc_prenom) \
                      VALUES(:foyerArea, :nomLocArea, :prenomLocArea)", data)
            c.execute("INSERT INTO cn_access(acc_identifiant, acc_foyer, acc_activated, acc_admin) \
                      VALUES(:loginArea, :foyerArea, 0, 0)", data)
            conn.commit()
            flash("Utilisateur ajouté!")
        except sqlite3.ProgrammingError:
            flash('La table existe déjà!')

        s = TimestampSigner(app.secret_key)     # Create signed token
        token = base64.b64encode(s.sign(data['loginArea']))

        smtp = smtplib.SMTP_SSL('smtp.gmail.com',465)
        smtp.login(SMTP_USER, SMTP_PASS)
        msg = """Subject: Confirmez votre adresse mail.

        Votre compte vient d'etre cree sur http://vps753617.ovh.net.
        Pour l'activer, suivez le lien suivant:
        http://vps753617.ovh.net/confirm_mail/{}
        Creez votre mot de passe en cliquant sur "Mot de passe oublie"
        """.format(token.decode('utf-8'))
        smtp.sendmail("admin@vps753617.ovh.net",data['loginArea'],msg)
        return render_template('flash.jinja2')


@app.route('/mentions-legales')
def conditions():
    return render_template('condition.html')


@app.route('/browser')
def browse():
    if not session.get('loggedIn'):
        return redirect('/login')
    userDir = os.path.join(UPLOAD_FOLDER, session.get('foyer'))
    try:
        itemList = os.listdir(userDir)
    except:
        itemList = []
    return render_template('browse.html', itemList=itemList)


@app.route('/browser/<path:urlFilePath>')
def browser(urlFilePath):
    if not session.get('loggedIn'):
        return redirect('/login')

    userDir = os.path.join(UPLOAD_FOLDER, session.get('foyer'))
    nestedFilePath = os.path.join(userDir, urlFilePath)
    if os.path.isdir(nestedFilePath):
        itemList = os.listdir(nestedFilePath)
        if not urlFilePath.startswith("/"):
            urlFilePath = "/" + urlFilePath
        return render_template('browse.html', urlFilePath=urlFilePath, itemList=itemList)

    if os.path.isfile(nestedFilePath):
        return send_file(nestedFilePath, as_attachment=True)
    flash("Erreur")
    return render_template('flash.jinja2')

@app.route('/upload', methods=['GET', 'POST'])
def upload_form():
    if not session.get('loggedIn'):
        return redirect('/login')
    if request.method == 'GET':
        return render_template('upload.jinja2')

    elif request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        elif file and allowed_file(file.filename):
            userDir = os.path.join(UPLOAD_FOLDER, session.get('foyer'))
            if not os.path.isdir(userDir):
                os.mkdir(userDir)
            filename = secure_filename(file.filename)
            file.save(os.path.join(userDir, filename))
            flash('File successfully uploaded')
            return redirect('/upload')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg')
            return redirect(request.url)
