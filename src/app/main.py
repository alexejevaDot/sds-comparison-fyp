from flask import Flask, render_template, request
import os
import json
from pathlib import Path
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
    Handle uploaded SDS PDF files, extract their text, detect sections,
    save debug data, and display simple results.
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

    old_sections = sds_parser.split_into_sections(old_text)
    new_sections = sds_parser.split_into_sections(new_text)

    debug_folder = Path("debug_outputs")
    debug_folder.mkdir(exist_ok=True)

    debug_data = {
        "old_text_preview": old_text[:2000],
        "new_text_preview": new_text[:2000],
        "old_sections_found": sorted(old_sections.keys()),
        "new_sections_found": sorted(new_sections.keys()),
        "old_section_lengths": {str(k): len(v) for k, v in old_sections.items()},
        "new_section_lengths": {str(k): len(v) for k, v in new_sections.items()},
        "old_section_preview": {str(k): v[:200] for k, v in old_sections.items()},
        "new_section_preview": {str(k): v[:200] for k, v in new_sections.items()},
    }

    with open(debug_folder / "section_detection_debug.json", "w", encoding="utf-8") as f:
        json.dump(debug_data, f, indent=4, ensure_ascii=False)

    return (
        f"Old SDS length: {len(old_text)} characters<br>"
        f"New SDS length: {len(new_text)} characters<br><br>"
        f"Old SDS sections found: {sorted(old_sections.keys())}<br>"
        f"New SDS sections found: {sorted(new_sections.keys())}<br><br>"
        f"Debug file saved to: debug_outputs/section_detection_debug.json"
    )


if __name__ == '__main__':
    app.run(debug=True)