import { RevengePlayersList } from "@/components/features/RevengePlayersList";

export default function Home() {
  return (
    <div className="bg-dark-bg min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <RevengePlayersList />
      </div>
    </div>
  );
}
