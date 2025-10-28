import { CreateTestContent } from "@/components/create-test-content";

export const dynamic = "force-dynamic";

export default function CreateTestPage() {
  return (
    <div className="flex-1 overflow-auto">
      <CreateTestContent />
    </div>
  );
}