// Environment configuration for MiniMax API
export const config = {
  minimax: {
    apiKey: process.env.MINIMAX_API_KEY || 'sk-cp-J0VMxT-lS-ywqjuZ4gy-70BmOTZY3q4aRjNVe2TRLEUhZC9aRirBjKGJALNrIVbKa3--ydf1wpC1ynIN1fBtDQHC5e0m7w1vUhxo74J8JMQ5FOCMUnJ7ldc',
    groupId: process.env.MINIMAX_GROUP_ID || 'MiniMax-M2.1',
    baseUrl: 'https://api.minimaxi.com/anthropic'
  },
  system: {
    projectsRoot: process.env.PROJECTS_ROOT || '../projects'
  }
};