# 🚀 Deployment Guide - Avian AI

Complete guide to deploy Avian AI to production environments.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Backend Deployment (Hugging Face Spaces)](#backend-deployment-hugging-face-spaces)
3. [Frontend Deployment (Render)](#frontend-deployment-render)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

---

## ⚡ Quick Start

### Deploy in 5 Minutes

1. **Backend**: Upload to [HF Spaces](https://huggingface.co/spaces)
   ```
   hf_spaces/app.py
   hf_spaces/best_model.pth
   requirements.txt
   ```

2. **Frontend**: Connect GitHub to [Render](https://render.com)
   - Set build: `npm install && npm run build`
   - Set start: `npm start`

3. **Done!** ✅ Auto-deploys on git push

---

## 🤖 Backend Deployment (Hugging Face Spaces)

### Prerequisites
- Hugging Face account
- 200MB storage for model file
- Git access

### Step 1: Create Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `avian-ai-backend`
   - **License**: `MIT`
   - **Space SDK**: `Docker`
   - **Template**: `Blank`
4. Click **"Create Space"**

### Step 2: Upload Files

Option A: **Via Git** (Recommended)
```bash
# Clone space
git clone https://huggingface.co/spaces/USERNAME/avian-ai-backend
cd avian-ai-backend

# Copy files
cp -r ../avian-ai/hf_spaces/* .

# Commit & push
git add .
git commit -m "Initial deployment"
git push
```

Option B: **Via Web Interface**
1. Go to your Space
2. Click **"Files"**
3. Upload:
   - `app.py`
   - `best_model.pth`
   - `requirements.txt`
4. Space auto-rebuilds

### Step 3: Verify Deployment

Check logs in Space UI:
```
✅ Upload folder created/verified: /app/uploads
✅ Model exists: True
✅ Running on all addresses (0.0.0.0)
```

### Step 4: Test Endpoint

```bash
# Health check
curl https://USERNAME-avian-ai-backend.hf.space/health

# Predict
curl -X POST \
  -F "file=@bird.mp3" \
  https://USERNAME-avian-ai-backend.hf.space/predict
```

### Configuration

**environment.txt** (in HF Space):
```
PYTHONUNBUFFERED=1
FLASK_ENV=production
```

**requirements.txt**:
```
--extra-index-url https://download.pytorch.org/whl/cpu

torch==2.6.0
torchvision==0.21.0
torchaudio==2.6.0
librosa==0.11.0
flask==2.3.3
flask-cors==4.0.0
```

---

## 🌐 Frontend Deployment (Render)

### Prerequisites
- GitHub repository
- Render account
- Node.js 18+

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/USERNAME/avian-ai
git push -u origin main
```

### Step 2: Connect to Render

1. Go to https://render.com/dashboard
2. Click **"+ New"** → **"Web Service"**
3. Connect GitHub account
4. Select **`avian-ai`** repository

### Step 3: Configure Build

Fill in settings:

| Setting | Value |
|---------|-------|
| **Name** | `avian-ai` |
| **Environment** | `Node` |
| **Region** | Choose closest |
| **Branch** | `main` |
| **Build Command** | `npm install && npm run build` |
| **Start Command** | `npm start` |
| **Plan** | Free or Paid |

### Step 4: Environment Variables

Add in Render dashboard:

```
NEXT_PUBLIC_API_URL=https://USERNAME-avian-ai-backend.hf.space
NODE_ENV=production
```

### Step 5: Deploy

Click **"Create Web Service"**
- Build starts automatically
- Wait 5-10 minutes
- Get public URL: `https://avian-ai-xxxxx.onrender.com`

### Step 6: Verify

Visit your URL and test:
- Upload audio file ✅
- Get prediction ✅
- Check console for errors ✅

---

## ✅ Production Checklist

### Before Going Live

#### Backend
- [ ] Model file uploaded (`best_model.pth` 128MB)
- [ ] All dependencies in `requirements.txt`
- [ ] CORS configured for frontend URL
- [ ] Error handling for invalid files
- [ ] Logging for debugging
- [ ] Health endpoint working
- [ ] Rate limiting configured (optional)

#### Frontend
- [ ] API URL points to backend
- [ ] Error messages user-friendly
- [ ] Loading states implemented
- [ ] Mobile responsive
- [ ] Audio playback working
- [ ] Confidence display formatting
- [ ] SEO meta tags added

#### Deployment
- [ ] GitHub repo public/private (choose)
- [ ] README.md complete
- [ ] LICENSE file added
- [ ] .gitignore configured
- [ ] Environment variables set
- [ ] HTTPS enabled
- [ ] Custom domain (optional)

#### Security
- [ ] File upload validation
- [ ] CORS restrictions
- [ ] Input sanitization
- [ ] Model file protected
- [ ] API rate limiting
- [ ] Error messages don't leak info

---

## 📊 Monitoring & Maintenance

### HF Spaces Monitoring

**View Logs**:
1. Go to Space
2. Click **"Logs"** tab
3. Check for errors

**Key Metrics**:
- ✅ Model loads successfully
- ✅ Audio preprocessing works
- ✅ Predictions return correctly
- ✅ No 404 or 500 errors

### Render Monitoring

**View Logs**:
1. Dashboard → Service
2. Scroll to **"Logs"**
3. Check for errors

**Key Metrics**:
- ✅ Builds succeed
- ✅ App stays online
- ✅ No crashed processes
- ✅ Response times < 5s

### Uptime Monitoring

Use free services:
- [UptimeRobot](https://uptimerobot.com) - Monitor API
- [StatusPage.io](https://statuspage.io) - Status dashboard
- [Sentry](https://sentry.io) - Error tracking

### Performance Optimization

```bash
# Frontend
npm run build
npm run analyze  # Check bundle size

# Backend
# Monitor model load time
# Check GPU/memory usage
```

---

## 🔧 Troubleshooting

### Backend Issues

#### Model File Not Found
```
Error: best_model.pth not found
```
**Solution**: Upload `best_model.pth` to HF Space files

#### 404 on /predict
```
POST /predict returns 404
```
**Solution**: Ensure `app.py` has correct route:
```python
@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    ...
```

#### CORS Errors
```
Access denied (origin mismatch)
```
**Solution**: Update CORS in app.py:
```python
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})
```

#### Audio Processing Errors
```
Error: n_mels (128) may be set too high
```
**Solution**: Warning is normal, not an error. Model still works.

### Frontend Issues

#### API Connection Failed
```
Error: Failed to connect to backend
```
**Solution**: Check `NEXT_PUBLIC_API_URL` in `.env.local`:
```
NEXT_PUBLIC_API_URL=https://USERNAME-avian-ai-backend.hf.space
```

#### Audio Playback Not Working
```
Audio fails to load
```
**Solution**: Ensure backend returns valid audio blob

#### Slow Predictions
```
Takes > 30 seconds
```
**Solution**: 
- Model is large (128MB)
- First load takes longer
- HF Spaces may have resource limits

### Deployment Issues

#### Build Failures on Render
```
npm install fails
```
**Solution**: 
1. Check `package.json` syntax
2. Use compatible Node version
3. Clear Render cache (redeploy)

#### Space Times Out
```
HF Space build takes > 1 hour
```
**Solution**:
- PyTorch builds are slow (1st time)
- Next deploys are faster
- Be patient or use paid tier

---

## 🔐 Production Secrets

### API Keys & Credentials

Keep safe in environment variables:

```bash
# .env.local (frontend)
NEXT_PUBLIC_API_URL=https://backend.url

# HF Space Settings
FLASK_ENV=production
```

**Never commit**:
- API keys
- Passwords
- Private URLs
- Secret tokens

### HTTPS & Security

✅ Both HF Spaces and Render provide free HTTPS
✅ Enforce HTTPS in browser
✅ Set secure cookies
✅ Use SameSite=Strict

---

## 📈 Scaling for Production

### Current Limits
- HF Spaces: 1 GPU-free, 16GB RAM
- Render Free: 750 hours/month
- File uploads: 50MB max

### Upgrade Path

1. **Scale Backend**:
   - Upgrade HF Space to paid GPU
   - Use FastAPI for higher throughput
   - Add request queuing

2. **Scale Frontend**:
   - Render paid tier (unlimited)
   - Add CDN (Cloudflare)
   - Cache static assets

3. **Add Database**:
   - Store predictions
   - Track usage
   - User authentication

---

## 🧹 Cleanup & Maintenance

### Weekly
- [ ] Check logs for errors
- [ ] Monitor API response times
- [ ] Verify model accuracy

### Monthly
- [ ] Update dependencies
- [ ] Review error rate
- [ ] Check storage usage

### Quarterly
- [ ] Security audit
- [ ] Performance optimization
- [ ] User feedback review

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Read troubleshooting section
3. Search GitHub issues
4. Open new issue with:
   - Error message
   - Full logs
   - Steps to reproduce

---

**Your Avian AI is production-ready! 🚀🐦**
