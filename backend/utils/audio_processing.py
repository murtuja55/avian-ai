"""
Audio Processing Utilities
Clean audio processing functions for bird sound classification
"""

import os
import librosa
import numpy as np
import torch
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Audio processing utilities"""
    
    def __init__(self, sample_rate=22050, n_mels=128, target_length=128):
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.hop_length = 512
        self.n_fft = 2048
        self.target_length = target_length
    
    def load_audio(self, audio_path):
        """Load audio file"""
        try:
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            return audio
        except Exception as e:
            logger.error(f"Error loading audio {audio_path}: {str(e)}")
            return None
    
    def create_mel_spectrogram(self, audio):
        """Create mel spectrogram from audio"""
        try:
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=self.sample_rate,
                n_mels=self.n_mels,
                hop_length=self.hop_length,
                n_fft=self.n_fft
            )
            
            # Convert to log scale
            mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            
            return mel_spec
            
        except Exception as e:
            logger.error(f"Error creating mel spectrogram: {str(e)}")
            return None
    
    def normalize_spectrogram(self, mel_spec):
        """Normalize spectrogram"""
        try:
            # Normalize to [0, 1]
            mel_spec = (mel_spec - mel_spec.min()) / (mel_spec.max() - mel_spec.min())
            return mel_spec
        except Exception as e:
            logger.error(f"Error normalizing spectrogram: {str(e)}")
            return None
    
    def resize_spectrogram(self, mel_spec):
        """Resize spectrogram to target length"""
        try:
            if mel_spec.shape[1] < self.target_length:
                pad_width = self.target_length - mel_spec.shape[1]
                mel_spec = np.pad(mel_spec, ((0, 0), (0, pad_width)), mode='constant')
            else:
                mel_spec = mel_spec[:, :self.target_length]
            return mel_spec
        except Exception as e:
            logger.error(f"Error resizing spectrogram: {str(e)}")
            return None
    
    def preprocess_audio(self, audio_path):
        """Complete audio preprocessing pipeline"""
        try:
            # Load audio
            audio = self.load_audio(audio_path)
            if audio is None:
                return None
            
            # Create mel spectrogram
            mel_spec = self.create_mel_spectrogram(audio)
            if mel_spec is None:
                return None
            
            # Normalize
            mel_spec = self.normalize_spectrogram(mel_spec)
            if mel_spec is None:
                return None
            
            # Resize
            mel_spec = self.resize_spectrogram(mel_spec)
            if mel_spec is None:
                return None
            
            # Convert to tensor and add channel dimension
            mel_spec = torch.FloatTensor(mel_spec).unsqueeze(0)
            
            return mel_spec
            
        except Exception as e:
            logger.error(f"Error preprocessing audio {audio_path}: {str(e)}")
            return None
    
    def validate_audio_file(self, audio_path):
        """Validate audio file"""
        try:
            if not os.path.exists(audio_path):
                return False, "File does not exist"
            
            # Check file extension
            valid_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
            if not any(audio_path.lower().endswith(ext) for ext in valid_extensions):
                return False, "Invalid file format"
            
            # Try to load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            if len(audio) == 0:
                return False, "Empty audio file"
            
            # Check duration (minimum 1 second)
            duration = len(audio) / sr
            if duration < 1.0:
                return False, "Audio too short (minimum 1 second)"
            
            return True, "Valid audio file"
            
        except Exception as e:
            return False, f"Error validating audio: {str(e)}"

def get_audio_processor():
    """Get audio processor instance"""
    return AudioProcessor()

if __name__ == "__main__":
    # Test audio processor
    processor = AudioProcessor()
    print("Audio processor initialized successfully!")
