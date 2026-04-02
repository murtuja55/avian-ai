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
  const apiBaseUrl =
    params.apiBaseUrl ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

  console.log("🎵 Uploading file:", params.file.name);
  console.log("🌐 API URL:", apiBaseUrl);

  const form = new FormData();
  // Backend expects form field name `file`
  form.append("file", params.file, params.file.name);

  try {
    console.log("📤 Sending request to:", `${apiBaseUrl}/predict`);
    
    // Create timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
    
    const res = await fetch(`${apiBaseUrl}/predict`, {
      method: "POST",
      body: form,
      signal: params.signal || controller.signal,
    });

    clearTimeout(timeoutId);

    console.log("📊 Response status:", res.status);
    console.log("📋 Response headers:", Object.fromEntries(res.headers.entries()));

    if (!res.ok) {
      const errorText = await res.text();
      console.error("❌ HTTP Error:", res.status, errorText);
      
      // Handle specific error cases
      if (res.status === 0) {
        throw new Error("Network error - unable to connect to server");
      } else if (res.status === 404) {
        throw new Error("API endpoint not found");
      } else if (res.status === 500) {
        throw new Error("Server error - please try again");
      } else {
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }
    }

    let data;
    try {
      data = await res.json();
      console.log("✅ API RESPONSE:", data);
    } catch (jsonError) {
      console.error("❌ JSON Parse Error:", jsonError);
      throw new Error("Invalid response format from server");
    }

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
          throw new Error("Unable to connect to server - please check if backend is running");
        } else if (error.message.includes("Failed to fetch")) {
          throw new Error("Network error - please check your connection");
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

