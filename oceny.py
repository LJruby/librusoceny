from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import sys
import re
import os
from bs4 import BeautifulSoup

class NameForm(FlaskForm):
    class Meta:
      csrf = False
    name1 = StringField('Login do librusa', validators=[DataRequired()])
    name2 = StringField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Jeszcze tylko manto i wakacje :)')

def do_login(login, password):
    session = requests.session()
    session.get('https://api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata')
    session.post('https://api.librus.pl/OAuth/Authorization/Grant?client_id=46', data={
        'action': 'login',
        'login': login,
        'pass': password
    })
    session.get('https://api.librus.pl/OAuth/Authorization/Grant?client_id=46')
    przegladaj_oceny = session.get('https://synergia.librus.pl/przegladaj_oceny/uczen').text
    a_list = BeautifulSoup(przegladaj_oceny,'html5lib').findAll("a",attrs={"title": re.compile('.*Data.*')})
    lines=[]
    for a in a_list:
      lines.append(re.search(r'\d{4}-\d{2}-\d{2}', a['title']).group() + ' Ocena: "' + a.get_text() + '" - ' + a['title'].replace('<br>',', ').replace('<br/>','').replace('<br />',', '))
    lines.sort(reverse=True)
    if not lines:
      return ['Zły login/hasło']
    else:
      return lines
          
oceny=Flask(__name__)
oceny.config['SECRET_KEY'] = os.urandom(12).hex()
Bootstrap(oceny)

@oceny.route("/", methods=['GET', 'POST'])
def index():
  form = NameForm()
  ocenki = []
  if form.validate_on_submit():
    name1 = form.name1.data
    name2 = form.name2.data
    return render_template("index.html", form=form, ocenki=do_login(name1,name2))
  else:
    return render_template("index.html", form=form, ocenki=ocenki)
    
if __name__ == "__main__":
  oceny.run()
