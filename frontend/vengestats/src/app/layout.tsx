import "./globals.css";
import { Navigation } from "@/components/ui/Navigation";
import { GoogleAnalytics } from "@next/third-parties/google";

export const metadata = {
  title: "VengeStats - NBA & NFL Revenge Games",
  description:
    "Discover when players face their former teams with detailed revenge game analytics, performance stats, and vengeance scores. Track NFL and NBA players seeking redemption against old squads.",
  keywords:
    "revenge games, NFL stats, NBA analytics, former team matchups, player performance, sports statistics",
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
      <GoogleAnalytics gaId={process.env.GA_MEASUREMENT_ID!} />
    </html>
  );
}
