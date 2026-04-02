"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { twMerge } from "tailwind-merge";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300 disabled:pointer-events-none disabled:opacity-60 ring-offset-slate-950",
  {
    variants: {
      variant: {
        default:
          "bg-indigo-600 text-white shadow-[0_0_0_1px_rgba(99,102,241,0.25),0_0_30px_rgba(99,102,241,0.3)] hover:bg-indigo-500",
        secondary: "bg-white/10 text-slate-200 hover:bg-white/15 border border-white/10",
        destructive: "bg-rose-600 text-white hover:bg-rose-500",
      },
      size: {
        default: "h-10 px-4",
        sm: "h-9 px-3 text-xs",
        lg: "h-11 px-6 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  };

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={twMerge(cn(buttonVariants({ variant, size }), className))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };

