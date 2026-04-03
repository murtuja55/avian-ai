# Frontend Integration Guide

## 🚀 CONNECT TO HUGGING FACE SPACES BACKEND

### API Endpoint
```
POST https://murtu55-avian-ai-backend.hf.space/run/predict
```

### Request Format
```json
{
    "data": ["base64_encoded_audio_file"]
}
```

### Response Format
```json
{
    "data": ["**Prediction:** American Robin\n**Confidence:** 0.923 (92.3%)\n\n**Top 3 Predictions:**\n1. American Robin (0.923)\n2. Northern Cardinal (0.045)\n3. Blue Jay (0.012)"]
}
```

---

## 📋 HTML/JS IMPLEMENTATION

### 1. Copy the HTML file
- Use `html_integration.html` as your main page
- No external dependencies required
- Works with any web server

### 2. Key Features
- File upload with audio format validation
- Base64 conversion using FileReader
- Fetch API with proper error handling
- Loading states and result display
- Responsive design

### 3. Integration Steps
```html
<!-- Add this to your existing HTML -->
<script>
    // The predictBird() function handles everything
    // Just include the script and call it when needed
</script>
```

---

## ⚛️ REACT IMPLEMENTATION

### 1. Copy the React component
- Use `react_integration.jsx` as your main component
- Requires React with useState hook

### 2. Key Features
- useState for file, loading, result, error states
- File input with onChange handler
- Base64 conversion with FileReader
- Fetch API with async/await
- Conditional rendering for states

### 3. Integration Steps
```jsx
import AvianAI from './react_integration';

function App() {
    return (
        <div>
            <AvianAI />
            {/* Your other components */}
        </div>
    );
}
```

---

## 🔧 CUSTOMIZATION OPTIONS

### Change API Endpoint
```javascript
// In both HTML and React versions
const API_URL = 'https://murtu55-avian-ai-backend.hf.space/run/predict';
```

### Modify Styling
```css
/* HTML version - modify the <style> section */
/* React version - modify the styles object */
```

### Add Additional Features
- Audio preview player
- History of predictions
- Multiple file uploads
- Confidence visualization

---

## 🎯 TESTING

### 1. Test with Audio Files
- Use WAV, MP3, FLAC, M4A files
- Test with different bird sounds
- Verify error handling

### 2. Test Edge Cases
- No file selected
- Invalid file format
- Network errors
- Large files

### 3. Console Debugging
```javascript
// Add to script for debugging
console.log('Selected file:', file);
console.log('Base64 length:', base64.length);
console.log('API response:', result);
```

---

## 🚨 ERROR HANDLING

### Common Errors
1. **No file selected**: Shows error message
2. **Network timeout**: Shows network error
3. **API error**: Shows API response error
4. **Invalid format**: File input validation

### Error Display
- Red background for errors
- Clear error messages
- Automatic retry option

---

## 📱 MOBILE COMPATIBILITY

### Responsive Design
- Works on mobile devices
- Touch-friendly buttons
- Optimized file input

### Performance
- Base64 conversion optimized
- Efficient API calls
- Fast loading states

---

## ✅ DEPLOYMENT READY

Both implementations are production-ready:
- **HTML**: Standalone, no dependencies
- **React**: Component-based, easy integration
- **API**: Proper error handling and loading states
- **UI**: Clean, professional design

Choose the version that matches your frontend stack and integrate!
