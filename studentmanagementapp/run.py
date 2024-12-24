from app import app, db, migrate
from app import index

if __name__ == "__main__":
    from app import admin
    app.run(debug=True)

