from flask import Flask, render_template, request, redirect, abort
import json
import random
import string
import os

app = Flask(__name__)

DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            f.write("{}")
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

def generate_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Lista nomi dominio fake
fake_domains = [
    "no-click-here",
    "definitely-not-link",
    "click-at-your-own-risk",
    "dont-trust-this-link",
    "secret-link-inside",
    "very-suspicious",
    "totally-safe-link",
    "click-if-you-dare",
    "not-a-virus",
    "free-stuff-here",
    "do-not-open",
    "link-from-hell",
    "weird-link-alert",
    "suspicious-link",
    "not-for-humans"
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form.get("url")
        custom_id = request.form.get("custom_id", "").strip().replace(" ", "-")

        if not original_url or not (original_url.startswith("http://") or original_url.startswith("https://")):
            return render_template("index.html", error="Please enter a valid URL starting with http:// or https://")

        db = load_db()

        # Se custom_id è stato fornito
        if custom_id:
            if custom_id in db:
                return render_template("index.html", error="This custom name is already taken.")
            new_id = custom_id
        else:
            new_id = generate_id()
            while new_id in db:
                new_id = generate_id()

        db[new_id] = original_url
        save_db(db)

        # Usa sempre lo stesso dominio fittizio per coerenza
        domain = request.host  # tipo pastaalvirus.replit.app
        short_url = f"https://{domain}/{new_id}"

        return render_template("index.html", short_url=short_url)

    return render_template("index.html")


@app.route("/<id>")
def redirect_link(id):
    db = load_db()
    if id in db:
        return redirect(db[id])
    else:
        return render_template("404.html", id=id), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
