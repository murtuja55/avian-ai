"use client";

import { useEffect } from "react";

interface ResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  bird?: string;
  confidence?: number;
  imageSrc?: string;
  audioSrc?: string;
  isLoading?: boolean;
  hasError?: boolean;
}

export function ResultModal({ isOpen, onClose, bird, confidence, imageSrc, audioSrc, isLoading, hasError }: ResultModalProps) {
  // Close on ESC key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop with blur */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 max-w-md w-full shadow-2xl ring-4 ring-white/10 animate-fade-in-scale">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-white/10 border border-white/20 hover:bg-white/20 transition-colors"
        >
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Modal Content */}
        <div className="flex flex-col items-center">
          {isLoading ? (
            // Loading State
            <div className="text-center py-12">
              <div className="w-16 h-16 border-4 border-purple-400/30 border-t-purple-400 rounded-full animate-spin mx-auto mb-6"></div>
              <p className="text-white text-lg">Analyzing audio...</p>
            </div>
          ) : hasError ? (
            // Error State
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">⚠️</span>
              </div>
              <p className="text-red-400 text-lg mb-2">Failed to analyze audio</p>
              <p className="text-slate-400 text-sm">Please try again</p>
            </div>
          ) : bird ? (
            // Success State
            <div className="text-center py-8">
              {/* Medium Bird Image */}
              <div className="w-48 h-48 bg-white/10 rounded-2xl border border-white/20 overflow-hidden mb-6 ring-4 ring-green-400/20">
                {imageSrc ? (
                  <img
                    src={imageSrc}
                    alt={bird}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      // Fallback to placeholder if image fails
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const fallback = target.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'flex';
                    }}
                  />
                ) : null}
                {/* Fallback placeholder */}
                <div className="w-full h-full items-center justify-center bg-gradient-to-br from-green-500/20 to-emerald-500/20" style={{display: imageSrc ? 'none' : 'flex'}}>
                  <span className="text-5xl">🦅</span>
                </div>
              </div>
              
              {/* Audio Player */}
              {audioSrc && (
                <div className="mb-6">
                  <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.1-.9 2-2 2s2-.9 2-2 2-2-.9-2-2z" />
                        </svg>
                      </div>
                      <span className="text-sm font-medium text-white">Audio Playback</span>
                    </div>
                    <audio 
                      controls 
                      className="w-full"
                      preload="metadata"
                    >
                      <source src={audioSrc} type="audio/mpeg" />
                      <source src={audioSrc} type="audio/wav" />
                      <source src={audioSrc} type="audio/ogg" />
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                </div>
              )}
              
              {/* Bird Name */}
              <h2 className="text-4xl font-bold text-white mb-2 tracking-tight">
                {bird.toUpperCase()}
              </h2>
              
              {/* Species Count */}
              <div className="text-sm text-slate-400 mb-4">
                <span className="text-white font-medium">1 of 50</span> species identified
              </div>
              
              {/* Confidence Display */}
              {confidence !== undefined && (
                <div className="mb-4">
                  <div className="flex items-center justify-center gap-3 mb-2">
                    <span className="text-sm text-slate-400">Confidence</span>
                    <div className="flex-1 max-w-xs">
                      <div className="bg-white/10 rounded-full h-2 overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-green-400 to-emerald-400 rounded-full transition-all duration-500"
                          style={{ width: `${confidence * 100}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-white">
                      {(confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  
                  {/* Confidence Level */}
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs">
                    {confidence >= 0.8 ? (
                      <>
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        <span className="text-green-400">High Confidence</span>
                      </>
                    ) : confidence >= 0.6 ? (
                      <>
                        <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                        <span className="text-yellow-400">Medium Confidence</span>
                      </>
                    ) : (
                      <>
                        <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                        <span className="text-orange-400">Low Confidence</span>
                      </>
                    )}
                  </div>
                </div>
              )}
              
              {/* Success Indicator */}
              <div className="flex items-center gap-2 text-green-400">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm">Bird Identified</span>
              </div>
            </div>
          ) : (
            // Empty State
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-slate-700/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">🎵</span>
              </div>
              <p className="text-slate-400 text-lg">No result yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
