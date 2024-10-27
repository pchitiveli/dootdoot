from flask import Flask, request, send_file
from flask_cors import CORS
import os
import AudioUtil

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'filename' not in request.files:
        return "No file part", 400

    file = request.files['filename']
    
    if file.filename == '':
        return "No selected file", 400

    # Save the uploaded file to the UPLOAD_FOLDER
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    #Generate the PDF using music_notator and retrieve the path
    pdf_path = AudioUtil.music_notator(file_path)

    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        return "PDF not generated", 500

if __name__ == '__main__':
    app.run(debug=True)
