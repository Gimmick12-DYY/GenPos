"use client";

import { cn } from "@/lib/utils";

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  className?: string;
}

export function Toggle({
  checked,
  onChange,
  label,
  description,
  disabled = false,
  className,
}: ToggleProps) {
  return (
    <label
      className={cn(
        "flex items-center gap-3 select-none",
        disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer",
        className,
      )}
    >
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors duration-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary",
          checked ? "bg-primary" : "bg-stone-300",
        )}
      >
        <span
          className={cn(
            "inline-block h-4.5 w-4.5 rounded-full bg-white shadow-sm transition-transform duration-200",
            checked ? "translate-x-5.5" : "translate-x-0.5",
          )}
        />
      </button>
      {(label || description) && (
        <div className="min-w-0">
          {label && (
            <span className="text-sm font-medium text-stone-700">{label}</span>
          )}
          {description && (
            <p className="text-xs text-stone-500">{description}</p>
          )}
        </div>
      )}
    </label>
  );
}
