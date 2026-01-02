const { execSync, spawn } = require('child_process');

const os = require('os');

const PORT = 3000;

const isWin = os.platform() === 'win32';

console.log(`🧹 [Auto-Clean] Checking port ${PORT}...`);

try {

  if (isWin) {

    // Windows: Find PID and Taskkill

    const stdout = execSync(`netstat -ano | findstr :${PORT}`).toString();

    const lines = stdout.trim().split('\n');

    lines.forEach(line => {

      const parts = line.trim().split(/\s+/);

      const pid = parts[parts.length - 1];

      if (pid && parseInt(pid) > 0) {

        console.log(`💀 Killing zombie PID ${pid}`);

        try { execSync(`taskkill /F /PID ${pid}`); } catch(e) {}

      }

    });

  } else {

    // Unix: lsof

    try {

      const pid = execSync(`lsof -t -i:${PORT}`).toString().trim();

      if (pid) {

        console.log(`💀 Killing zombie PID ${pid}`);

        execSync(`kill -9 ${pid}`);

      }

    } catch(e) {} // lsof returns non-zero if no process found

  }

} catch (e) {

  // Ignore errors if no process was running

}

console.log('🚀 Starting Next.js...');

// IMPORTANT: Use 'npx next dev' to avoid recursive loop

const next = spawn('npx', ['next', 'dev'], {

  stdio: 'inherit',

  shell: true,

  env: { ...process.env } // Pass through env vars

});

next.on('close', (code) => {

  console.log(`Server stopped (code ${code})`);

});
