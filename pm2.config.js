module.exports = {
  apps: [
    {
      name: 'asean-backend',
      script: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/backend/venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000 --workers 2',
      cwd: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/backend',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/backend',
        AGNES_API_KEY: process.env.AGNES_API_KEY || '',
        AGNES_API_URL: 'https://api.agnes.ai/v1'
      },
      max_memory_restart: '500M',
      error_file: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/logs/backend.err.log',
      out_file: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/logs/backend.out.log',
      log_file: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/logs/backend.combine.log',
      time: true
    },
    {
      name: 'asean-frontend',
      script: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/frontend/node_modules/.bin/vite',
      args: 'preview --host 0.0.0.0 --port 18181 --base ./',
      cwd: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/frontend',
      env: {
        NODE_ENV: 'production'
      },
      max_memory_restart: '300M',
      error_file: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/logs/frontend.err.log',
      out_file: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/logs/frontend.out.log',
      log_file: '/vol1/@apphome/trim.openclaw/data/workspace/ASEANListingAI/logs/frontend.combine.log',
      time: true
    }
  ]
};
