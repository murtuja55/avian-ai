"""
Simple Bird Sound Classification Training
Robust audio loading with fallback methods
"""

import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import models, transforms
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

class SimpleBirdDataset(Dataset):
    """Simple Bird Audio Dataset with robust loading"""
    
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.samples = []
        self.class_names = []
        self.class_to_idx = {}
        
        # Load dataset
        self._load_dataset()
        
        logger.info(f"🎯 Loaded {len(self.samples)} samples")
        logger.info(f"🐦 Number of classes: {len(self.class_names)}")
    
    def _load_dataset(self):
        """Load all audio samples and classes"""
        raw_dir = self.root_dir / "raw"
        
        # Load metadata
        metadata_path = self.root_dir / "dataset_metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Create class mapping
        for idx, species in enumerate(metadata['species']):
            class_name = species['scientific_name']
            self.class_names.append(class_name)
            self.class_to_idx[class_name] = idx
        
        # Load samples
        for species in metadata['species']:
            folder_name = species['folder_name']
            scientific_name = species['scientific_name']
            class_idx = self.class_to_idx[scientific_name]
            
            species_folder = raw_dir / folder_name
            if species_folder.exists():
                for audio_file in species_folder.glob("*.ogg"):
                    self.samples.append((str(audio_file), class_idx))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        audio_path, class_idx = self.samples[idx]
        
        # Load audio using librosa (more reliable)
        try:
            import librosa
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=22050, mono=True)
            
            # Fixed length (5 seconds)
            target_length = 22050 * 5
            if len(audio) < target_length:
                audio = np.pad(audio, (0, target_length - len(audio)))
            else:
                audio = audio[:target_length]
            
            # Create mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio, 
                sr=22050, 
                n_mels=128, 
                n_fft=512, 
                hop_length=256
            )
            
            # Convert to log scale
            log_mel = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Normalize
            log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-9)
            
            # Convert to tensor
            log_mel = torch.FloatTensor(log_mel)
            
            # Resize to 128x128
            resize_transform = transforms.Resize((128, 128))
            log_mel = resize_transform(log_mel.unsqueeze(0))
            
            # Convert to 3-channel
            log_mel = log_mel.repeat(3, 1, 1)
            
            return log_mel, class_idx
            
        except Exception as e:
            logger.warning(f"Error loading {audio_path}: {e}")
            # Return dummy data
            dummy_tensor = torch.zeros(3, 128, 128)
            return dummy_tensor, class_idx

class SimpleBirdModel(nn.Module):
    """Simple Bird Classification Model"""
    
    def __init__(self, num_classes=50):
        super(SimpleBirdModel, self).__init__()
        
        # Use pretrained ResNet18
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        
        # Modify final layer
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_features, num_classes)
        
        # Add dropout
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        x = self.backbone(x)
        x = self.dropout(x)
        return x

class SimpleTrainer:
    """Simple Model Trainer"""
    
    def __init__(self, dataset_path):
        self.dataset_path = Path(dataset_path)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"🎯 Using device: {self.device}")
        
        # Create dataset
        self.dataset = SimpleBirdDataset(self.dataset_path)
        
        # Split dataset
        train_size = int(0.8 * len(self.dataset))
        val_size = len(self.dataset) - train_size
        self.train_dataset, self.val_dataset = random_split(
            self.dataset, [train_size, val_size]
        )
        
        # Data loaders
        self.train_loader = DataLoader(
            self.train_dataset, batch_size=16, shuffle=True, num_workers=0
        )
        self.val_loader = DataLoader(
            self.val_dataset, batch_size=16, shuffle=False, num_workers=0
        )
        
        logger.info(f"📊 Train samples: {len(self.train_dataset)}")
        logger.info(f"📊 Val samples: {len(self.val_dataset)}")
        
        # Model
        self.model = SimpleBirdModel(num_classes=50).to(self.device)
        
        # Loss and optimizer
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
    
    def train_epoch(self, epoch):
        """Train one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        progress_bar = tqdm(self.train_loader, desc=f'Epoch {epoch+1}')
        
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
            if batch_idx % 10 == 0:
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
        """Validate one epoch"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, targets in self.val_loader:
                data, targets = data.to(self.device), targets.to(self.device)
                
                outputs = self.model(data)
                loss = self.criterion(outputs, targets)
                
                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
        
        epoch_loss = running_loss / len(self.val_loader)
        epoch_acc = 100. * correct / total
        
        self.val_losses.append(epoch_loss)
        self.val_accuracies.append(epoch_acc)
        
        return epoch_loss, epoch_acc
    
    def train(self, num_epochs=30):
        """Main training loop"""
        logger.info("🚀 STARTING TRAINING")
        logger.info("=" * 80)
        
        best_val_acc = 0.0
        
        for epoch in range(num_epochs):
            # Train
            train_loss, train_acc = self.train_epoch(epoch)
            
            # Validate
            val_loss, val_acc = self.validate_epoch()
            
            # Print results
            logger.info(f'Epoch {epoch+1}/{num_epochs}:')
            logger.info(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
            logger.info(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self.save_model('best_model.pth', epoch, val_acc)
            
            # Early stopping if no improvement
            if epoch > 20 and val_acc < best_val_acc - 10:
                logger.info(f'🛑 Early stopping at epoch {epoch+1}')
                break
        
        # Save final model
        self.save_model('final_model.pth', num_epochs, val_acc)
        
        # Plot results
        self.plot_results()
        
        logger.info(f"🎉 TRAINING COMPLETED!")
        logger.info(f"🏆 Best Validation Accuracy: {best_val_acc:.2f}%")
        
        return best_val_acc
    
    def save_model(self, filename, epoch, accuracy):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'accuracy': accuracy,
            'class_names': self.dataset.class_names,
            'class_to_idx': self.dataset.class_to_idx,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies
        }
        
        torch.save(checkpoint, filename)
        logger.info(f'💾 Model saved: {filename} (Acc: {accuracy:.2f}%)')
    
    def plot_results(self):
        """Plot training curves"""
        plt.figure(figsize=(12, 5))
        
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
        plt.savefig('training_results.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f'📊 Training curves saved: training_results.png')

def main():
    """Main function"""
    logger.info("🎯 SIMPLE BIRD SOUND CLASSIFICATION TRAINING")
    logger.info("=" * 80)
    logger.info("📁 Dataset: dataset_50_meaningful_species")
    logger.info("🐦 Species: 50 meaningful species")
    logger.info("🔬 Model: ResNet18 (pretrained)")
    logger.info("📊 Training: 30 epochs, 80/20 split")
    logger.info("=" * 80)
    
    # Install librosa if needed
    try:
        import librosa
    except ImportError:
        logger.info("📦 Installing librosa...")
        os.system("pip install librosa")
        import librosa
    
    # Create trainer
    trainer = SimpleTrainer("dataset_50_meaningful_species")
    
    # Start training
    best_accuracy = trainer.train(num_epochs=30)
    
    logger.info("🎉 TRAINING COMPLETED SUCCESSFULLY!")
    logger.info(f"🏆 Best Accuracy: {best_accuracy:.2f}%")
    logger.info(f"📁 Models saved: best_model.pth, final_model.pth")
    logger.info(f"📊 Results plotted: training_results.png")
    
    return trainer

if __name__ == "__main__":
    trainer = main()
