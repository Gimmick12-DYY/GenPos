import { WorkspaceLayout } from "@/components/layout/workspace-layout";

export default function WorkspaceGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <WorkspaceLayout>{children}</WorkspaceLayout>;
}
