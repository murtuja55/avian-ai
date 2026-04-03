export type PredictResponse = {
  success: boolean;
  prediction?: string;
  confidence?: number;
  top_predictions?: Array<{
    label: string;
    confidence: number;
  }>;
  audio_url?: string;
  error?: string;
};

export async function predictBirdAudio(params: {
  file: File;
  apiBaseUrl?: string;
  signal?: AbortSignal;
}): Promise<PredictResponse> {
  // Use Hugging Face Spaces API
  const hfApiUrl = "https://murtu55-avian-ai-backend.hf.space/run/predict";
  
  console.log(" Uploading file:", params.file.name);
  console.log(" HF API URL:", hfApiUrl);

  try {
    // Convert file to base64
    const base64 = await fileToBase64(params.file);
    
    console.log(" Sending base64 data to HF Spaces...");
    
    // Create timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout
    
    const res = await fetch(hfApiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        "data": [base64]
      }),
      signal: params.signal || controller.signal,
    });

    clearTimeout(timeoutId);

    console.log(" Response status:", res.status);
    console.log(" Response headers:", Object.fromEntries(res.headers.entries()));

    if (!res.ok) {
      const errorText = await res.text();
      console.error("❌ HTTP Error:", res.status, errorText);
      
      // Handle specific error cases
      if (res.status === 0) {
        throw new Error("Network error - unable to connect to Hugging Face Spaces");
      } else if (res.status === 404) {
        throw new Error("HF Spaces endpoint not found");
      } else if (res.status === 500) {
        throw new Error("HF Spaces server error - please try again");
      } else if (res.status === 413) {
        throw new Error("Audio file too large - please use a smaller file");
      } else if (res.status === 400) {
        throw new Error("Invalid audio format - please use WAV, MP3, FLAC, or M4A");
      } else {
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }
    }

    let data;
    try {
      data = await res.json();
      console.log(" HF Spaces API RESPONSE:", data);
    } catch (jsonError) {
      console.error(" JSON Parse Error:", jsonError);
      throw new Error("Invalid response format from HF Spaces");
    }

    // Handle HF Spaces response format
    if (!data.data || !Array.isArray(data.data) || data.data.length === 0) {
      console.error(" Invalid HF Spaces response:", data);
      throw new Error("No prediction data received from HF Spaces");
    }

    // Parse the prediction result from HF Spaces
    const predictionText = data.data[0];
    console.log(" Prediction text:", predictionText);

    // Extract bird species and confidence from the text
    const predictionMatch = predictionText.match(/\*\*Prediction:\*\* (.+)/);
    const confidenceMatch = predictionText.match(/\*\*Confidence:\*\* ([\d.]+)/);
    
    const bird = predictionMatch ? predictionMatch[1].trim() : "Unknown";
    const confidence = confidenceMatch ? parseFloat(confidenceMatch[1]) : 0;

    return {
      success: true,
      prediction: bird,
      confidence: confidence,
      top_predictions: [], // HF Spaces returns formatted text, not structured data
      audio_url: undefined, // HF Spaces doesn't return audio URL
    };
  } catch (error) {
    console.error(" Fetch Error:", error);
    
    // Handle specific error types
    if (error instanceof Error) {
      if (error.name === "AbortError") {
        throw new Error("Request cancelled");
      } else if (error.message.includes("Network error")) {
        throw new Error("Unable to connect to Hugging Face Spaces - please check if backend is running");
      } else if (error.message.includes("Failed to fetch")) {
        throw new Error("Network error - please check your connection to HF Spaces");
      } else {
        throw error;
      }
    } else {
      throw new Error("Unknown error occurred");
    }
  }
}

// Helper function to convert file to base64
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      // Get the base64 part (remove data:audio/...;base64, prefix)
      const base64Data = reader.result as string;
      const base64 = base64Data.split(',')[1];
      resolve(base64);
    };
    reader.onerror = error => reject(error);
    reader.readAsDataURL(file);
  });
}

export function resolveImageUrl(apiBaseUrl: string, imageUrl: string) {
  // Backend returns paths like `/images/sparrow.jpg`.
  if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) return imageUrl;
  return new URL(imageUrl, apiBaseUrl).toString();
}

