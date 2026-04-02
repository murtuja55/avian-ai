"use client";

import { useState, useCallback } from "react";
import { MicrophoneIcon, StopIcon } from "@heroicons/react/24/outline";

interface RecordCardProps {
  disabled?: boolean;
  onFileReady: (file: File) => void;
}

export function RecordCard({ disabled, onFileReady }: RecordCardProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [recordedChunks, setRecordedChunks] = useState<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const file = new File([blob], 'recording.webm', { type: 'audio/webm' });
        onFileReady(file);
        
        // Clean up
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setRecordedChunks(chunks);
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  }, [onFileReady]);

  const stopRecording = useCallback(() => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
      setMediaRecorder(null);
    }
  }, [mediaRecorder, isRecording]);

  const handleClick = useCallback(() => {
    if (disabled) return;
    
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [disabled, isRecording, startRecording, stopRecording]);

  return (
    <div className="relative group h-full">
      <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 to-orange-500/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300"></div>
      
      <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all duration-300 h-full flex flex-col justify-center">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className={`p-3 rounded-2xl border transition-all duration-300 ${
              isRecording 
                ? 'bg-red-500/10 border-red-500/20 animate-pulse' 
                : 'bg-red-500/10 border-red-500/20'
            }`}>
              <MicrophoneIcon className={`w-8 h-8 transition-colors duration-300 ${
                isRecording ? 'text-red-400' : 'text-red-400'
              }`} />
            </div>
          </div>
          
          <h3 className="text-xl font-semibold text-white mb-2">Record Audio</h3>
          <p className="text-sm text-slate-400 mb-6">Click to start recording</p>
          
          <button
            onClick={handleClick}
            disabled={disabled}
            className={`
              relative w-20 h-20 mx-auto rounded-full border-2 transition-all duration-300
              ${isRecording 
                ? 'bg-red-500 border-red-400 hover:bg-red-600' 
                : 'bg-white/5 border-slate-600 hover:bg-white/10 hover:border-slate-500'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {isRecording ? (
              <StopIcon className="w-8 h-8 text-white mx-auto" />
            ) : (
              <MicrophoneIcon className="w-8 h-8 text-slate-400 mx-auto" />
            )}
          </button>
          
          <div className="mt-4">
            <p className={`text-sm transition-colors duration-300 ${
              isRecording ? 'text-red-400 animate-pulse' : 'text-slate-500'
            }`}>
              {isRecording ? 'Recording...' : 'Ready to record'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
