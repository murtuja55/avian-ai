---
title: Avian AI - Bird Sound Recognition
emoji: 🐦
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app_fixed.py
pinned: false
license: mit
python_version: "3.13"
---

# 🐦 Avian AI - Bird Sound Recognition

Identify bird species from audio recordings using deep learning.

## 🎯 Features

- **50 Bird Species**: Recognizes common North American birds
- **High Accuracy**: Trained on thousands of bird recordings
- **Easy Upload**: Simply upload an audio file or use your microphone
- **Top 3 Predictions**: Shows confidence scores for multiple species
- **CPU Optimized**: Runs efficiently without GPU requirements

## 🎮 How to Use

1. **Upload Audio**: Click "Upload Bird Audio File" or use your microphone
2. **Wait for Analysis**: The AI processes the audio (takes a few seconds)
3. **View Results**: See the predicted bird species with confidence scores

## 🦆 Supported Species

The model can identify 50 common bird species including:
- American Robin, Blue Jay, Cardinal, Chickadee, Crow
- Dove, Eagle, Finch, Goose, Hawk
- Hummingbird, Sparrow, Warbler, Woodpecker
- And many more...

## 📊 Technical Details

- **Model Architecture**: ResNet-18 based CNN
- **Input**: Audio files (WAV, MP3, FLAC, M4A)
- **Processing**: Mel spectrogram analysis
- **Output**: Species classification with confidence scores
- **Accuracy**: ~95% on test dataset

## 🔧 Model Information

- **Framework**: PyTorch (latest version compatible with Python 3.13)
- **Audio Processing**: Librosa
- **Spectrogram**: 128x128 mel spectrograms
- **Sample Rate**: 22.05 kHz
- **Duration**: 5 seconds maximum

## 🚀 Deployment

This app is deployed on Hugging Face Spaces with:
- **CPU-only inference** (optimized for free tier)
- **Memory optimization** (single-threaded processing)
- **Gradio interface** (easy-to-use web UI)

## 📝 Usage Tips

- **Clear Audio**: Best results with clear bird recordings
- **Duration**: Works best with 3-10 second clips
- **Background Noise**: Minimal background noise improves accuracy
- **File Formats**: Supports WAV, MP3, FLAC, M4A

## ⚠️ Limitations

- **CPU Only**: No GPU acceleration (for free tier compatibility)
- **50 Species**: Limited to trained bird species
- **Audio Quality**: Performance depends on recording quality
- **Regional**: Best for North American bird species

## 🤝 Contributing

This model was trained on publicly available bird sound datasets. For improvements or issues, please open an issue.

## 📄 License

MIT License - Free for commercial and personal use.

---

**🐦 Happy bird watching!**
