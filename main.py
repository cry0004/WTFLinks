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
def index():
    error = None
    if request.method == 'POST':
        url = request.form.get('url')
        preset_style = request.form.get('style')
        custom_text = request.form.get('custom_text', '').strip()
        category = request.form.get('category', '').strip().lower().replace(' ', '-')
        
        # Check: o uno o l'altro, mai entrambi o nessuno
        if preset_style and custom_text:
            error = "Scegli solo uno: preset style oppure testo personalizzato, non entrambi."
            return render_template('index.html', error=error)
        
        if not preset_style and not custom_text:
            error = "Devi scegliere un preset style oppure inserire un testo personalizzato."
            return render_template('index.html', error=error)
        
        # Determina il path finale
        final_path = preset_style if preset_style else custom_text
        
        # Validazione del path (equivalente alla validazione slug)
        if not re.match(r'^[a-z0-9\-]+$', final_path.lower()):
            error = "Path non valido. Usa solo lettere minuscole, numeri e trattini."
            return render_template('index.html', error=error)
        
        # Costruisci lo slug finale
        slug = f"{category}/{final_path}" if category else final_path
        
        # Salva nel DB
        try:
            conn = sqlite3.connect('links.db')
            c = conn.cursor()
            c.execute('INSERT INTO links (slug, url, category) VALUES (?, ?, ?)', (slug, url, category))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            error = "Questo slug esiste già. Scegli un altro nome."
            return render_template('index.html', error=error)
        
        short_url = f"{request.host_url}{slug}"
        return render_template('index.html', short_url=short_url)
    
    return render_template('index.html', error=error)

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
