"use client";
import Image from "next/image";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScoringModal } from "@/components/features/ScoringModal";
import { useRouter } from "next/navigation";

export function Navigation() {
  const router = useRouter();
  const handleClick = () => {
    router.push("/");
  };

  return (
    <nav className="bg-dark-bg border-b border-borderDefault px-4 py-4">
      <div className="max-w-7xl mx-auto">
        {/* Desktop Layout */}
        <div className="hidden md:flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <Image
              src="/logo.png"
              alt="VengeStats Logo"
              width={200}
              height={60}
              priority
              className="object-contain cursor-pointer"
              onClick={handleClick}
            />
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-md mx-8">
            <Input
              placeholder="Search players, teams, or revenge matchups..."
              className="bg-dark-card border-borderDefault text-white placeholder:text-text-secondary focus:border-venge-red"
            />
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-4">
            <ScoringModal>
              <Button
                variant="ghost"
                className="text-text-secondary hover:text-venge-red hover:bg-transparent"
              >
                How Scoring Works
              </Button>
            </ScoringModal>

            <Button
              variant="ghost"
              size="icon"
              asChild
              className="text-text-secondary hover:text-white hover:bg-transparent"
            >
              <a
                href="https://twitter.com/vengestats"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Follow VengeStats on Twitter"
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>
            </Button>
          </div>
        </div>

        {/* Mobile Layout */}
        <div className="md:hidden space-y-4">
          {/* Top row: Logo + Icons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Image
                src="/logo.png"
                alt="VengeStats Logo"
                width={150}
                height={45}
                priority
                className="object-contain cursor-pointer"
                onClick={handleClick}
              />
            </div>

            <div className="flex items-center gap-2">
              <ScoringModal>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-text-secondary hover:text-venge-red hover:bg-transparent text-xs"
                >
                  Scoring
                </Button>
              </ScoringModal>

              <Button
                variant="ghost"
                size="icon"
                asChild
                className="text-text-secondary hover:text-white hover:bg-transparent"
              >
                <a
                  href="https://twitter.com/vengestats"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Follow VengeStats on Twitter"
                >
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </a>
              </Button>
            </div>
          </div>

          <div className="w-full">
            <Input
              placeholder="Search players, teams..."
              className="bg-dark-card border-borderDefault text-white placeholder:text-text-secondary focus:border-venge-red w-full"
            />
          </div>
        </div>
      </div>
    </nav>
  );
}
