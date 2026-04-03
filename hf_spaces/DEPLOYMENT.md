# 🚀 Hugging Face Spaces Deployment Guide

## 📋 Prerequisites

1. **Hugging Face Account**: Create account at https://huggingface.co
2. **Model File**: Copy `best_model.pth` to this directory
3. **Git**: Install git on your system

## 📁 Files Required

```
hf_spaces/
├── app.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # Space metadata
├── best_model.pth      # Your trained model (copy from backend/model/)
└── DEPLOYMENT.md       # This file
```

## 🔧 Step-by-Step Deployment

### 1. Copy Model File
```bash
# Copy your trained model to the Spaces directory
cp backend/model/best_model.pth hf_spaces/
```

### 2. Initialize Git Repository
```bash
cd hf_spaces
git init
git add .
git commit -m "Initial commit - Avian AI Spaces"
```

### 3. Create Hugging Face Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose:
   - **Space Name**: `avian-ai-bird-recognition`
   - **License**: MIT
   - **SDK**: Gradio
   - **Hardware**: CPU basic (free tier)
   - **Visibility**: Public
4. Click "Create Space"

### 4. Push to Hugging Face
```bash
# Add remote (replace YOUR_USERNAME with your Hugging Face username)
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/avian-ai-bird-recognition

# Push to deploy
git push origin main
```

### 5. Wait for Build
- Hugging Face will automatically build your Space
- Takes 2-5 minutes for first build
- Check the "Build" tab for progress

## 🌐 Access Your App

Once built, your app will be available at:
```
https://YOUR_USERNAME-avian-ai-bird-recognition.hf.space
```

## 🔧 Troubleshooting

### Build Fails?
1. Check `requirements.txt` for correct versions
2. Verify `best_model.pth` is included
3. Check the "Build" tab for error logs

### Model Loading Error?
1. Ensure `best_model.pth` is in the correct location
2. Check file permissions
3. Verify model file is not corrupted

### Memory Issues?
1. The app is optimized for CPU (512MB limit)
2. Uses single-threaded processing
3. Automatic garbage collection

## 📊 Expected Performance

- **Startup Time**: 10-15 seconds (model loading)
- **Prediction Time**: 2-5 seconds per audio file
- **Memory Usage**: ~200-300MB (within free tier)
- **Accuracy**: ~95% on trained species

## 🎯 Usage Tips

1. **Test Audio**: Start with clear bird recordings
2. **File Formats**: WAV, MP3, FLAC, M4A supported
3. **Duration**: 3-10 seconds works best
4. **Background**: Minimal background noise improves results

## 🔄 Updates

To update your app:
```bash
# Make changes
git add .
git commit -m "Update app"
git push origin main
```

The Space will automatically rebuild with your changes.

## 📱 Mobile Access

The app works on mobile devices:
- Upload audio files from phone
- Use microphone for live recording
- Responsive design for small screens

## 🎉 Success!

Your Avian AI bird sound recognition app is now live on Hugging Face Spaces! 🐦
