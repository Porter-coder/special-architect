// Environment configuration for MiniMax API
export const config = {
  minimax: {
    apiKey: process.env.MINIMAX_API_KEY || '',
    groupId: process.env.MINIMAX_GROUP_ID || 'MiniMax-M2.1',
    baseUrl: 'https://api.minimaxi.com/anthropic'
  },
  system: {
    projectsRoot: process.env.PROJECTS_ROOT || '../projects'
  }
};