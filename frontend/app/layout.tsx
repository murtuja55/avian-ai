import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { RouteTransition } from "@/components/RouteTransition";

export const metadata: Metadata = {
  title: "Bird Sound Recognition System",
  description: "AI-powered bird sound recognition",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body>
        <RouteTransition>{children}</RouteTransition>
      </body>
    </html>
  );
}

