from flask import Flask, render_template, request
import os
from . import sds_parser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(
    os.path.dirname(__file__), '..', '..', 'data', 'uploads'
)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET'])
def index():

    """
    Display the home page with the SDS upload form.
    """
    return render_template('upload.html')

@app.route('/compare', methods=['POST'])
def compare():

    """
    Handle uploaded SDS PDF files, extract their text, and pass results
    to the comparison template for display.
    """
    
    old_file = request.files.get('old_sds')
    new_file = request.files.get('new_sds')

    if not old_file or not new_file:
        return "Please upload both SDS files.", 400

    old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'old_sds.pdf')
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], 'new_sds.pdf')

    old_file.save(old_path)
    new_file.save(new_path)

    old_text = sds_parser.extract_text_from_pdf(old_path)
    new_text = sds_parser.extract_text_from_pdf(new_path)

    return (
        f"Old SDS length: {len(old_text)} characters<br>"
        f"New SDS length: {len(new_text)} characters"
    )

if __name__ == '__main__':
    app.run(debug=True)