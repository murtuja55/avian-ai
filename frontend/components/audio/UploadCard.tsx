"use client";

import { useCallback, useState } from "react";
import { CloudArrowUpIcon } from "@heroicons/react/24/outline";

interface UploadCardProps {
  disabled?: boolean;
  onFileSelected: (file: File) => void;
}

export function UploadCard({ disabled, onFileSelected }: UploadCardProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const audioFile = files.find(file => 
      file.type.startsWith("audio/") || 
      file.name.match(/\.(wav|mp3|m4a|ogg|flac)$/i)
    );

    if (audioFile && !disabled) {
      onFileSelected(audioFile);
    }
  }, [disabled, onFileSelected]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && !disabled) {
      onFileSelected(file);
    }
  }, [disabled, onFileSelected]);

  return (
    <div className="relative group h-full">
      <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all duration-300 h-full flex flex-col justify-center">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-2xl border border-blue-500/20">
              <CloudArrowUpIcon className="w-8 h-8 text-blue-400" />
            </div>
          </div>
          
          <h3 className="text-xl font-semibold text-white mb-2">Upload Audio</h3>
          <p className="text-sm text-slate-400 mb-6">Upload a bird sound (5–20 seconds recommended)</p>
          
          <div
            className={`
              relative border-2 border-dashed rounded-xl p-8 transition-all duration-300
              ${isDragOver 
                ? 'border-blue-400 bg-blue-500/5' 
                : 'border-slate-600 hover:border-slate-500'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !disabled && document.getElementById('file-upload')?.click()}
          >
            <input
              id="file-upload"
              type="file"
              accept="audio/*,.wav,.mp3,.m4a,.ogg,.flac"
              onChange={handleFileSelect}
              disabled={disabled}
              className="hidden"
            />
            
            <div className="flex flex-col items-center space-y-3">
              <CloudArrowUpIcon className="w-12 h-12 text-slate-500" />
              <p className="text-sm text-slate-400">
                {isDragOver ? 'Drop your audio file here' : 'Support: WAV, MP3, M4A'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
