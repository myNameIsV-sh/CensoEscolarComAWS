from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.get("/")
def hello_world():
    return jsonify({"message": "Hello, World!"}), 200

if __name__ == "__main__":
    app.run(debug=True)