/** @type {import('next').NextConfig} */

module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  i18n: { locales: ["en"], defaultLocale: "en" },
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: true,
        ignored: "/node_modules",
      };
    }
    return config;
  },
};
