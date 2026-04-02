"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";

type RecorderState = "idle" | "recording" | "processing";

function chooseMimeType() {
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/ogg",
    "audio/wav",
  ];
  for (const t of candidates) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    if (typeof MediaRecorder !== "undefined" && (MediaRecorder as any).isTypeSupported?.(t)) {
      return t;
    }
  }
  return "";
}

export function AudioRecorder(props: {
  onFileReady: (file: File) => void;
  disabled?: boolean;
}) {
  const [state, setState] = useState<RecorderState>("idle");
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const rafRef = useRef<number | null>(null);
  const mimeTypeRef = useRef<string>("");

  const stopWaveform = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    if (audioContextRef.current) {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    if (mediaStreamRef.current) {
      for (const track of mediaStreamRef.current.getTracks()) track.stop();
      mediaStreamRef.current = null;
    }
    analyserRef.current = null;
  }, []);

  const drawWaveform = useCallback(() => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    if (!canvas || !analyser) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { width, height } = canvas;
    const bufferLength = analyser.fftSize;
    const data = new Uint8Array(bufferLength);

    const draw = () => {
      if (!analyserRef.current) return;
      analyserRef.current.getByteTimeDomainData(data);

      ctx.clearRect(0, 0, width, height);

      ctx.lineWidth = 2;
      ctx.strokeStyle = "rgba(165, 180, 252, 0.9)"; // indigo-ish
      ctx.beginPath();

      const sliceWidth = width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = data[i] / 128.0;
        const y = (v * height) / 2;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
        x += sliceWidth;
      }

      ctx.lineTo(width, height / 2);
      ctx.stroke();

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);
  }, []);

  const start = useCallback(async () => {
    setError(null);

    if (props.disabled) return;

    try {
      setState("recording");
      chunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // Waveform (Web Audio API)
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      analyserRef.current = analyser;
      source.connect(analyser);

      drawWaveform();

      const mimeType = chooseMimeType();
      mimeTypeRef.current = mimeType;

      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      mediaRecorderRef.current = recorder;
      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.start();
    } catch (e) {
      setState("idle");
      setError((e as Error).message || "Microphone access failed.");
      stopWaveform();
    }
  }, [drawWaveform, props.disabled, stopWaveform]);

  const finish = useCallback(() => {
    const recorder = mediaRecorderRef.current;
    if (!recorder) return;

    setState("processing");

    recorder.onstop = () => {
      stopWaveform();

      const mimeType = mimeTypeRef.current || recorder.mimeType || "audio/webm";
      const blob = new Blob(chunksRef.current, { type: mimeType });

      const ext = mimeType.includes("wav")
        ? "wav"
        : mimeType.includes("ogg")
          ? "ogg"
          : "webm";

      const file = new File([blob], `recording.${ext}`, { type: mimeType });
      props.onFileReady(file);

      chunksRef.current = [];
      mediaRecorderRef.current = null;
      mimeTypeRef.current = "";
      setState("idle");
    };

    recorder.stop();
  }, [props, stopWaveform]);

  useEffect(() => {
    return () => {
      // Cleanup if unmounted during recording.
      try {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
          mediaRecorderRef.current.stop();
        }
      } catch {
        // ignore
      }
      stopWaveform();
    };
  }, [stopWaveform]);

  return (
    <div className="w-full">
      <div className="rounded-2xl border border-white/10 bg-white/3 p-5">
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between gap-3">
            <div className="text-sm text-slate-300">Record Audio</div>
            <div className="text-xs text-slate-500">
              {state === "recording" ? "Recording..." : state === "processing" ? "Preparing..." : "Ready"}
            </div>
          </div>

          <canvas
            ref={canvasRef}
            width={520}
            height={120}
            className="h-[120px] w-full rounded-xl bg-slate-950/30 ring-1 ring-white/10"
          />

          {error ? <div className="text-sm text-rose-300">{error}</div> : null}

          <div className="flex gap-3">
            {state !== "recording" ? (
              <Button
                className="flex-1"
                type="button"
                onClick={start}
                disabled={props.disabled}
                variant="default"
              >
                {props.disabled ? "Microphone unavailable" : "Record Audio"}
              </Button>
            ) : (
              <Button
                className="flex-1"
                type="button"
                onClick={finish}
                variant="destructive"
              >
                Stop & Analyze
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

