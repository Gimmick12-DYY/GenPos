import { cn } from "@/lib/utils";

const statusStyles = {
  passed: "bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200/80",
  failed: "bg-red-50 text-red-800 ring-1 ring-red-200/80",
  pending: "bg-amber-50 text-amber-900 ring-1 ring-amber-200/80",
  review_needed: "bg-sky-50 text-sky-900 ring-1 ring-sky-200/80",
  draft: "bg-stone-100 text-stone-700 ring-1 ring-stone-200/80",
} as const;

interface BadgeProps {
  status: keyof typeof statusStyles;
  children: React.ReactNode;
  className?: string;
}

const statusLabels: Record<keyof typeof statusStyles, string> = {
  passed: "已通过",
  failed: "未通过",
  pending: "待审核",
  review_needed: "需修改",
  draft: "草稿",
};

export function Badge({ status, children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        statusStyles[status],
        className,
      )}
    >
      {children}
    </span>
  );
}

export function StatusBadge({
  status,
  className,
}: {
  status: keyof typeof statusStyles;
  className?: string;
}) {
  return (
    <Badge status={status} className={className}>
      {statusLabels[status]}
    </Badge>
  );
}
