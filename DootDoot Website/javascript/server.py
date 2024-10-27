from flask import Flask, request, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'filename' not in request.files:
        return "No file part", 400
    file = request.files['filename']
    if file.filename == '':
        return "No selected file", 400

    file.save(os.path.join('uploads'), file.filename)  # Ensure 'uploads' directory exists
    
    # Here you would convert the file and generate a PDF
    # sends pdf it back
    pdf_path = os.path.join('uploads', 'music_sheet.pdf')  # Path to generated PDF
    return send_file(pdf_path, as_attachment=True)  # Sends the PDF file as a response

if __name__ == '__main__':
    app.run(debug=True)
