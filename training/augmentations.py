"""
Training Pipeline Detector
Determines which training pipeline was actually used
"""

import os
import json
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
import logging
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Import both audio libraries
try:
    import torchaudio
    TORCHAUDIO_AVAILABLE = True
except ImportError:
    TORCHAUDIO_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrainingPipelineDetector:
    """Detects which training pipeline was actually used"""
    
    def __init__(self, model_path="best_model.pth", dataset_path="dataset_50_meaningful_species"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = Path(model_path)
        self.dataset_path = Path(dataset_path)
        
        logger.info("🔍 TRAINING PIPELINE DETECTOR")
        logger.info("=" * 80)
        
        self.load_model()
        self.load_dataset_info()
    
    def load_model(self):
        """Load model and check architecture"""
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Check model architecture
        self.class_names = checkpoint['class_names']
        self.class_to_idx = checkpoint['class_to_idx']
        
        logger.info(f"✅ Model loaded")
        logger.info(f"   Classes: {len(self.class_names)}")
        
        # Check if model has pretrained weights indicator
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            
            # Check conv1 layer - this will tell us which training script was used
            if 'backbone.conv1.weight' in state_dict:
                conv1_weight = state_dict['backbone.conv1.weight']
                logger.info(f"   Conv1 weight shape: {conv1_weight.shape}")
                
                # If conv1 was modified (like in train_bird_model.py), it will be (64, 3, 7, 7)
                # If not modified (like in simple_bird_trainer.py), it will be (64, 3, 7, 7) but with different initialization
                if conv1_weight.shape == torch.Size([64, 3, 7, 7]):
                    logger.info("   ✅ Conv1 layer matches 3-channel input (both scripts)")
                else:
                    logger.info(f"   ❌ Unexpected conv1 shape: {conv1_weight.shape}")
            
            # Check if backbone has pretrained weights
            if 'backbone.layer1.0.conv1.weight' in state_dict:
                layer1_weight = state_dict['backbone.layer1.0.conv1.weight']
                logger.info(f"   Layer1 weight shape: {layer1_weight.shape}")
                logger.info(f"   Layer1 weight mean: {layer1_weight.mean():.6f}")
                logger.info(f"   Layer1 weight std: {layer1_weight.std():.6f}")
                
                # Pretrained weights will have specific statistics
                if abs(layer1_weight.mean()) < 0.1 and layer1_weight.std() > 0.1:
                    logger.info("   ✅ Likely pretrained weights (like simple_bird_trainer.py)")
                else:
                    logger.info("   ❌ Likely random initialization")
    
    def load_dataset_info(self):
        """Load dataset information"""
        metadata_path = self.dataset_path / "dataset_metadata.json"
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        logger.info(f"📊 Dataset info loaded")
        logger.info(f"   Species: {len(self.metadata['species'])}")
    
    def test_both_pipelines(self, num_samples=10):
        """Test both librosa and torchaudio pipelines"""
        logger.info("🔍 TESTING BOTH PIPELINES")
        logger.info("=" * 80)
        
        # Collect test files
        all_audio_files = []
        raw_dir = self.dataset_path / "raw"
        
        for species in self.metadata['species']:
            folder_name = species['folder_name']
            scientific_name = species['scientific_name']
            
            species_folder = raw_dir / folder_name
            if species_folder.exists():
                for audio_file in species_folder.glob("*.ogg"):
                    all_audio_files.append((str(audio_file), scientific_name))
        
        # Sample test files
        np.random.shuffle(all_audio_files)
        test_files = all_audio_files[:num_samples]
        
        logger.info(f"📊 Testing {len(test_files)} files with both pipelines")
        
        # Test both pipelines
        librosa_results = []
        torchaudio_results = []
        
        for audio_path, true_species in test_files:
            logger.info(f"\n🔍 Testing: {audio_path}")
            logger.info(f"   True species: {true_species}")
            
            # Test librosa pipeline
            try:
                librosa_pred = self.test_librosa_pipeline(audio_path)
                librosa_results.append({
                    'path': audio_path,
                    'true': true_species,
                    'pred': librosa_pred,
                    'correct': librosa_pred == true_species
                })
                logger.info(f"   Librosa prediction: {librosa_pred} ({'✅' if librosa_pred == true_species else '❌'})")
            except Exception as e:
                logger.error(f"   Librosa failed: {e}")
            
            # Test torchaudio pipeline
            try:
                torchaudio_pred = self.test_torchaudio_pipeline(audio_path)
                torchaudio_results.append({
                    'path': audio_path,
                    'true': true_species,
                    'pred': torchaudio_pred,
                    'correct': torchaudio_pred == true_species
                })
                logger.info(f"   Torchaudio prediction: {torchaudio_pred} ({'✅' if torchaudio_pred == true_species else '❌'})")
            except Exception as e:
                logger.error(f"   Torchaudio failed: {e}")
        
        # Calculate accuracies
        librosa_accuracy = sum(1 for r in librosa_results if r['correct']) / len(librosa_results) if librosa_results else 0
        torchaudio_accuracy = sum(1 for r in torchaudio_results if r['correct']) / len(torchaudio_results) if torchaudio_results else 0
        
        logger.info(f"\n📊 PIPELINE COMPARISON RESULTS:")
        logger.info(f"   Librosa accuracy: {librosa_accuracy:.2%}")
        logger.info(f"   Torchaudio accuracy: {torchaudio_accuracy:.2%}")
        
        # Determine which pipeline was used
        if librosa_accuracy > torchaudio_accuracy:
            logger.info(f"🎯 CONCLUSION: Model was likely trained with LIBROSA pipeline")
            logger.info(f"   (simple_bird_trainer.py)")
        elif torchaudio_accuracy > librosa_accuracy:
            logger.info(f"🎯 CONCLUSION: Model was likely trained with TORCHAUDIO pipeline")
            logger.info(f"   (train_bird_model.py)")
        else:
            logger.info(f"❌ CONCLUSION: Both pipelines perform similarly - inconclusive")
        
        return librosa_accuracy, torchaudio_accuracy
    
    def test_librosa_pipeline(self, audio_path):
        """Test librosa pipeline (like simple_bird_trainer.py)"""
        # Load audio
        audio, sr = librosa.load(audio_path, sr=22050, mono=True)
        
        # Fixed length
        target_length = 22050 * 5
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            audio = audio[:target_length]
        
        # Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio, 
            sr=22050, 
            n_mels=128, 
            n_fft=512, 
            hop_length=256
        )
        
        # Log conversion
        log_mel = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Normalize
        log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-9)
        
        # Convert to tensor
        log_mel = torch.FloatTensor(log_mel)
        
        # Resize
        from torchvision import transforms
        resize_transform = transforms.Resize((128, 128))
        log_mel = resize_transform(log_mel.unsqueeze(0))
        
        # 3-channel
        log_mel = log_mel.repeat(3, 1, 1)
        
        # Get prediction
        return self.get_prediction(log_mel)
    
    def test_torchaudio_pipeline(self, audio_path):
        """Test torchaudio pipeline (like train_bird_model.py)"""
        # Load audio
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # Mono
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        # Resample
        if sample_rate != 22050:
            resampler = torchaudio.transforms.Resample(sample_rate, 22050)
            waveform = resampler(waveform)
        
        # Pad/truncate
        target_length = 22050 * 5
        if waveform.shape[1] < target_length:
            padding = target_length - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, padding))
        else:
            waveform = waveform[:, :target_length]
        
        # Mel spectrogram
        mel_spectrogram = torchaudio.transforms.MelSpectrogram(
            sample_rate=22050,
            n_fft=512,
            hop_length=256,
            n_mels=128
        )(waveform)
        
        # Log conversion
        log_mel = torch.log(mel_spectrogram + 1e-9)
        
        # Normalize
        log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-9)
        
        # Resize
        from torchvision import transforms
        resize_transform = transforms.Resize((128, 128))
        log_mel = resize_transform(log_mel)
        
        # 3-channel
        log_mel = log_mel.repeat(3, 1, 1)
        
        # Get prediction
        return self.get_prediction(log_mel)
    
    def get_prediction(self, audio_tensor):
        """Get prediction from model"""
        # Load model
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Create model (simple version like simple_bird_trainer.py)
        from torchvision import models
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, 50)
        model.dropout = nn.Dropout(0.5)
        
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        model.to(self.device)
        
        # Get prediction
        with torch.no_grad():
            audio_tensor = audio_tensor.unsqueeze(0).to(self.device)
            outputs = model(audio_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            _, predicted = torch.max(probabilities, 1)
            
            species_idx = predicted.cpu().numpy()[0]
            return self.class_names[species_idx]

def main():
    """Main function"""
    logger.info("🔍 TRAINING PIPELINE DETECTOR")
    logger.info("🎯 GOAL: Determine which training pipeline was actually used")
    logger.info("=" * 80)
    
    if not TORCHAUDIO_AVAILABLE:
        logger.error("❌ Torchaudio not available!")
        return
    
    if not LIBROSA_AVAILABLE:
        logger.error("❌ Librosa not available!")
        return
    
    # Initialize detector
    try:
        detector = TrainingPipelineDetector()
        
        # Test both pipelines
        librosa_acc, torchaudio_acc = detector.test_both_pipelines(num_samples=10)
        
        logger.info("\n🎉 PIPELINE DETECTION COMPLETED!")
        
        return detector
        
    except Exception as e:
        logger.error(f"❌ Pipeline detection failed: {str(e)}")
        return None

if __name__ == "__main__":
    detector = main()
