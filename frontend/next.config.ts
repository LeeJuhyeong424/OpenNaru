import type { NextConfig } from "next";
import { codecovWebpackPlugin } from "@codecov/webpack-plugin";

const nextConfig: NextConfig = {
  output: "standalone",
  webpack: (config, { webpack }) => {
    config.plugins.push(
      codecovWebpackPlugin({
        enableBundleAnalysis: process.env.CODECOV_TOKEN !== undefined,
        bundleName: "opennaru-frontend",
        uploadToken: process.env.CODECOV_TOKEN,
        webpack,
      })
    );
    return config;
  },
};

export default nextConfig;
