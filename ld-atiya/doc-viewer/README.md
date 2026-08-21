# Documentation Viewer

A simple web application to view HTML documentation files with authentication.

## Features

- User authentication (username: dpandit, password: dpandit)
- Folder-based organization of documentation
- Clean, modern UI
- View HTML files directly in the browser

## Setup

1. Install dependencies:
```bash
/home/test/reg/bin/python -m pip install -r requirements.txt
```

2. Start the server (runs in background):
```bash
./start.sh
```

3. Check server status:
```bash
./status.sh
```

4. Stop the server:
```bash
./stop.sh
```

5. Open your browser and navigate to:
```
http://127.0.0.1:5000           (from local machine)
http://10.2.182.163:5000        (from other machines on network)
http://192.168.100.5:5000       (internal IP)
```

6. Login with:
   - Username: `dpandit`
   - Password: `dpandit`

## Server Management

- **Start:** `./start.sh` - Starts server in background, creates PID file
- **Stop:** `./stop.sh` - Gracefully stops the server
- **Status:** `./status.sh` - Check if server is running
- **Logs:** View `server.log` for application logs

## Directory Structure

The application serves HTML files from:
```
/home/test/reg/agent-dp/ld-atiya/learn-and-build/learning-docs/all-topics
```

Files are organized by topic folders, and each topic can contain multiple HTML files.

## Security

- The application only runs on localhost (127.0.0.1)
- Basic session-based authentication
- Path traversal protection to prevent unauthorized file access
