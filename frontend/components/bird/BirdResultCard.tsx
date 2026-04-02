"use client";
import { Progress } from "@/components/ui/progress";

export function BirdResultCard(props: {
  status: "idle" | "analyzing" | "ready" | "error";
  bird?: string;
  confidence?: number; // 0..1
  imageSrc?: string;
  errorMessage?: string;
}) {
  const confidence = props.confidence ?? 0;
  const confidencePct = Math.max(0, Math.min(1, confidence)) * 100;

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-[0_0_0_1px_rgba(255,255,255,0.03),0_0_40px_rgba(79,70,229,0.08)] backdrop-blur">
      <div className="flex items-start gap-4">
        <div className="relative h-20 w-20 overflow-hidden rounded-xl bg-slate-900/40 ring-1 ring-white/10">
          {props.imageSrc ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              alt={props.bird ?? "Bird"}
              src={props.imageSrc}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="h-full w-full" />
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center justify-between gap-3">
            <div className="text-sm text-slate-300">
              {props.status === "analyzing" ? (
                <span className="inline-flex items-center gap-2">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-400" />
                  Analyzing...
                </span>
              ) : props.status === "error" ? (
                <span className="inline-flex items-center gap-2 text-rose-300">
                  <span className="h-2 w-2 rounded-full bg-rose-400" />
                  Error
                </span>
              ) : props.status === "idle" ? (
                <span className="inline-flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-slate-400/90" />
                  Waiting for audio...
                </span>
              ) : (
                <span className="text-green-400">✓ Bird Identified</span>
              )}
            </div>
          </div>

          <div className="mt-2">
            <div className="text-3xl font-bold tracking-tight text-white">
              {props.bird ?? "—"}
            </div>
          </div>

          {props.status === "error" && props.errorMessage ? (
            <div className="mt-3 text-sm text-rose-300">{props.errorMessage}</div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

