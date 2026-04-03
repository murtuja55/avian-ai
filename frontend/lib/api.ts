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
  // Use Hugging Face Spaces API with /predict endpoint
  const hfApiUrl = "https://murtu55-avian-ai-backend.hf.space/predict";
  
  console.log(" Uploading file:", params.file.name);
  console.log(" HF API URL:", hfApiUrl);

  try {
    // Create FormData for file upload
    const form = new FormData();
    form.append("file", params.file, params.file.name);
    
    console.log(" Sending file data to HF Spaces...");
    
    // Create timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout
    
    const res = await fetch(hfApiUrl, {
      method: "POST",
      body: form,
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
      console.error("❌ JSON Parse Error:", jsonError);
      throw new Error("Invalid response format from HF Spaces");
    }

    // Handle Flask API response format
    if (!data.success) {
      console.error("❌ API Error:", data.error);
      throw new Error(data.error || "Prediction failed");
    }

    return data;
  } catch (error) {
    console.error("❌ Fetch Error:", error);
    
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

export function resolveImageUrl(apiBaseUrl: string, imageUrl: string) {
  // Backend returns paths like `/images/sparrow.jpg`.
  if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) return imageUrl;
  return new URL(imageUrl, apiBaseUrl).toString();
}

