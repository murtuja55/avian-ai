"use client";

import Link from "next/link";
import { useCallback, useMemo, useState } from "react";
import { UploadCard } from "@/components/audio/UploadCard";
import { ResultModal } from "@/components/bird/ResultModal";
import { predictBirdAudio, type PredictResponse } from "@/lib/api";

type Status = "idle" | "analyzing" | "ready" | "error";

export default function DetectPage() {
  const apiBaseUrl = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "",
    []
  );

  const [status, setStatus] = useState<Status>("idle");
  const [bird, setBird] = useState<string | undefined>(undefined);
  const [confidence, setConfidence] = useState<number | undefined>(undefined);
  const [imageSrc, setImageSrc] = useState<string | undefined>(undefined);
  const [audioSrc, setAudioSrc] = useState<string | undefined>(undefined);
  const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showAbout, setShowAbout] = useState(false);

  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const handleAboutClick = () => {
    console.log('About button clicked - scrolling to about section');
    const aboutSection = document.getElementById('about-section');
    if (aboutSection) {
      aboutSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleBackToUpload = () => {
    console.log('Back to Upload button clicked - scrolling to top');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const analyze = useCallback(
    async (file: File) => {
      // Cancel any in-flight request.
      abortController?.abort();
      const controller = new AbortController();
      setAbortController(controller);

      // Open modal and set loading state
      setIsModalOpen(true);
      setStatus("analyzing");
      setErrorMessage(undefined);
      setBird(undefined);
      setImageSrc(undefined);
      setAudioSrc(undefined);

      try {
        console.log("🚀 Starting analysis for file:", file.name);
        
        const resp: PredictResponse = await predictBirdAudio({
          file,
          apiBaseUrl,
          signal: controller.signal,
        });

        console.log("✅ Prediction received:", resp);

        // Get prediction from response
        if (resp.success && resp.prediction) {
          setBird(resp.prediction);
          setConfidence(resp.confidence || 0);
          // Use actual audio URL from backend
          if (resp.audio_url) {
            const audioUrl = resp.audio_url.startsWith('http') 
              ? resp.audio_url 
              : resp.audio_url;
            setAudioSrc(audioUrl);
          }
          // Create dummy image URL for now
          setImageSrc("/api/bird-image");
          setStatus("ready");
          console.log("🎉 Success! Status set to ready");
        } else {
          console.error("❌ Invalid response:", resp);
          throw new Error(resp.error || "No prediction received");
        }
      } catch (e) {
        console.error("❌ Analysis error:", e);
        if ((e as Error).name === "AbortError") return;
        setStatus("error");
        const errorMessage = (e as Error).message || "Failed to analyze audio.";
        setErrorMessage(errorMessage);
        console.error("❌ Error message set:", errorMessage);
        
        // Ensure error is visible to user
        console.error("❌ Full error details:", {
          name: (e as Error).name,
          message: (e as Error).message,
          stack: (e as Error).stack
        });
      }
    },
    [abortController, apiBaseUrl]
  );

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
    setStatus("idle");
    setBird(undefined);
    setConfidence(undefined);
    setImageSrc(undefined);
    setAudioSrc(undefined);
    setErrorMessage(undefined);
  }, []);

  const birdSpecies = [
    "American Robin", "Blue Jay", "Cardinal", "Chickadee", "Crow",
    "Eagle", "Finch", "Goldfinch", "Hawk", "Hummingbird",
    "Junco", "Kinglet", "Lark", "Martin", "Nuthatch",
    "Oriole", "Pigeon", "Quail", "Robin", "Sparrow",
    "Titmouse", "Upland Sandpiper", "Vireo", "Warbler", "Xenops",
    "Yellowthroat", "Zebra Finch", "Barn Owl", "Cedar Waxwing",
    "Dark-eyed Junco", "Eastern Bluebird", "Flamingo", "Grackle",
    "Hermit Thrush", "Indigo Bunting", "Jay", "Kestrel", "Loon",
    "Meadowlark", "Nightingale", "Osprey", "Peregrine Falcon", "Quail Dove",
    "Red-tailed Hawk", "Swallow", "Tanager", "Umbrellabird", "Vulture",
    "White-breasted Nuthatch", "Yellow Warbler", "Zonotrichia"
  ];

  if (showAbout) {
    return (
      <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent"></div>
        
        {/* Modern Navbar */}
        <div className="relative z-10 sticky top-0">
          <div className="bg-slate-900/50 backdrop-blur-sm border-b border-white/10">
            <div className="flex justify-between items-center px-6 py-4">
              {/* App Name */}
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                  <span className="text-white text-lg font-bold">🐦</span>
                </div>
                <div>
                  <span className="text-2xl font-bold text-white">Avian</span>
                  <span className="text-lg font-semibold text-slate-300 ml-2">AI</span>
                </div>
              </div>
              
              {/* Navigation Tabs */}
              <div className="flex items-center gap-2">
                <Link href="/" className="px-4 py-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-full text-sm font-medium transition-all duration-300">
                  ← Back
                </Link>
                <button className="px-4 py-2 bg-blue-500 text-white rounded-full text-sm font-medium hover:bg-blue-400 transition-all duration-300 shadow-lg shadow-blue-500/25">
                  Upload
                </button>
                <Link href="/about" className="px-4 py-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-full text-sm font-medium transition-all duration-300">
                  About
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* About Content */}
        <div className="relative z-10 flex items-start justify-center min-h-[calc(100vh-120px)] px-6 pt-20">
          <div className="w-full max-w-6xl">
            {/* Header */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-4 px-8 py-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-2xl">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-purple-400 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-2xl font-bold">ℹ️</span>
                </div>
                <div className="text-left">
                  <h1 className="text-3xl font-bold text-white mb-2">About Avian AI</h1>
                  <p className="text-slate-400 text-lg">Advanced Bird Sound Recognition System</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Project Overview */}
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                  <span className="w-8 h-8 bg-gradient-to-r from-green-400 to-emerald-400 rounded-xl flex items-center justify-center">
                    <span className="text-white text-lg">🎯</span>
                  </span>
                  Project Overview
                </h2>
                <div className="space-y-4 text-slate-300">
                  <p className="text-lg leading-relaxed">
                    Avian AI is a cutting-edge bird sound recognition system that uses advanced deep learning techniques to identify bird species from audio recordings. Our system can accurately identify 50 different bird species with high confidence scores.
                  </p>
                  <div className="grid grid-cols-2 gap-4 mt-6">
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                      <div className="text-3xl font-bold text-white mb-2">50+</div>
                      <div className="text-sm text-slate-400">Bird Species</div>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                      <div className="text-3xl font-bold text-white mb-2">75%</div>
                      <div className="text-sm text-slate-400">Accuracy Rate</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Technologies Used */}
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                  <span className="w-8 h-8 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-xl flex items-center justify-center">
                    <span className="text-white text-lg">⚙️</span>
                  </span>
                  Technologies Used
                </h2>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-bold text-white mb-4">Frontend Development</h3>
                    <div className="space-y-3 text-slate-300">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                        <span className="text-lg">Next.js 14 - React Framework</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                        <span className="text-lg">Tailwind CSS - Styling</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                        <span className="text-lg">TypeScript - Type Safety</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-xl font-bold text-white mb-4">Backend Development</h3>
                    <div className="space-y-3 text-slate-300">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        <span className="text-lg">Flask - Python Web Framework</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                        <span className="text-lg">PyTorch - Deep Learning</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                        <span className="text-lg">Librosa - Audio Processing</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-xl font-bold text-white mb-4">AI & ML Technologies</h3>
                    <div className="space-y-3 text-slate-300">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-pink-400 rounded-full"></div>
                        <span className="text-lg">Convolutional Neural Networks</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                        <span className="text-lg">Audio Feature Extraction</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-indigo-400 rounded-full"></div>
                        <span className="text-lg">Spectrogram Analysis</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bird Species List */}
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                  <span className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-xl flex items-center justify-center">
                    <span className="text-white text-lg">🦜</span>
                  </span>
                  Recognized Bird Species (50 Species)
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {birdSpecies.map((species, index) => (
                    <div key={index} className="bg-white/5 border border-white/10 rounded-lg p-3 hover:bg-white/10 transition-all duration-300">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full"></div>
                        <span className="text-white font-medium">{species}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-6 text-center">
          <div className="text-slate-400 text-sm">
            Built with ❤️ using Deep Learning | Avian AI Bird Sound Classification
          </div>
        </div>

        {/* Result Modal */}
        <ResultModal
          isOpen={isModalOpen}
          onClose={closeModal}
          bird={bird}
          confidence={confidence}
          imageSrc={imageSrc}
          audioSrc={audioSrc}
          isLoading={status === "analyzing"}
          hasError={status === "error"}
        />

        {/* Global Styles */}
        <style jsx>{`
          @keyframes fade-in-scale {
            from {
              opacity: 0;
              transform: scale(0.9);
            }
            to {
              opacity: 1;
              transform: scale(1);
            }
          }
          
          .animate-fade-in-scale {
            animation: fade-in-scale 0.3s ease-out;
          }
          
          .animate-spin {
            animation: spin 1s linear infinite;
          }
          
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent"></div>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent"></div>
      
      {/* Modern Navbar */}
      <div className="relative z-10 sticky top-0">
        <div className="bg-slate-900/50 backdrop-blur-sm border-b border-white/10">
          <div className="flex justify-between items-center px-6 py-4">
            {/* App Name */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                <span className="text-white text-lg font-bold">🐦</span>
              </div>
              <div>
                <span className="text-2xl font-bold text-white">Avian</span>
                <span className="text-lg font-semibold text-slate-300 ml-2">AI</span>
              </div>
            </div>
            
            {/* Navigation Tabs */}
            <div className="flex items-center gap-2">
              <Link href="/" className="px-4 py-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-full text-sm font-medium transition-all duration-300">
                ← Back
              </Link>
              <button className="px-4 py-2 bg-blue-500 text-white rounded-full text-sm font-medium hover:bg-blue-400 transition-all duration-300 shadow-lg shadow-blue-500/25">
                Upload
              </button>
              <Link href="/about" className="px-4 py-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-full text-sm font-medium transition-all duration-300">
                About
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Centered Upload */}
      <div className="relative z-10 flex items-center justify-center min-h-[calc(100vh-120px)] px-6 pt-20">
        
        {/* Single Centered Upload Card */}
        <div className="w-full max-w-2xl">
          <UploadCard
            disabled={status === "analyzing"}
            onFileSelected={(file) => {
              void analyze(file).catch((e) => {
                setStatus("error");
                setErrorMessage((e as Error).message || "Invalid file.");
              });
            }}
          />
          
          {/* Details Section */}
          <div className="mt-8 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-xl">
              <div className="h-2 w-2 rounded-full bg-green-400"></div>
              <span className="text-sm text-slate-300">
                50 Bird Species Trained
              </span>
            </div>
            
            <div className="mt-4 max-w-lg mx-auto">
              <p className="text-sm text-slate-400 leading-relaxed">
                Our AI model has been trained on 50 different bird species with high accuracy. 
                Upload any bird sound recording to get instant species identification with confidence scores.
              </p>
            </div>
            
            <div className="mt-6 grid grid-cols-2 gap-4 max-w-md mx-auto">
              <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                <div className="text-lg font-semibold text-white">75%</div>
                <div className="text-xs text-slate-400">Accuracy Rate</div>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                <div className="text-lg font-semibold text-white">2-3s</div>
                <div className="text-xs text-slate-400">Processing Time</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Result Modal */}
      <ResultModal
        isOpen={isModalOpen}
        onClose={closeModal}
        bird={bird}
        confidence={confidence}
        imageSrc={imageSrc}
        audioSrc={audioSrc}
        isLoading={status === "analyzing"}
        hasError={status === "error"}
      />

      {/* Global Styles */}
      <style jsx>{`
        @keyframes fade-in-scale {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        .animate-fade-in-scale {
          animation: fade-in-scale 0.3s ease-out;
        }
        
        .animate-spin {
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
