import "./globals.css";
import { Navigation } from "@/components/ui/Navigation";
import { GoogleAnalytics } from "@next/third-parties/google";

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
