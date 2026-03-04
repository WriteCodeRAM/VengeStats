import type { Config } from "tailwindcss";

export default {
  // content: tells Tailwind which files to scan for class names
  // It only includes CSS for classes you actually use (tree-shaking)
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],

  theme: {
    extend: {
      colors: {
        "venge-red": "#BE181A",
        "dark-bg": "#09153F",
        "dark-card": "#1A1F2E",
        "text-primary": "#FFFFFF",
        // Flatten everything, no nested objects
      },
      fontFamily: {
        sora: ["Sora", "sans-serif"],
      },

      spacing: {
        "18": "4.5rem",
      },

      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
      },
    },
  },
  plugins: [],
} satisfies Config;
