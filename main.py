from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from waitress import serve
from app.api import api  


app = Flask(__name__)


swagger = Swagger(app)


CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})


app.register_blueprint(api,url_prefix="/api")


@app.route("/")
def home():
    return {"message": "Coin Dashboard API is running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
