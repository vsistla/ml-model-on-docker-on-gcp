import pandas as pd
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import requests
import json
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])

    @app.route("/", methods=['GET', 'POST'])
    def hello():
        form = ReusableForm(request.form)
        if request.method == 'POST':
            try:
                nlp_url = 'http://nlp:5000'
                baseline = requests.post('http://nlp:5000', json={'a': 'zzz'}).json()
            except: 
                nlp_url = 'http://host.docker.internal:5000'
                baseline = requests.post(nlp_url, json={'a': 'zzz'}).json()
            baseline_scores = baseline[0]['score']

            try:
                # if input is blank, just refresh
                words = request.form['name']
                req = {'text': str(words)}
                results = requests.post(nlp_url, json=req).json()
                scores = results[0]['score']
            except json.decoder.JSONDecodeError:
                return render_template('index.html', form=form)

            corpus = pd.DataFrame(list(zip(*results[0]['corpus']))).T
            corpus.columns = 'words', 'in corpus'
            corpus = corpus.set_index('words')

            scores = {k: v-baseline_scores[k] for k, v in scores.items()}

            df = pd.DataFrame([scores]).T.sort_values(0, ascending=False).round(3)
            df.columns = ['score']
            top_score = df.index[0]
            df = df.to_html()
            corpus_html = corpus.to_html()
            pct_in = sum(corpus['in corpus']) / corpus.shape[0]
            pct_in = round(pct_in*100, 1)

        if form.validate():

            flash(words)
            flash(f'top result: {top_score}')
            flash(f'{pct_in}% of words in corpus')
            flash('in corpus words: ' + str(list(corpus[corpus['in corpus'] == 1].index)))
            flash('out of corpus words: ' + str(list(corpus[corpus['in corpus'] == 0].index)))

        else:
            df = ''
            corpus_html = ''

        return render_template('index.html', form=form, df=df, corpus=corpus_html)


if __name__ == "__main__":
    app.run(port=8000, debug=True, host='0.0.0.0')
