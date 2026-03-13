import { cn } from "@/lib/utils";

const statusStyles = {
  passed: "bg-emerald-50 text-emerald-700 border-emerald-200",
  failed: "bg-red-50 text-red-700 border-red-200",
  pending: "bg-amber-50 text-amber-700 border-amber-200",
  review_needed: "bg-blue-50 text-blue-700 border-blue-200",
  draft: "bg-stone-100 text-stone-600 border-stone-200",
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
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
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
