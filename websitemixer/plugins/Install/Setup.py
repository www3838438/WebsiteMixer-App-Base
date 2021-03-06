import os
import binascii
from flask import render_template, request, redirect
from websitemixer import app, models
from websitemixer.database import db


@app.route('/setup/step1/')
def setup1():
    return render_template("Install/step1.html")


@app.route('/setup/step2/', methods=['POST'])
def setup2():
    secretkey = binascii.hexlify(os.urandom(24)).decode("utf-8")
    appname = request.form['appname']
    dbname = request.form['dbname']
    dbuser = request.form['dbuser']
    dbpwd = request.form['dbpwd']
    dbsrv = request.form['dbsrv']

    with open('config.py', 'w') as file:
        file.seek(0)
        file.truncate()
        file.write("import os\n")
        file.write("basedir = os.path.abspath(os.path.dirname(__file__))\n\n")
        file.write("SECRET_KEY = '"+secretkey+"'\n")
        file.write("UPLOAD_FOLDER = basedir+'/websitemixer/static/upload/'\n")

        extensions = "set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'," +\
                     " 'zip'])\n\n"
        file.write("ALLOWED_EXTENSIONS = " + extensions)

        if request.form['dbmeth'] == 'mysql':
            file.write("SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://" +
                       dbuser + ":" + dbpwd + "@" + dbsrv + ":3306/" +
                       dbname + "'\n")
        elif request.form['dbmeth'] == 'postgres':
            sqlUrl = "SQLALCHEMY_DATABASE_URI = 'postgresql://" + dbuser
            file.write(sqlUrl + ":" + dbpwd + "@" + dbsrv + ":5432/" +
                       dbname + "'\n")
        else:
            sqlUrl = "SQLALCHEMY_DATABASE_URI = 'sqlite:///'"
            base = "+os.path.join(basedir,'" + appname + ".db')\n"
            file.write(sqlUrl + base)
        file.write("SQLALCHEMY_TRACK_MODIFICATIONS = True")
        file.close()

    return render_template("Install/step2.html")


@app.route('/setup/step3/', methods=['POST'])
def setup3():
    db.drop_all()
    db.create_all()

    sitename = request.form['sitename']
    sitedesc = request.form['sitedesc']
    admuser = request.form['admuser']
    admpwd1 = request.form['admpwd1']
    admpwd2 = request.form['admpwd2']
    admemail = request.form['admemail']

    if admpwd1 != admpwd2:
        return 'Admin passwords do not match! Click back and try again!'

    a = models.User(admuser, admpwd1, admemail)
    db.session.add(a)

    update = models.User.query.filter_by(username=admuser).update({'admin': 1})

    a = models.Setting('siteName', sitename)
    db.session.add(a)
    a = models.Setting('siteSubheading', sitedesc)
    db.session.add(a)
    a = models.Setting('theme', 'Base')
    db.session.add(a)

    post_text = '<p>This is your first post!'
    post_text += ' You can delete this and start posting!</p>'
    a = models.Post(admuser, 'Hello World!', '/hello-world/', post_text,
                    '', '', 'Hello World, Welcome')
    db.session.add(a)
    a = models.Page('About', '/about/', '<p>It\'s an about page!</p>', '', '')
    db.session.add(a)
    a = models.Page('Contact', '/contact/', '<p>It\'s a contact page!</p>',
                    '', '')
    db.session.add(a)

    db.session.commit()
    return redirect('/')
