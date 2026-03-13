"use client";

import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const variants = {
  primary:
    "bg-primary text-white hover:bg-primary-dark active:bg-primary-dark/90 shadow-sm",
  secondary:
    "bg-stone-100 text-stone-700 hover:bg-stone-200 active:bg-stone-300",
  ghost: "text-stone-600 hover:bg-stone-100 active:bg-stone-200",
  destructive:
    "bg-red-500 text-white hover:bg-red-600 active:bg-red-700 shadow-sm",
  outline:
    "border border-stone-300 text-stone-700 hover:bg-stone-50 active:bg-stone-100",
} as const;

const sizes = {
  sm: "h-8 px-3 text-sm rounded-md gap-1.5",
  md: "h-10 px-4 text-sm rounded-lg gap-2",
  lg: "h-12 px-6 text-base rounded-lg gap-2.5",
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
        "inline-flex items-center justify-center font-medium transition-colors duration-150 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "Button";
