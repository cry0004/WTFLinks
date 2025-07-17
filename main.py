from flask import Flask, render_template, request, redirect, abort
import sqlite3
import os
import re

app = Flask(__name__)

# init DB
def init_db():
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE,
            url TEXT NOT NULL,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        category = request.form['category'].strip().lower().replace(' ', '-')
        custom_slug = request.form.get('custom_slug', '').strip().lower()

        # validazione slug
        if not custom_slug or not re.match(r'^[a-z0-9\-]+$', custom_slug):
            return "Slug non valido. Usa solo lettere minuscole, numeri e trattini.", 400

        slug = f"{category}/{custom_slug}" if category else custom_slug

        # salva nel DB
        try:
            conn = sqlite3.connect('links.db')
            c = conn.cursor()
            c.execute('INSERT INTO links (slug, url, category) VALUES (?, ?, ?)', (slug, url, category))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            return "Questo slug esiste già. Scegli un altro nome.", 400

        short_url = f"{request.host_url}{slug}"
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<path:slug>')
def redirect_slug(slug):
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('SELECT url FROM links WHERE slug = ?', (slug,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return abort(404)

if __name__ == '__main__':
    app.run(debug=True)
