/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow API routes to access file system
  serverRuntimeConfig: {
    PROJECTS_ROOT: process.env.PROJECTS_ROOT || '../projects',
  },
  // Disable static optimization for API routes
  generateBuildId: async () => {
    return 'build-' + Date.now()
  },
}

module.exports = nextConfig
