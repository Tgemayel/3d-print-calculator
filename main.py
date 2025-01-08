import os
import logging
from flask import Flask, request, jsonify, render_template, abort
from werkzeug.utils import secure_filename
import tempfile
from utils.stl_processor import process_stl_file
from utils.gcode_analyzer import analyze_gcode

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_EXTENSIONS'] = ['.stl']

@app.route('/')
def documentation():
    """Render API docs"""
    return render_template('documentation.html')

@app.route('/estimate', methods=['POST'])
def estimate_print():
    """Upload STL file and return print estimates"""
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("No file selected")
        return jsonify({'error': 'No file selected'}), 400

    # Get material type from request, default to PLA
    material_type = request.form.get('material_type', 'PLA').upper()

    # Validate material type
    valid_materials = ['PLA', 'ABS', 'PETG', 'TPU']
    if material_type not in valid_materials:
        logger.error(f"Invalid material type: {material_type}")
        return jsonify({'error': f'Invalid material type. Must be one of: {", ".join(valid_materials)}'}), 400

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
        logger.error(f"Invalid file extension: {file_ext}")
        return jsonify({'error': 'Invalid file type. Only .stl files are allowed'}), 400

    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as temp_file:
            file.save(temp_file.name)

            # Process STL file
            gcode_data = process_stl_file(temp_file.name)

            # Analyze G-code for estimates
            estimates = analyze_gcode(gcode_data, material_type)

            # Clean up temporary file
            os.unlink(temp_file.name)

            return jsonify({
                'success': True,
                'estimates': {
                    'build_time_minutes': estimates['print_time'],
                    'material_usage_grams': estimates['material_usage'],
                    'estimated_cost': estimates['cost'],
                    'material_type': estimates['material_type'],
                    'price_per_kg': estimates['price_per_kg']
                }
            })

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': 'Error processing STL file'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)