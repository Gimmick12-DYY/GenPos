"use client";

import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const variants = {
  primary:
    "bg-primary text-white shadow-md shadow-primary/25 hover:bg-primary-dark active:bg-primary-dark/95",
  secondary:
    "border border-stone-200 bg-white text-stone-800 shadow-sm hover:bg-stone-50 active:bg-stone-100",
  ghost: "text-stone-600 hover:bg-stone-100/80 active:bg-stone-200/80",
  destructive:
    "bg-red-500 text-white shadow-sm hover:bg-red-600 active:bg-red-700",
  outline:
    "border border-stone-300 bg-transparent text-stone-800 hover:bg-stone-50 active:bg-stone-100",
} as const;

const sizes = {
  sm: "h-8 px-3 text-sm rounded-lg gap-1.5",
  md: "h-10 px-4 text-sm rounded-xl gap-2",
  lg: "h-12 px-6 text-base rounded-xl gap-2.5",
} as const;

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center font-medium transition-all duration-150 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "Button";
