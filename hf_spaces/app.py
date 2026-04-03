"""
Hugging Face Spaces Backend for Avian AI
Bird Sound Recognition with Gradio Interface
"""

import gradio as gr
import torch
import torchaudio
import librosa
import numpy as np
import os
import sys
from pathlib import Path
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
    """Audio processing for bird sound classification"""
    
    def __init__(self, sample_rate=22050, duration=5.0):
        self.sample_rate = sample_rate
        self.duration = duration
        self.n_mels = 128
        self.n_fft = 2048
        self.hop_length = 512
        self.target_length = 128
    
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

# Global variables for lazy loading
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
        
        # Load state dict with compatibility for different PyTorch versions
        try:
            checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
        except:
            # Fallback for newer PyTorch versions
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
    """Main prediction function for Gradio"""
    if audio_file is None:
        return "Please upload an audio file"
    
    try:
        # Load model lazily
        model = load_model()
        global _processor
        
        # Process audio
        audio_tensor = _processor.load_and_preprocess(audio_file)
        if audio_tensor is None:
            return "Error: Failed to process audio file"
        
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
            top3_predictions.append(f"{i+1}. {class_name} ({prob:.3f})")
        
        # Format output
        result = f"**Prediction:** {predicted_class}\n"
        result += f"**Confidence:** {confidence_score:.3f} ({confidence_score*100:.1f}%)\n\n"
        result += "**Top 3 Predictions:**\n"
        result += "\n".join(top3_predictions)
        
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Cleanup
        import gc
        gc.collect()

# Create Gradio interface
def create_interface():
    """Create and return Gradio interface"""
    
    interface = gr.Interface(
        fn=predict_bird,
        inputs=gr.Audio(
            sources=["upload", "microphone"],
            type="filepath",
            label="Upload Bird Audio File"
        ),
        outputs=gr.Textbox(
            label="Prediction Results",
            lines=8,
            max_lines=10
        ),
        title="🐦 Avian AI - Bird Sound Recognition",
        description="Upload an audio file of a bird sound to identify the species. Works with common bird species with high accuracy.",
        allow_flagging="never"
    )
    
    return interface

# Launch the interface
if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
