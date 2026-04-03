"""
Production API Server for Avian AI - Synchronous Model Loading
Clean Flask API for bird sound classification
"""

import sys
import os

# CRITICAL: Reduce memory usage for Render 512MB limit
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

# Set absolute base directory and ensure it's in Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print(f"🐍 Python version: {sys.version}")
print(f"🐍 Python executable: {sys.executable}")
print(f"📁 BASE_DIR: {BASE_DIR}")
print(f"🧠 Memory optimization: Single-threaded mode enabled")
print(f"🐍 Python path includes BASE_DIR: {BASE_DIR in sys.path}")

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import tempfile
import requests
from pathlib import Path

# Model configuration with absolute paths
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "best_model.pth")
MODEL_URL = os.environ.get("MODEL_URL", "https://github.com/murtuja55/avian-ai/releases/download/v1.0.0/best_model.pth")

print(f"📁 MODEL_DIR: {MODEL_DIR}")
print(f"📁 MODEL_PATH: {MODEL_PATH}")
print(f"📁 MODEL_URL: {MODEL_URL}")

def download_model():
    """Download model synchronously before server starts"""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    if os.path.exists(MODEL_PATH):
        print(f"✅ Model already exists at {MODEL_PATH}")
        print(f"✅ Model size: {os.path.getsize(MODEL_PATH) / (1024*1024):.1f} MB")
        return True
    
    print(f"📥 Downloading model from {MODEL_URL}")
    print(f"📥 Target path: {MODEL_PATH}")
    
    try:
        print("🌐 Starting HTTP request...")
        response = requests.get(MODEL_URL, stream=True, timeout=300)
        response.raise_for_status()
        print("✅ HTTP request successful")
        
        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        
        print(f"📥 Downloading model ({total / (1024*1024):.1f} MB)...")
        
        with open(MODEL_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        progress = (downloaded / total) * 100
                        print(f"📥 Download progress: {progress:.1f}%", end='\r')
        
        print(f"\n✅ Model downloaded: {MODEL_PATH} ({downloaded} bytes)")
        print(f"✅ Model size: {os.path.getsize(MODEL_PATH) / (1024*1024):.1f} MB")
        
        # Verify model exists
        if os.path.exists(MODEL_PATH):
            print("✅ Model verification passed")
            return True
        else:
            print("❌ Model verification failed - file not found after download")
            return False
            
    except Exception as e:
        print(f"❌ Model download FAILED: {e}")
        # Clean up partial download
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
            print("🗑️ Cleaned up partial download")
        return False

# SYNCHRONOUS MODEL DOWNLOAD - MUST FINISH BEFORE SERVER STARTS
print("🚀 Starting Avian AI...")
print("🔍 Downloading model before server startup...")
if not download_model():
    print("❌ Cannot start without model. Exiting.")
    sys.exit(1)

print("✅ Model ready - initializing Flask app...")

# Initialize Flask app AFTER model is confirmed present
app = Flask(__name__, static_folder='static')
CORS(app, origins=["*"])

# NOW import inference AFTER model is confirmed present
INFERENCE_READY = False
INFERENCE_SYSTEM = None

try:
    print("🧠 Initializing inference system...")
    print(f"🔍 Model file exists: {os.path.exists(MODEL_PATH)}")
    print(f"🔍 Model path: {MODEL_PATH}")
    
    from inference import predict_bird_species
    INFERENCE_SYSTEM = predict_bird_species
    INFERENCE_READY = True
    print("✅ Inference system loaded successfully")
    print("🎯 Predictions are now ready!")
except Exception as e:
    INFERENCE_READY = False
    print(f"❌ Error loading inference system: {e}")
    print("❌ Predictions will not work until this is fixed")

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'ogg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Store uploaded files for serving
uploaded_files = {}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'inference_ready': INFERENCE_READY,
        'model_loaded': os.path.exists(MODEL_PATH),
        'model_path': MODEL_PATH
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict bird species from audio file"""
    if not INFERENCE_READY:
        return jsonify({'error': 'Inference system not ready'}), 500
    
    if not INFERENCE_SYSTEM:
        return jsonify({'error': 'Inference system not available'}), 500
    
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
            prediction = INFERENCE_SYSTEM(temp_path)
            
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
        print(f"❌ Audio serving error: {e}")
        return jsonify({'error': 'Failed to serve audio'}), 500

# Frontend serving routes
@app.route('/')
def serve_index():
    """Serve main frontend page"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"❌ Frontend serving error: {e}")
        return jsonify({'error': 'Frontend not available'}), 404

@app.route('/<path:path>')
def serve_static(path):
    """Serve static frontend files"""
    try:
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        # If static file not found, return index.html for SPA routing
        print(f"📁 Static file not found: {path}, serving index.html instead")
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except Exception as fallback_error:
            print(f"❌ Fallback frontend serving error: {fallback_error}")
            return jsonify({'error': 'Frontend not available'}), 404

@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🔧 Inference ready: {INFERENCE_READY}")
    
    # Use environment PORT for deployment (Render uses PORT env var)
    port = int(os.environ.get("PORT", 10000))
    
    print(f"🌐 Server will run on http://0.0.0.0:{port}")
    print("🚀 Server starting - model already loaded!")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        threaded=True
    )
