from app import create_app
#import pymysql 
#pymysql.install_as_MySQLdb()

from dotenv import load_dotenv
load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
