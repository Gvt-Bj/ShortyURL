# app.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
import random
import string

app = FastAPI()

# Initialize SQLite database
conn = sqlite3.connect("urls.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short TEXT UNIQUE,
    full TEXT
)
""")
conn.commit()

# Helper function to generate short URL
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Home page with inline CSS
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>URL Shortener</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }
                input[type="url"] { width: 80%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ccc; }
                button { padding: 10px 20px; border: none; background: #4CAF50; color: white; border-radius: 5px; cursor: pointer; }
                button:hover { background: #45a049; }
                a { color: #4CAF50; text-decoration: none; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Simple URL Shortener</h1>
                <form action="/shorten" method="post">
                    <input type="url" name="full_url" placeholder="Enter URL" required>
                    <br>
                    <button type="submit">Shorten</button>
                </form>
            </div>
        </body>
    </html>
    """

# Shorten URL
@app.post("/shorten")
async def shorten(full_url: str = Form(...)):
    short_code = generate_short_code()
    cursor.execute("INSERT INTO urls (short, full) VALUES (?, ?)", (short_code, full_url))
    conn.commit()
    return HTMLResponse(f"""
        <html>
            <head>
                <title>URL Created</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }}
                    a {{ color: #4CAF50; text-decoration: none; font-weight: bold; }}
                    a:hover {{ text-decoration: underline; }}
                    button {{ padding: 10px 20px; border: none; background: #4CAF50; color: white; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
                    button:hover {{ background: #45a049; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Short URL Created!</h2>
                    <a href="/{short_code}">http://shortyURL😁/{short_code}</a>
                    <br>
                    <form action="/">
                        <button type="submit">Shorten Another</button>
                    </form>
                </div>
            </body>
        </html>
    """)

# Redirect to full URL
@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    cursor.execute("SELECT full FROM urls WHERE short = ?", (short_code,))
    row = cursor.fetchone()
    if row:
        return RedirectResponse(row[0])
    return HTMLResponse("<h2>URL not found</h2><a href='/'>Go Home</a>")

# Optional: run directly with python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
