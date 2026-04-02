"use client";

import { useCallback, useRef, useState } from "react";
import { Button } from "@/components/ui/button";

export function AudioDropzone(props: {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onPick = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const validate = useCallback((file: File) => {
    if (!file.type.startsWith("audio/")) return "Please select an audio file.";
    // Keep it reasonable for server inference.
    if (file.size > 25 * 1024 * 1024) return "Audio file is too large (max 25MB).";
    return null;
  }, []);

  const handleFile = useCallback(
    (file: File) => {
      const err = validate(file);
      if (err) {
        setError(err);
        return;
      }
      setError(null);
      props.onFileSelected(file);
    },
    [props, validate]
  );

  return (
    <div className="w-full">
      <input
        ref={inputRef}
        type="file"
        accept="audio/*"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
        disabled={props.disabled}
      />

      <div
        className={[
          "flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed p-6 text-center transition",
          isDragging ? "border-indigo-400/70 bg-indigo-500/10" : "border-white/15 bg-white/3",
          props.disabled ? "opacity-60" : "hover:border-indigo-300/60",
        ].join(" ")}
        role="button"
        tabIndex={0}
        onClick={props.disabled ? undefined : onPick}
        onKeyDown={(e) => {
          if (props.disabled) return;
          if (e.key === "Enter" || e.key === " ") onPick();
        }}
        onDragEnter={(e) => {
          e.preventDefault();
          if (!props.disabled) setIsDragging(true);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          if (!props.disabled) setIsDragging(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setIsDragging(false);
        }}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (props.disabled) return;
          const file = e.dataTransfer.files?.[0];
          if (file) handleFile(file);
        }}
      >
        <div className="text-sm text-slate-300">
          Drag & drop your audio here
        </div>
        <Button
          className="mt-1"
          disabled={props.disabled}
          type="button"
          onClick={props.disabled ? undefined : onPick}
        >
          Upload Audio
        </Button>
        <div className="text-xs text-slate-500">
          Supports mp3, wav, ogg, and other browser-decoded formats.
        </div>

        {error ? <div className="mt-3 text-sm text-rose-300">{error}</div> : null}
      </div>
    </div>
  );
}

