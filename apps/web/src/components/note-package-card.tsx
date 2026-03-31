"use client";

import { useState } from "react";
import { Heart, MessageCircle, Bookmark, MoreHorizontal } from "lucide-react";
import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface NotePackageCardProps {
  title: string;
  coverUrl?: string;
  score?: number;
  styleFamily?: string;
  complianceStatus?: "passed" | "failed" | "pending" | "review_needed" | "draft";
  likes?: number;
  comments?: number;
  onApprove?: () => void;
  onReject?: () => void;
  /** Phase 2 / BL-208: trigger on-demand generation for the same product */
  onGenerateMore?: () => void;
  generateMorePending?: boolean;
  className?: string;
}

export function NotePackageCard({
  title,
  coverUrl,
  score,
  styleFamily,
  complianceStatus = "draft",
  likes = 0,
  comments = 0,
  onApprove,
  onReject,
  onGenerateMore,
  generateMorePending = false,
  className,
}: NotePackageCardProps) {
  const [coverFailed, setCoverFailed] = useState(false);

  return (
    <Card className={cn("group overflow-hidden", className)}>
      {/* Cover image */}
      <div className="relative aspect-[3/4] overflow-hidden bg-gradient-to-br from-stone-100 to-stone-200">
        {coverUrl && !coverFailed ? (
          <img
            src={coverUrl}
            alt={title}
            className="h-full w-full object-cover"
            referrerPolicy="no-referrer"
            onError={() => setCoverFailed(true)}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <div className="text-center">
              <div className="mx-auto mb-2 h-12 w-12 rounded-xl bg-stone-300/50" />
              <p className="text-xs text-stone-400">封面预览</p>
            </div>
          </div>
        )}

        {/* Score badge */}
        {score !== undefined && (
          <div className="absolute top-2.5 right-2.5 flex h-8 w-8 items-center justify-center rounded-full bg-black/60 text-xs font-bold text-white backdrop-blur-sm">
            {score}
          </div>
        )}

        {/* Style family tag */}
        {styleFamily && (
          <div className="absolute bottom-2.5 left-2.5 rounded-md bg-black/50 px-2 py-1 text-[11px] text-white backdrop-blur-sm">
            {styleFamily}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-3.5">
        <div className="mb-2 flex items-start justify-between gap-2">
          <h3 className="line-clamp-2 text-sm font-medium leading-snug text-stone-900">
            {title}
          </h3>
          <button className="shrink-0 rounded p-0.5 text-stone-400 opacity-0 transition-opacity hover:text-stone-600 group-hover:opacity-100">
            <MoreHorizontal className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <StatusBadge status={complianceStatus} />
          <div className="flex items-center gap-3 text-stone-400">
            <span className="flex items-center gap-1 text-xs">
              <Heart className="h-3.5 w-3.5" />
              {likes}
            </span>
            <span className="flex items-center gap-1 text-xs">
              <MessageCircle className="h-3.5 w-3.5" />
              {comments}
            </span>
          </div>
        </div>

        {/* Action buttons for review */}
        {(onApprove || onReject || onGenerateMore) && (
          <div className="mt-3 space-y-2 border-t border-stone-100 pt-3">
            {(onApprove || onReject) && (
              <div className="flex gap-2">
                {onApprove && (
                  <button
                    type="button"
                    onClick={onApprove}
                    className="flex-1 rounded-md bg-emerald-50 py-1.5 text-xs font-medium text-emerald-700 transition-colors hover:bg-emerald-100"
                  >
                    通过
                  </button>
                )}
                {onReject && (
                  <button
                    type="button"
                    onClick={onReject}
                    className="flex-1 rounded-md bg-red-50 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-100"
                  >
                    拒绝
                  </button>
                )}
              </div>
            )}
            {onGenerateMore && (
              <button
                type="button"
                onClick={onGenerateMore}
                disabled={generateMorePending}
                className="w-full rounded-md border border-primary/25 bg-primary/5 py-1.5 text-xs font-medium text-primary-dark transition-colors hover:bg-primary/10 disabled:opacity-50"
              >
                {generateMorePending ? "生成中…" : "为此产品再生成一条"}
              </button>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
