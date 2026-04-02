"""
Production Inference System
Clean bird sound classification with confidence scoring
"""

import os
import json
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
import logging
import warnings
warnings.filterwarnings('ignore')

# Import librosa
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    os.system("pip install librosa")
    import librosa
    LIBROSA_AVAILABLE = True

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BirdModel(nn.Module):
    """Bird Classification Model"""
    
    def __init__(self, num_classes=50):
        super(BirdModel, self).__init__()
        from torchvision import models
        self.backbone = models.resnet18(weights=None)
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_features, num_classes)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        x = self.backbone(x)
        x = self.dropout(x)
        return x

class AudioProcessor:
    """Audio processing for bird sound classification"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.n_mels = 128
        self.n_fft = 512  # FIXED: Was 2048, should be 512 like training
        self.hop_length = 256  # FIXED: Was 512, should be 256 like training
        self.target_length = 128
    
    def load_and_preprocess(self, audio_path):
        """Load and preprocess audio file - EXACT MATCH TO TRAINING"""
        try:
            # Load audio EXACTLY like training
            import librosa
            audio, sr = librosa.load(audio_path, sr=22050, mono=True)
            
            # Fixed length (5 seconds) - EXACT like training
            target_length = 22050 * 5
            if len(audio) < target_length:
                audio = np.pad(audio, (0, target_length - len(audio)))
            else:
                audio = audio[:target_length]
            
            # Create mel spectrogram EXACTLY like training
            mel_spec = librosa.feature.melspectrogram(
                y=audio, 
                sr=22050, 
                n_mels=128, 
                n_fft=512, 
                hop_length=256
            )
            
            # Convert to log scale - EXACT like training
            log_mel = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Normalize EXACTLY like training
            log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-9)
            
            # Convert to tensor EXACTLY like training
            log_mel = torch.FloatTensor(log_mel)
            
            # Resize to 128x128 - EXACT like training
            from torchvision import transforms
            resize_transform = transforms.Resize((128, 128))
            log_mel = resize_transform(log_mel.unsqueeze(0))
            
            # Convert to 3-channel EXACTLY like training
            log_mel = log_mel.repeat(3, 1, 1)
            
            # Add batch dimension - CRITICAL FIX
            log_mel = log_mel.unsqueeze(0)
            
            # Debug prints
            print(f"Input shape: {log_mel.shape}")
            print(f"Mean: {log_mel.mean()}")
            print(f"Std: {log_mel.std()}")
            
            return log_mel
            
        except Exception as e:
            logger.error(f"Error processing audio {audio_path}: {str(e)}")
            return None

class BirdClassifier:
    """Main bird sound classifier"""
    
    def __init__(self, model_path=None, class_names_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.class_names = []
        self.processor = AudioProcessor()
        
        # Default paths
        if model_path is None:
            model_path = Path(__file__).parent / "model" / "best_model.pth"
        if class_names_path is None:
            class_names_path = Path(__file__).parent.parent / "data" / "dataset_50_meaningful_species" / "dataset_metadata.json"
        
        self.load_model(model_path, class_names_path)
    
    def load_model(self, model_path, class_names_path):
        """Load trained model and class names"""
        try:
            # Load model
            self.model = BirdModel(num_classes=50).to(self.device)
            
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                
                # Check if it's a full checkpoint or just state dict
                if 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                    # Also load class names from checkpoint if available
                    if 'class_names' in checkpoint and len(self.class_names) == 0:
                        self.class_names = checkpoint['class_names']
                else:
                    self.model.load_state_dict(checkpoint)
                    
                self.model.eval()
                logger.info(f"Model loaded from {model_path}")
            else:
                logger.error(f"Model file not found: {model_path}")
                return
            
            # Load class names
            if os.path.exists(class_names_path):
                with open(class_names_path, 'r') as f:
                    metadata = json.load(f)
                    species_data = metadata.get('species', [])
                    self.class_names = [item.get('scientific_name', item.get('folder_name', f"Species_{i}")) for i, item in enumerate(species_data)]
                
                if len(self.class_names) == 0:
                    # Fallback class names
                    self.class_names = [f"Species_{i}" for i in range(50)]
                
                logger.info(f"Loaded {len(self.class_names)} class names")
            else:
                logger.warning(f"Class names file not found: {class_names_path}")
                self.class_names = [f"Species_{i}" for i in range(50)]
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
    
    def predict(self, audio_path):
        """Predict bird species from audio file"""
        try:
            if self.model is None:
                return {"error": "Model not loaded"}
            
            # Process audio
            audio_tensor = self.processor.load_and_preprocess(audio_path)
            if audio_tensor is None:
                return {"error": "Failed to process audio"}
            
            # Move to device (batch dimension already added in processor)
            audio_tensor = audio_tensor.to(self.device)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(audio_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            # Get results
            predicted_class = self.class_names[predicted.item()]
            confidence_score = confidence.item()
            
            # Get top 3 predictions
            top3_probs, top3_indices = torch.topk(probabilities, 3)
            top3_predictions = []
            
            for i in range(3):
                class_name = self.class_names[top3_indices[0][i].item()]
                prob = top3_probs[0][i].item()
                top3_predictions.append({
                    "label": class_name,
                    "confidence": prob
                })
            
            return {
                "prediction": predicted_class,
                "confidence": confidence_score,
                "top3": top3_predictions,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {"error": f"Prediction failed: {str(e)}"}

# Global classifier instance
_classifier = None

def get_classifier():
    """Get or create classifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = BirdClassifier()
    return _classifier

def predict_bird_species(audio_path):
    """Convenience function for prediction"""
    classifier = get_classifier()
    return classifier.predict(audio_path)

if __name__ == "__main__":
    # Test the classifier
    classifier = BirdClassifier()
    print("Bird classifier initialized successfully!")
    print(f"Device: {classifier.device}")
    print(f"Number of classes: {len(classifier.class_names)}")
