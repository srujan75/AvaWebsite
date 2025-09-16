from flask import Flask, render_template, request, redirect, url_for
import psycopg2, os

app = Flask(__name__)

# Render provides DATABASE_URL as env var
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Create table if not exists
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id SERIAL PRIMARY KEY,
            type TEXT,
            filename TEXT,
            title TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM media ORDER BY uploaded_at DESC")
    media = cur.fetchall()
    conn.close()
    return render_template("index.html", media=media)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    media_type = request.form["type"]
    title = request.form.get("title", "")

    if file:
        folder = "static/uploads"
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, file.filename)
        file.save(filepath)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO media (type, filename, title) VALUES (%s, %s, %s)",
                    (media_type, file.filename, title))
        conn.commit()
        conn.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
