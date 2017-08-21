from flask import Flask
import psycopg2

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello"

@app.route('/db')
def db():
    connect_str = " dbname='myproject' user='myprojectuser' password='password' host='postgres' port='5432' "
    connectionToDb = psycopg2.connect(connect_str)
    cursor = connectionToDb.cursor()
    cursor.execute("DROP TABLE IF EXISTS test;")
    cursor.execute("CREATE TABLE test(key text, value text);")
    cursor.execute("INSERT INTO test VALUES (%s, %s);", ("Some key", "Some value") )
    cursor.execute( "SELECT value FROM test WHERE key = %s;" , ("Some key", ) )
    res = cursor.fetchone()
    val = res[0]
    connectionToDb.close()
    return val

@app.route('/drop')
def drop():
    connect_str = " dbname='myproject' user='myprojectuser' host='localhost' password='password' "
    connectionToDb = psycopg2.connect(connect_str)
    cursor = connectionToDb.cursor()
    cursor.execute("DROP TABLE IF EXISTS test;")
    connectionToDb.close()
    return "Dropped"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
