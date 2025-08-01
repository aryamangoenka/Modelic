/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    typedRoutes: true,
  },
  webpack: (config, { isServer }) => {
    // Suppress punycode deprecation warning
    config.ignoreWarnings = [
      { module: /node_modules\/punycode/ },
      /the `punycode` module is deprecated/,
    ];
    return config;
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
};

module.exports = nextConfig; 