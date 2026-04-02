# Avian AI - Deployment Instructions

## 🚀 Ready for Deployment

This project is configured for single-service deployment on platforms like Render.

### 📁 Project Structure
```
bird-sound-recognition/
├── backend/
│   ├── app.py              # Main Flask app with frontend serving
│   ├── inference.py        # ML inference (DO NOT MODIFY)
│   ├── model/
│   │   └── best_model.pth  # Critical model file (134MB)
│   └── static/             # Built frontend (out/ moved here)
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment config
└── data/                  # Dataset (not needed for deployment)
```

### 🔧 Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to render.com
   - Create new Web Service
   - Connect your GitHub repo
   - Build Command: (leave empty - uses pip install)
   - Start Command: `gunicorn app:app`
   - Instance Type: Free (or paid for better performance)

### 🎯 Expected URLs
- **Main App**: `https://your-app.onrender.com`
- **API**: `https://your-app.onrender.com/predict`
- **Health**: `https://your-app.onrender.com/health`

### ✅ Verification
After deployment, test:
1. UI loads correctly
2. Audio upload works
3. Prediction returns results
4. No "Failed to analyze audio" errors

### 🔥 Critical Notes
- **DO NOT MODIFY** inference.py logic
- **DO NOT DELETE** model/best_model.pth
- **DO NOT CHANGE** tensor shape logic
- Frontend is served from backend/static
- API calls use relative URLs (no localhost)

### 📊 Performance
- Model size: 134MB
- Startup time: ~2-3 minutes (first time)
- Memory usage: ~500MB
- Recommended: Paid instance for production
