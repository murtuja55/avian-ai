"""
Flask Backend for Hugging Face Spaces - Bird Sound Recognition
Alternative to Gradio with REST API endpoints
"""

import os
import sys
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import librosa
import numpy as np
from werkzeug.utils import secure_filename
import warnings
warnings.filterwarnings('ignore')

# Force CPU mode
torch.set_grad_enabled(False)
device = torch.device('cpu')

# Model configuration
MODEL_PATH = "best_model.pth"

# Class names (top 50 bird species)
CLASS_NAMES = [
    "American Robin", "Blue Jay", "Cardinal", "Chickadee", "Crow",
    "Dove", "Eagle", "Finch", "Goose", "Hawk",
    "Hummingbird", "Junco", "Kinglet", "Loon", "Mallard",
    "Nuthatch", "Oriole", "Pelican", "Quail", "Robin",
    "Sparrow", "Titmouse", "Upland Sandpiper", "Vulture", "Warbler",
    "Woodpecker", "Yellowhammer", "Zebra Finch", "Barn Owl", "Snowy Owl",
    "Great Horned Owl", "Barred Owl", "Screech Owl", "Hawk Owl", "Eagle Owl",
    "Kestrel", "Merlin", "Peregrine Falcon", "Prairie Falcon", "Gyrfalcon",
    "Red-tailed Hawk", "Cooper's Hawk", "Sharp-shinned Hawk", "Broad-winged Hawk", "Swainson's Hawk",
    "Rough-legged Hawk", "Ferruginous Hawk", "Swamp Harrier", "Northern Harrier", "White-tailed Kite"
]

class BirdModel(torch.nn.Module):
    """Bird Classification Model"""
    
    def __init__(self, num_classes=50):
        super(BirdModel, self).__init__()
        from torchvision import models
        self.backbone = models.resnet18(weights=None)
        num_features = self.backbone.fc.in_features
        self.backbone.fc = torch.nn.Linear(num_features, num_classes)
        self.dropout = torch.nn.Dropout(0.5)
    
    def forward(self, x):
        x = self.backbone(x)
        x = self.dropout(x)
        return x

class AudioProcessor:
    """Audio processing for bird sound recognition"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.n_mels = 128
        self.n_fft = 2048
        self.hop_length = 512
        self.duration = 5.0
    
    def load_and_preprocess(self, audio_path):
        """Load and preprocess audio file"""
        try:
            if audio_path is None:
                return None
            
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, duration=self.duration)
            
            # Ensure minimum duration
            target_samples = int(self.sample_rate * self.duration)
            if len(audio) < target_samples:
                # Pad with zeros
                padding = target_samples - len(audio)
                audio = np.pad(audio, (0, padding), mode='constant')
            elif len(audio) > target_samples:
                # Trim to target length
                audio = audio[:target_samples]
            
            # Convert to mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=self.sample_rate,
                n_mels=self.n_mels,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            
            # Convert to log scale
            log_mel = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Normalize
            log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-8)
            
            # Resize to 128x128
            from torchvision import transforms
            resize_transform = transforms.Resize((128, 128))
            log_mel_tensor = torch.FloatTensor(log_mel)
            log_mel_resized = resize_transform(log_mel_tensor.unsqueeze(0))
            
            # Convert to 3 channels (duplicate mono channel)
            log_mel_3ch = log_mel_resized.repeat(3, 1, 1)
            
            # Add batch dimension: [1, 3, 128, 128]
            log_mel_3ch = log_mel_3ch.unsqueeze(0)
            
            return log_mel_3ch
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            return None

# Global variables
_model = None
_processor = None

def load_model():
    """Load model lazily"""
    global _model, _processor
    
    if _model is not None:
        return _model
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    
    try:
        # Initialize processor
        _processor = AudioProcessor()
        
        # Load model
        _model = BirdModel(num_classes=50).to(device)
        
        # Load state dict
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        if 'model_state_dict' in checkpoint:
            _model.load_state_dict(checkpoint['model_state_dict'])
        else:
            _model.load_state_dict(checkpoint)
        
        _model.eval()
        return _model
        
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}")

def predict_bird(audio_file):
    """Main prediction function"""
    if audio_file is None:
        return {"error": "Please upload an audio file"}
    
    try:
        # Load model lazily
        model = load_model()
        global _processor
        
        print(f"🎵 Processing audio: {audio_file}")
        
        # Process audio
        audio_tensor = _processor.load_and_preprocess(audio_file)
        if audio_tensor is None:
            print("❌ Audio processing failed")
            return {"error": "Failed to process audio file"}
        
        print(f"🧠 Audio tensor shape: {audio_tensor.shape}")
        print("🧠 Running prediction...")
        
        # Make prediction
        with torch.no_grad():
            outputs = model(audio_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        # Get results
        predicted_class = CLASS_NAMES[predicted.item()]
        confidence_score = confidence.item()
        
        # Get top 3 predictions
        top3_probs, top3_indices = torch.topk(probabilities, 3)
        top3_predictions = []
        
        for i in range(3):
            class_name = CLASS_NAMES[top3_indices[0][i].item()]
            prob = top3_probs[0][i].item()
            top3_predictions.append({
                "label": class_name,
                "confidence": prob
            })
        
        result = {
            "success": True,
            "prediction": predicted_class,
            "confidence": confidence_score,
            "top_predictions": top3_predictions
        }
        
        print(f"✅ Prediction successful: {predicted_class}")
        print(f"✅ Confidence: {confidence_score:.3f}")
        return result
        
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return {"error": str(e)}
    finally:
        # Cleanup
        import gc
        gc.collect()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'ogg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Main prediction endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Allowed: WAV, MP3, FLAC, M4A, OGG'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Make prediction
            result = predict_bird(filepath)
            
            if 'error' in result:
                return jsonify(result), 500
            
            return jsonify(result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': os.path.exists(MODEL_PATH),
        'service': 'avian-ai-backend'
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Avian AI Backend API',
        'endpoints': {
            '/predict': 'POST - Upload audio file for bird species prediction',
            '/health': 'GET - Health check'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Avian AI Flask Backend...")
    print(f"📁 Model path: {MODEL_PATH}")
    print(f"📁 Model exists: {os.path.exists(MODEL_PATH)}")
    
    app.run(
        host="0.0.0.0",
        port=7860,
        debug=False
    )
