from flask import Flask, request, jsonify, render_template
import os
import requests

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

API_URL = "https://mlbb-api.example.com/check"  # Replace with the actual API endpoint

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check", methods=["POST"])
def check():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    results = check_accounts(file_path)
    os.remove(file_path)  # Cleanup uploaded file
    return jsonify(results)

def check_accounts(file_path):
    working_accounts = []
    with open(file_path, "r") as f:
        accounts = f.readlines()

    for account in accounts:
        username, password = account.strip().split(",")
        payload = {"username": username, "password": password}
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                status = "Working" if data.get("valid") else "Invalid"
                working_accounts.append({"username": username, "status": status})
            else:
                working_accounts.append({"username": username, "status": "Error"})
        except:
            working_accounts.append({"username": username, "status": "Error"})

    return working_accounts

if __name__ == "__main__":
    app.run(debug=True)
