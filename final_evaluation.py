#!/usr/bin/env python3
"""
FINAL MASTER TASK — COMPLETE MODEL PERFORMANCE + DEMO SYSTEM
Full dataset evaluation + clean demo file extraction
"""

import os
import json
import glob
import shutil
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

def evaluate_full_dataset():
    """STEP 1: Full dataset evaluation"""
    
    logger.info("🚀 STARTING FINAL MASTER EVALUATION...")
    
    # Initialize classifier with current pipeline
    classifier = BirdClassifier()
    
    # STEP 9: Verify pipeline first
    logger.info("🔍 STEP 9: VERIFYING PIPELINE...")
    logger.info(f"   Model loaded: {classifier.model is not None}")
    logger.info(f"   Device: {classifier.device}")
    logger.info(f"   Class count: {len(classifier.class_names)}")
    
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
    
    # STEP 1: Full dataset evaluation
    logger.info("📈 STEP 1: FULL DATASET EVALUATION...")
    
    # Results storage per species
    species_results = defaultdict(lambda: {
        'total_samples': 0,
        'correct_predictions': 0,
        'confidences': [],
        'high_conf_correct': [],
        'all_results': []
    })
    
    # Process all audio files
    audio_files = list(dataset_path.rglob("*.ogg"))
    logger.info(f"🎵 Found {len(audio_files)} audio files")
    
    for i, audio_file in enumerate(audio_files):
        if i % 500 == 0:
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
            
            # Store results per species
            species_data = species_results[true_label]
            species_data['total_samples'] += 1
            species_data['all_results'].append({
                'file': str(audio_file),
                'predicted': predicted_label,
                'actual': true_label,
                'confidence': confidence,
                'correct': predicted_label == true_label
            })
            
            if predicted_label == true_label:
                species_data['correct_predictions'] += 1
                species_data['confidences'].append(confidence)
                
                if confidence >= 0.9:
                    species_data['high_conf_correct'].append({
                        'file': str(audio_file),
                        'confidence': confidence
                    })
            
        except Exception as e:
            logger.error(f"❌ Error processing {audio_file}: {str(e)}")
            continue
    
    logger.info(f"✅ Dataset evaluation complete!")
    
    # STEP 2: Per-species metrics
    logger.info("📊 STEP 2: PER-SPECIES METRICS...")
    
    species_metrics = {}
    for species_name, data in species_results.items():
        total = data['total_samples']
        correct = data['correct_predictions']
        accuracy = correct / total if total > 0 else 0
        avg_confidence = sum(data['confidences']) / len(data['confidences']) if data['confidences'] else 0
        high_conf_count = len(data['high_conf_correct'])
        
        species_metrics[species_name] = {
            'total_samples': total,
            'correct_predictions': correct,
            'accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'high_conf_count': high_conf_count
        }
    
    # STEP 3: Classify species into 3 tiers
    logger.info("🏆 STEP 3: CLASSIFY SPECIES INTO 3 TIERS...")
    
    strong_species = []
    medium_species = []
    weak_species = []
    
    for species_name, metrics in species_metrics.items():
        accuracy = metrics['accuracy']
        high_conf_count = metrics['high_conf_count']
        
        if accuracy >= 0.80 and high_conf_count >= 20:
            strong_species.append(species_name)
        elif 0.60 <= accuracy < 0.80:
            medium_species.append(species_name)
        else:
            weak_species.append(species_name)
    
    # STEP 4: Count summary
    logger.info("📈 STEP 4: COUNT SUMMARY...")
    logger.info("=" * 60)
    logger.info(f"📊 Total species: 50")
    logger.info(f"🏆 STRONG species count: {len(strong_species)}")
    logger.info(f"⚖️  MEDIUM species count: {len(medium_species)}")
    logger.info(f"⚠️  WEAK species count: {len(weak_species)}")
    logger.info("=" * 60)
    
    # STEP 5: Build demo files (ONLY STRONG species)
    logger.info("🎯 STEP 5: BUILD DEMO FILES (ONLY STRONG SPECIES)...")
    
    demo_files = {}
    for species_name in strong_species:
        species_data = species_results[species_name]
        
        # Select TOP 3 files with confidence >= 0.95 and correct predictions
        high_quality_files = []
        for result in species_data['all_results']:
            if result['correct'] and result['confidence'] >= 0.95:
                high_quality_files.append(result)
        
        # Sort by confidence DESC and pick top 3
        high_quality_files.sort(key=lambda x: x['confidence'], reverse=True)
        top_3_files = high_quality_files[:3]
        
        if top_3_files:
            demo_files[species_name] = top_3_files
            logger.info(f"✅ {species_name}: {len(top_3_files)} demo files selected")
        else:
            logger.warning(f"⚠️  {species_name}: No files >= 0.95 confidence found")
    
    # STEP 6: Create clean demo folder
    logger.info("📁 STEP 6: CREATE CLEAN DEMO FOLDER...")
    
    demo_folder = Path("demo_ready")
    if demo_folder.exists():
        shutil.rmtree(demo_folder)
    demo_folder.mkdir(exist_ok=True)
    
    demo_file_paths = {}
    for species_name, files in demo_files.items():
        # Create species folder
        species_folder = demo_folder / species_name.replace(" ", "_")
        species_folder.mkdir(exist_ok=True)
        
        demo_file_paths[species_name] = []
        
        for file_info in files:
            source_path = Path(file_info['file'])
            if source_path.exists():
                # Copy file to demo folder
                dest_path = species_folder / source_path.name
                shutil.copy2(source_path, dest_path)
                
                demo_file_paths[species_name].append({
                    'file': str(dest_path),
                    'confidence': file_info['confidence']
                })
    
    # STEP 7: Create final JSON
    logger.info("💾 STEP 7: CREATE FINAL JSON...")
    
    with open("demo_ready.json", 'w') as f:
        json.dump(demo_file_paths, f, indent=2)
    
    # STEP 8: Real behavior report
    logger.info("📋 STEP 8: REAL BEHAVIOR REPORT...")
    logger.info("=" * 60)
    logger.info("🏆 STRONG SPECIES (DEMO READY):")
    for species in strong_species:
        metrics = species_metrics[species]
        logger.info(f"   🦉 {species}")
        logger.info(f"      Expected: Correct predictions, high confidence")
        logger.info(f"      Accuracy: {metrics['accuracy']:.3f}")
        logger.info(f"      High confidence count: {metrics['high_conf_count']}")
    
    logger.info("\n⚖️  MEDIUM SPECIES:")
    for species in medium_species:
        metrics = species_metrics[species]
        logger.info(f"   🦉 {species}")
        logger.info(f"      Expected: Mixed results")
        logger.info(f"      Accuracy: {metrics['accuracy']:.3f}")
    
    logger.info("\n⚠️  WEAK SPECIES:")
    for species in weak_species:
        metrics = species_metrics[species]
        logger.info(f"   🦉 {species}")
        logger.info(f"      Expected: Frequent wrong predictions")
        logger.info(f"      Accuracy: {metrics['accuracy']:.3f}")
    
    logger.info("=" * 60)
    
    # Final summary
    logger.info("🎉 FINAL SUMMARY:")
    logger.info(f"   📁 Demo folder created: demo_ready/")
    logger.info(f"   📄 Demo JSON created: demo_ready.json")
    logger.info(f"   🏆 Strong species with demo files: {len(demo_files)}")
    logger.info(f"   📁 Total demo files: {sum(len(files) for files in demo_file_paths.values())}")
    logger.info(f"   ✅ All demo files have confidence >= 0.95")
    logger.info(f"   ✅ All demo files are correct predictions")
    
    logger.info("\n🎯 FINAL GOAL ACHIEVED:")
    logger.info("   When uploading ANY file from demo_ready/:")
    logger.info("   → Prediction will be CORRECT")
    logger.info("   → Confidence will be >= 0.95")
    logger.info("   → No 'Failed to analyze audio'")
    logger.info("   System is DEMO PERFECT + REALISTIC")
    
    return demo_file_paths, species_metrics

if __name__ == "__main__":
    evaluate_full_dataset()
