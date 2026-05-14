from flask import Flask, render_template, request
import os
import json
from pathlib import Path
from . import sds_parser, sds_compare

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
    compare sections, save debug data, and display simple results.
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

    comparison_results = sds_compare.compare_sections(old_sections, new_sections)
    summary = sds_compare.summarize_changes(comparison_results)

    debug_folder = Path("debug_outputs")
    debug_folder.mkdir(exist_ok=True)

    debug_data = {
        "old_text_preview": old_text[:2000],
        "new_text_preview": new_text[:2000],
        "old_sections_found": sorted(old_sections.keys()),
        "new_sections_found": sorted(new_sections.keys()),
        "old_section_lengths": {str(k): len(v) for k, v in old_sections.items()},
        "new_section_lengths": {str(k): len(v) for k, v in new_sections.items()},
        "comparison_results": {str(k): v for k, v in comparison_results.items()},
        "summary": summary,
    }

    with open(debug_folder / "section_detection_debug.json", "w", encoding="utf-8") as f:
        json.dump(debug_data, f, indent=4, ensure_ascii=False)

        section_rows = []

    for section_num, result in comparison_results.items():
        section_rows.append({
            "section_num": section_num,
            "old_present": result["old_present"],
            "new_present": result["new_present"],
            "old_length": result["old_length"],
            "new_length": result["new_length"],
            "changed": result["changed"],
            "old_preview": result["old_preview"],
            "new_preview": result["new_preview"],
            "change_summary": result["change_summary"],
    })
    section_2 = comparison_results.get(2)

    return render_template(
        "results.html",
        old_text_length=len(old_text),
        new_text_length=len(new_text),
        old_sections_found=sorted(old_sections.keys()),
        new_sections_found=sorted(new_sections.keys()),
        summary=summary,
        section_rows=section_rows,
        section_2=section_2,
    )


if __name__ == '__main__':
    app.run(debug=True)