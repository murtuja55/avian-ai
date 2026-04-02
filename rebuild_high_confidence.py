#!/usr/bin/env python3
"""
Rebuild High-Confidence Audio Files from Scratch
Using CURRENT inference pipeline - NO modifications
"""

import os
import json
import glob
import logging
from pathlib import Path
from collections import defaultdict
import sys

# Add backend to path
sys.path.append('backend')

# Import current inference pipeline
from inference import BirdClassifier

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_dataset():
    """Analyze entire dataset with current pipeline"""
    
    logger.info("🚀 Starting high-confidence analysis...")
    
    # Initialize classifier with current pipeline
    classifier = BirdClassifier()
    
    # Dataset path
    dataset_path = Path("data/dataset_50_meaningful_species/raw")
    
    if not dataset_path.exists():
        logger.error(f"❌ Dataset path not found: {dataset_path}")
        return
    
    # Load species mapping
    metadata_path = Path("data/dataset_50_meaningful_species/dataset_metadata.json")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Create species mapping
    species_map = {}
    for species in metadata['species']:
        species_map[species['folder_name']] = species['scientific_name']
    
    logger.info(f"📊 Found {len(species_map)} species")
    
    # Results storage
    all_results = []
    correct_predictions = []
    high_confidence_correct = []
    
    # Process all audio files
    audio_files = list(dataset_path.rglob("*.ogg"))
    logger.info(f"🎵 Found {len(audio_files)} audio files")
    
    for i, audio_file in enumerate(audio_files):
        if i % 100 == 0:
            logger.info(f"📈 Progress: {i}/{len(audio_files)} ({i/len(audio_files)*100:.1f}%)")
        
        try:
            # Get true label from folder name
            folder_name = audio_file.parent.name
            true_label = species_map.get(folder_name, folder_name)
            
            # Run CURRENT inference pipeline
            result = classifier.predict(str(audio_file))
            
            if result.get('error'):
                logger.warning(f"⚠️  Error processing {audio_file}: {result['error']}")
                continue
            
            predicted_label = result['prediction']
            confidence = result['confidence']
            
            # Store all results
            all_results.append({
                'file': str(audio_file),
                'true_label': true_label,
                'predicted_label': predicted_label,
                'confidence': confidence,
                'correct': predicted_label == true_label
            })
            
            # Store correct predictions
            if predicted_label == true_label:
                correct_predictions.append({
                    'file': str(audio_file),
                    'species_name': true_label,
                    'confidence': confidence,
                    'predicted': predicted_label,
                    'actual': true_label
                })
                
                # Store high-confidence correct predictions
                if confidence >= 0.9:
                    high_confidence_correct.append({
                        'file': str(audio_file),
                        'species_name': true_label,
                        'confidence': confidence,
                        'predicted': predicted_label,
                        'actual': true_label
                    })
            
        except Exception as e:
            logger.error(f"❌ Error processing {audio_file}: {str(e)}")
            continue
    
    logger.info(f"✅ Analysis complete:")
    logger.info(f"   Total files: {len(all_results)}")
    logger.info(f"   Correct predictions: {len(correct_predictions)}")
    logger.info(f"   High-confidence correct (>=0.9): {len(high_confidence_correct)}")
    
    # Group by species
    species_groups = defaultdict(list)
    for item in high_confidence_correct:
        species_groups[item['species_name']].append(item)
    
    logger.info(f"📊 Species with high-confidence correct predictions: {len(species_groups)}")
    
    # Select top 5 species by count
    top_species = sorted(species_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    
    # Select top 5 files per species
    best_files = {}
    for species_name, files in top_species:
        # Sort by confidence descending
        sorted_files = sorted(files, key=lambda x: x['confidence'], reverse=True)[:5]
        best_files[species_name] = sorted_files
    
    # Save results
    output_file = "best_high_confidence_files.json"
    with open(output_file, 'w') as f:
        json.dump(best_files, f, indent=2)
    
    logger.info(f"💾 Saved to: {output_file}")
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("🎯 HIGH-CONFIDENCE SPECIES SUMMARY")
    logger.info("="*60)
    
    for species_name, files in best_files.items():
        logger.info(f"\n🦉 {species_name}")
        logger.info(f"   Total high-confidence correct files: {len(species_groups[species_name])}")
        logger.info(f"   Top 5 selected files:")
        for i, file_info in enumerate(files, 1):
            logger.info(f"     {i}. {file_info['confidence']:.3f} - {Path(file_info['file']).name}")
    
    logger.info("\n" + "="*60)
    logger.info("✅ HIGH-CONFIDENCE REBUILD COMPLETE!")
    logger.info("="*60)
    
    return best_files

if __name__ == "__main__":
    analyze_dataset()
