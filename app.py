from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ---------- Config ----------
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///files.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Create upload folder
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------- Model ----------
class File(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255)
    )

with app.app_context():
    db.create_all()

# ---------- Upload ----------
@app.route(
    "/upload",
    methods=["POST"]
)
def upload_file():

    if "file" not in request.files:

        return jsonify({
            "message": "No file uploaded"
        }), 400

    file = request.files["file"]

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    record = File(
        filename=file.filename
    )

    db.session.add(record)
    db.session.commit()

    return jsonify({
        "message": "File uploaded",
        "filename": file.filename
    })

# ---------- List Files ----------
@app.route("/files")
def files():

    data = File.query.all()

    return jsonify([
        {
            "id": f.id,
            "filename": f.filename
        }
        for f in data
    ])

# ---------- Download ----------
@app.route("/download/<filename>")
def download(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )

# ---------- Delete ----------
@app.route(
    "/delete/<int:file_id>",
    methods=["DELETE"]
)
def delete_file(file_id):

    file = File.query.get(file_id)

    if not file:
        return jsonify({
            "message": "File not found"
        }), 404

    path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    if os.path.exists(path):
        os.remove(path)

    db.session.delete(file)
    db.session.commit()

    return jsonify({
        "message": "File deleted"
    })

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
