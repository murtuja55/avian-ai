"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export default function LandingPage() {
  return (
    <div className="relative flex min-h-[100vh] items-center justify-center overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900" />
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute -left-28 top-[-120px] h-[280px] w-[280px] rounded-full bg-indigo-600/30 blur-3xl"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      />
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute -right-28 bottom-[-120px] h-[280px] w-[280px] rounded-full bg-fuchsia-600/25 blur-3xl"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut", delay: 0.08 }}
      />

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 flex w-full max-w-xl flex-col items-center gap-6 px-6 text-center"
      >
        <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 shadow-glow">
          <span className="h-2 w-2 rounded-full bg-indigo-400" />
          <span>Real-time bird detection</span>
        </div>

        <h1 className="text-balance text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          Bird Sound Recognition System
        </h1>

        <p className="text-pretty text-lg text-slate-300">
          AI-powered bird sound recognition
        </p>

        <Link
          href="/detect"
          className="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-[0_0_0_1px_rgba(99,102,241,0.25),0_0_30px_rgba(99,102,241,0.35)] transition hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        >
          Start Detection
        </Link>

        <p className="max-w-[42ch] text-sm text-slate-400">
          Upload an audio clip or record directly in your browser.
        </p>
      </motion.div>
    </div>
  );
}

