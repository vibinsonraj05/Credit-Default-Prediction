import type { NextConfig } from "next";

const isProduction = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "export",
  images: {
    unoptimized: true,
  },
  basePath: isProduction ? "/Credit-Default-Prediction" : "",
  trailingSlash: true,
};

export default nextConfig;