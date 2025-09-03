/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ["cdn.nba.com"],
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
