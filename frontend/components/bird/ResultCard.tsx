"use client";

interface ResultCardProps {
  bird?: string;
  imageSrc?: string;
  isLoading?: boolean;
  hasError?: boolean;
}

export function ResultCard({ bird, imageSrc, isLoading, hasError }: ResultCardProps) {
  if (isLoading) {
    return (
      <div className="relative group h-full">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-3xl blur-xl"></div>
        
        <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 h-full flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-purple-400/30 border-t-purple-400 rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-white text-lg">Analyzing audio...</p>
          </div>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="relative group h-full">
        <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 to-orange-500/20 rounded-3xl blur-xl"></div>
        
        <div className="relative bg-white/5 backdrop-blur-xl border border-red-500/20 rounded-3xl p-8 h-full flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚠️</span>
            </div>
            <p className="text-red-400 text-lg">Failed to analyze audio</p>
            <p className="text-slate-400 text-sm mt-2">Please try again</p>
          </div>
        </div>
      </div>
    );
  }

  if (!bird) {
    return (
      <div className="relative group h-full">
        <div className="absolute inset-0 bg-gradient-to-r from-slate-500/10 to-slate-500/10 rounded-3xl blur-xl"></div>
        
        <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 h-full flex items-center justify-center">
          <div className="text-center">
            <div className="w-24 h-24 bg-slate-700/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">🎵</span>
            </div>
            <p className="text-slate-400 text-lg">No result yet</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative group h-full animate-fade-in">
      <div className="absolute inset-0 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-3xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
      
      <div className="relative bg-white/5 backdrop-blur-xl border border-green-500/20 rounded-3xl p-8 h-full flex flex-col items-center justify-center">
        {/* Large Bird Image */}
        <div className="w-64 h-64 bg-white/10 rounded-3xl border border-white/20 overflow-hidden mb-6 ring-4 ring-green-400/20">
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
            <span className="text-6xl">🦅</span>
          </div>
        </div>
        
        {/* Bird Name */}
        <h2 className="text-5xl font-bold text-white mb-4 tracking-tight">
          {bird.toUpperCase()}
        </h2>
        
        {/* Success Indicator */}
        <div className="flex items-center gap-2 text-green-400">
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          <span className="text-sm">Bird Identified</span>
        </div>
      </div>
    </div>
  );
}
