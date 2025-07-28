import "./globals.css";
import { Navigation } from "@/components/ui/Navigation";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-dark-bg">
        <Navigation />
        {children}
      </body>
    </html>
  );
}
