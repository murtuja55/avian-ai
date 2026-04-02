"""
Production API Server for Avian AI Frontend
Clean Flask API for bird sound classification
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import uuid
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.append('.')

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'ogg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize inference system
try:
    from inference import predict_bird_species
    INFERENCE_READY = True
    print("✅ Inference system loaded successfully")
except Exception as e:
    INFERENCE_READY = False
    print(f"❌ Error loading inference system: {e}")

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'inference_ready': INFERENCE_READY,
        'version': '1.0.0'
    })

# Store uploaded files for serving
uploaded_files = {}

@app.route('/predict', methods=['POST'])
def predict():
    """Predict bird species from audio file"""
    if not INFERENCE_READY:
        return jsonify({'error': 'Inference system not ready'}), 500
    
    try:
        # Check if file is in request
        if 'file' not in request.files:
            print("❌ No file provided in request")
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("❌ No filename provided")
            return jsonify({'error': 'No file selected'}), 400
        
        print(f"📁 File received: {file.filename}")
        print(f"📊 File size: {len(file.read())} bytes")
        file.seek(0)  # Reset file pointer
        
        # Validate file
        if not allowed_file(file.filename):
            print(f"❌ Invalid file format: {file.filename}")
            return jsonify({'error': 'Invalid file format. Allowed formats: WAV, MP3, FLAC, M4A, OGG'}), 400
        
        # Save uploaded file with unique name
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        temp_filename = f"avian_ai_{unique_id}_{filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        # Store file for serving
        uploaded_files[unique_id] = temp_filename
        
        file.save(temp_path)
        print(f"💾 File saved to: {temp_path}")
        
        try:
            # Make prediction
            print("🧠 Starting prediction...")
            prediction = predict_bird_species(temp_path)
            
            # Debug logging
            print("Prediction result:", prediction)
            
            if prediction.get('error'):
                print("❌ Prediction failed:", prediction['error'])
                # Clean up temp file on error
                try:
                    os.remove(temp_path)
                except:
                    pass
                return jsonify({
                    'success': False,
                    'error': prediction['error']
                }), 500
            
            # Log successful prediction
            print(f"✅ Prediction successful: {prediction['prediction']} (confidence: {prediction['confidence']:.3f})")
            
            # Return successful prediction with exact format
            # DO NOT delete temp file - keep for audio serving
            return jsonify({
                'success': True,
                'prediction': prediction['prediction'],
                'confidence': prediction['confidence'],
                'top_predictions': prediction['top3'],
                'audio_url': f'/api/audio/{unique_id}'
            })
            
        except Exception as e:
            print(f"❌ Prediction exception: {str(e)}")
            # Clean up temp file on error
            try:
                os.remove(temp_path)
            except:
                pass
            raise e
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/audio/<unique_id>')
def serve_audio(unique_id):
    """Serve uploaded audio files"""
    try:
        if unique_id in uploaded_files:
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_files[unique_id])
            if os.path.exists(audio_path):
                return send_file(audio_path, as_attachment=False, mimetype='audio/mpeg')
        return jsonify({'error': 'Audio file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to serve audio: {str(e)}'}), 500

@app.route('/species', methods=['GET'])
def get_species():
    """Get list of supported bird species"""
    try:
        from inference import get_classifier
        classifier = get_classifier()
        return jsonify({
            'species': classifier.class_names,
            'count': len(classifier.class_names)
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get species list: {str(e)}'}), 500

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    try:
        from inference import get_classifier
        classifier = get_classifier()
        return jsonify({
            'model_loaded': classifier.model is not None,
            'device': str(classifier.device),
            'num_classes': len(classifier.class_names),
            'sample_rate': classifier.processor.sample_rate,
            'n_mels': classifier.processor.n_mels
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get model info: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({'error': 'Internal server error'}), 500

# Frontend serving routes
@app.route('/')
def serve_index():
    """Serve the main frontend page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static frontend files"""
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    print("🚀 Starting Avian AI API Server...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🔧 Inference ready: {INFERENCE_READY}")
    print(f"🌐 Server will run on http://localhost:5000")
    
    # Use environment PORT for deployment
    port = int(os.environ.get('PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
