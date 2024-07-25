import secrets 
SQLALCHEMY_DATABASE_URI = 'sqlite:///maindb.db' #Configure a DB using SQLite
SECRET_KEY = '4af22bddb1f59cf92f1b6ce124eade2c' #Configure a security key to ensure a secure connection
BCRYPT_LEVEL = 10 #Rounds of hashing for passwords to ensure secure