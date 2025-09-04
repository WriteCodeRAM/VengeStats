import "./globals.css";
import { Navigation } from "@/components/ui/Navigation";

export const metadata = {
  title: "VengeStats - NBA & NFL Revenge Games",
  description: "Track revenge games when players face their former teams",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "48x48" },
      { url: "/favicon-16x16.png", sizes: "16x16" },
      { url: "/favicon-32x32.png", sizes: "32x32" },
    ],
    apple: "/apple-touch-icon.png",
  },
};

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
