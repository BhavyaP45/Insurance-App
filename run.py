# Import modules needed.
from docs import app, db
from os import path


if __name__ == '__main__':
    if not path.exists('instance/maindata.db'):
        with app.app_context():
            db.create_all()
    app.run(debug = True)