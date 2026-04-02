"""
Complete Bird Sound Classification Model Training
Using dataset_50_meaningful_species with 50 species
"""

import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import models, transforms
import torchaudio
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report
import logging
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BirdAudioDataset(Dataset):
    """Custom Dataset for Bird Audio Classification"""
    
    def __init__(self, root_dir, transform=None, sample_rate=22050, n_mels=128, n_fft=512, hop_length=256):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length
        
        # Load species information
        self.species_data = self._load_species_data()
        self.audio_files = self._load_audio_files()
        self.class_to_idx = {species['scientific_name']: idx for idx, species in enumerate(self.species_data)}
        self.idx_to_class = {idx: species for idx, species in enumerate(self.species_data)}
        
        logger.info(f"🎯 Loaded {len(self.audio_files)} audio files")
        logger.info(f"🐦 Number of species: {len(self.species_data)}")
    
    def _load_species_data(self):
        """Load species information from metadata"""
        metadata_path = self.root_dir / "dataset_metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return metadata['species']
    
    def _load_audio_files(self):
        """Load all audio file paths and labels"""
        audio_files = []
        raw_dir = self.root_dir / "raw"
        
        for species_folder in raw_dir.iterdir():
            if species_folder.is_dir():
                # Find species info
                species_name = None
                for species in self.species_data:
                    if species['folder_name'] == species_folder.name:
                        species_name = species['scientific_name']
                        break
                
                if species_name:
                    for audio_file in species_folder.glob("*.ogg"):
                        audio_files.append((str(audio_file), species_name))
        
        return audio_files
    
    def __len__(self):
        return len(self.audio_files)
    
    def __getitem__(self, idx):
        audio_path, species_name = self.audio_files[idx]
        
        # Load audio
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
        except ImportError:
            # Fallback to soundfile if torchaudio fails
            import soundfile as sf
            audio_data, sample_rate = sf.read(audio_path)
            waveform = torch.from_numpy(audio_data).float().unsqueeze(0)
            if waveform.shape[0] > 1:
                waveform = waveform.T  # Convert to (channels, samples) format
        
        # Convert to mono if needed
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        # Resample if needed
        if sample_rate != self.sample_rate:
            resampler = torchaudio.transforms.Resample(sample_rate, self.sample_rate)
            waveform = resampler(waveform)
        
        # Pad or truncate to fixed length (target 5 seconds)
        target_length = self.sample_rate * 5  # 5 seconds
        if waveform.shape[1] < target_length:
            # Pad with zeros
            padding = target_length - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, padding))
        else:
            # Truncate
            waveform = waveform[:, :target_length]
        
        # Convert to log-mel spectrogram
        mel_spectrogram = torchaudio.transforms.MelSpectrogram(
            sample_rate=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=self.n_mels
        )(waveform)
        
        # Convert to log scale
        log_mel = torch.log(mel_spectrogram + 1e-9)
        
        # Normalize
        log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-9)
        
        # Resize to fixed size (128x128) for ResNet
        resize_transform = transforms.Resize((128, 128))
        log_mel = resize_transform(log_mel)
        
        # Convert to 3-channel (for ResNet)
        log_mel = log_mel.repeat(3, 1, 1)
        
        # Get label
        label = self.class_to_idx[species_name]
        
        if self.transform:
            log_mel = self.transform(log_mel)
        
        return log_mel, label

class BirdClassifier(nn.Module):
    """Bird Sound Classification Model using ResNet18"""
    
    def __init__(self, num_classes=50):
        super(BirdClassifier, self).__init__()
        
        # Load pretrained ResNet18
        self.backbone = models.resnet18(pretrained=True)
        
        # Modify first conv layer for spectrogram input
        self.backbone.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        
        # Replace final layer
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_features, num_classes)
        
        # Add dropout for regularization
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, x):
        x = self.backbone(x)
        x = self.dropout(x)
        return x

class ModelTrainer:
    """Model Training Class"""
    
    def __init__(self, dataset_path, output_dir="trained_models"):
        self.dataset_path = Path(dataset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Device setup
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"🎯 Using device: {self.device}")
        
        # Training parameters
        self.batch_size = 32
        self.learning_rate = 0.001
        self.num_epochs = 40
        self.train_split = 0.8
        
        # Data transforms
        self.transform = transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.RandomRotation(degrees=10),
        ])
        
        # Initialize dataset
        self.dataset = BirdAudioDataset(
            root_dir=self.dataset_path,
            transform=self.transform
        )
        
        # Split dataset
        train_size = int(self.train_split * len(self.dataset))
        val_size = len(self.dataset) - train_size
        self.train_dataset, self.val_dataset = random_split(
            self.dataset, [train_size, val_size]
        )
        
        # Data loaders
        self.train_loader = DataLoader(
            self.train_dataset, 
            batch_size=self.batch_size, 
            shuffle=True,
            num_workers=0,  # Disable multiprocessing
            pin_memory=False
        )
        
        self.val_loader = DataLoader(
            self.val_dataset, 
            batch_size=self.batch_size, 
            shuffle=False,
            num_workers=0,  # Disable multiprocessing
            pin_memory=False
        )
        
        logger.info(f"📊 Training samples: {len(self.train_dataset)}")
        logger.info(f"📊 Validation samples: {len(self.val_dataset)}")
        
        # Initialize model
        self.model = BirdClassifier(num_classes=50).to(self.device)
        
        # Loss and optimizer
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
    
    def train_epoch(self, epoch):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        progress_bar = tqdm(self.train_loader, desc=f'Epoch {epoch+1}/{self.num_epochs}')
        
        for batch_idx, (data, targets) in enumerate(progress_bar):
            data, targets = data.to(self.device), targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(data)
            loss = self.criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            # Update progress bar
            current_acc = 100. * correct / total
            progress_bar.set_postfix({
                'Loss': f'{running_loss/(batch_idx+1):.4f}',
                'Acc': f'{current_acc:.2f}%'
            })
        
        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = 100. * correct / total
        
        self.train_losses.append(epoch_loss)
        self.train_accuracies.append(epoch_acc)
        
        return epoch_loss, epoch_acc
    
    def validate_epoch(self):
        """Validate for one epoch"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for data, targets in self.val_loader:
                data, targets = data.to(self.device), targets.to(self.device)
                
                outputs = self.model(data)
                loss = self.criterion(outputs, targets)
                
                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
                
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(targets.cpu().numpy())
        
        epoch_loss = running_loss / len(self.val_loader)
        epoch_acc = 100. * correct / total
        
        self.val_losses.append(epoch_loss)
        self.val_accuracies.append(epoch_acc)
        
        return epoch_loss, epoch_acc, all_predictions, all_targets
    
    def train(self):
        """Main training loop"""
        logger.info("🚀 STARTING MODEL TRAINING")
        logger.info("=" * 80)
        
        best_val_acc = 0.0
        patience_counter = 0
        max_patience = 10
        
        for epoch in range(self.num_epochs):
            # Training
            train_loss, train_acc = self.train_epoch(epoch)
            
            # Validation
            val_loss, val_acc, predictions, targets = self.validate_epoch()
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Print epoch results
            logger.info(f'Epoch {epoch+1}/{self.num_epochs}:')
            logger.info(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
            logger.info(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self.save_model('best_model.pth', epoch, val_acc)
                patience_counter = 0
            else:
                patience_counter += 1
            
            # Early stopping
            if patience_counter >= max_patience:
                logger.info(f'🛑 Early stopping at epoch {epoch+1}')
                break
        
        # Final evaluation
        self.final_evaluation()
        
        # Plot training curves
        self.plot_training_curves()
        
        # Save final model
        self.save_model('final_model.pth', self.num_epochs, val_acc)
        
        logger.info("🎉 TRAINING COMPLETED!")
        return best_val_acc
    
    def save_model(self, filename, epoch, accuracy):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'accuracy': accuracy,
            'class_to_idx': self.dataset.class_to_idx,
            'idx_to_class': self.dataset.idx_to_class,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies
        }
        
        torch.save(checkpoint, self.output_dir / filename)
        logger.info(f'💾 Model saved: {filename} (Acc: {accuracy:.2f}%)')
    
    def final_evaluation(self):
        """Final model evaluation"""
        logger.info("🔍 FINAL MODEL EVALUATION")
        logger.info("=" * 80)
        
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for data, targets in self.val_loader:
                data, targets = data.to(self.device), targets.to(self.device)
                outputs = self.model(data)
                _, predicted = outputs.max(1)
                
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(targets.cpu().numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(all_targets, all_predictions)
        
        logger.info(f'📊 Final Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)')
        
        # Classification report
        class_names = [self.dataset.idx_to_class[i]['scientific_name'] for i in range(50)]
        report = classification_report(all_targets, all_predictions, 
                                     target_names=class_names, 
                                     output_dict=True)
        
        # Save metrics
        metrics = {
            'final_accuracy': accuracy,
            'classification_report': report,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies
        }
        
        with open(self.output_dir / 'training_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f'📄 Metrics saved: training_metrics.json')
    
    def plot_training_curves(self):
        """Plot training and validation curves"""
        plt.figure(figsize=(15, 5))
        
        # Loss curves
        plt.subplot(1, 2, 1)
        plt.plot(self.train_losses, label='Training Loss', color='blue')
        plt.plot(self.val_losses, label='Validation Loss', color='red')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        # Accuracy curves
        plt.subplot(1, 2, 2)
        plt.plot(self.train_accuracies, label='Training Accuracy', color='blue')
        plt.plot(self.val_accuracies, label='Validation Accuracy', color='red')
        plt.title('Training and Validation Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy (%)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'training_curves.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f'📊 Training curves saved: training_curves.png')

def main():
    """Main training function"""
    
    logger.info("🎯 BIRD SOUND CLASSIFICATION MODEL TRAINING")
    logger.info("=" * 80)
    logger.info("📁 Dataset: dataset_50_meaningful_species")
    logger.info("🐦 Species: 50 meaningful species")
    logger.info("🔬 Model: ResNet18 (pretrained)")
    logger.info("📊 Training: 40 epochs, 80/20 split")
    logger.info("=" * 80)
    
    # Initialize trainer
    trainer = ModelTrainer(
        dataset_path="dataset_50_meaningful_species",
        output_dir="trained_models"
    )
    
    # Start training
    best_accuracy = trainer.train()
    
    logger.info(f"🎉 TRAINING COMPLETED!")
    logger.info(f"🏆 Best Validation Accuracy: {best_accuracy:.2f}%")
    logger.info(f"📁 Models saved in: trained_models/")
    logger.info(f"📊 Metrics and plots generated")
    
    return trainer

if __name__ == "__main__":
    trainer = main()
