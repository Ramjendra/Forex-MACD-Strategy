# Running Forex MACD Dashboard in Background

This guide explains how to run your Forex MACD Dashboard persistently in the background so it remains available even when you close your laptop or terminal.

## 🌐 Internet Access (Quick Start)

**To make your dashboard accessible from anywhere on the internet:**

```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy

# Install screen (one-time)
sudo apt-get install screen

# Start with internet access
./run_with_internet.sh start

# Get your public URL
./run_with_internet.sh url
```

Your dashboard will be accessible via a public HTTPS URL that you can access from any device, anywhere!

---

## 📋 Table of Contents

1. [Quick Start (Recommended)](#quick-start-recommended)
2. [Method 1: Systemd Service](#method-1-systemd-service-recommended)
3. [Method 2: Screen Session](#method-2-screen-session-simple)
4. [Method 3: Tmux Session](#method-3-tmux-session-alternative)
5. [Method 4: Nohup (Basic)](#method-4-nohup-basic)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start (Recommended)

**Using Screen (Simplest):**
```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
chmod +x run_in_screen.sh
./run_in_screen.sh start
```

**Using Systemd (Most Robust):**
```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
chmod +x start_forex_service.sh
sudo cp forex-macd.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start forex-macd
sudo systemctl enable forex-macd  # Auto-start on boot
```

---

## Method 1: Systemd Service (Recommended)

### ✅ Advantages
- Automatic startup on system boot
- Automatic restart on failure
- Professional service management
- Integrated logging
- Resource management

### 📝 Setup Instructions

1. **Make the startup script executable:**
   ```bash
   chmod +x start_forex_service.sh
   ```

2. **Copy the service file to systemd:**
   ```bash
   sudo cp forex-macd.service /etc/systemd/system/
   ```

3. **Reload systemd to recognize the new service:**
   ```bash
   sudo systemctl daemon-reload
   ```

4. **Start the service:**
   ```bash
   sudo systemctl start forex-macd
   ```

5. **Enable auto-start on boot (optional):**
   ```bash
   sudo systemctl enable forex-macd
   ```

### 🎮 Service Management Commands

```bash
# Start the service
sudo systemctl start forex-macd

# Stop the service
sudo systemctl stop forex-macd

# Restart the service
sudo systemctl restart forex-macd

# Check service status
sudo systemctl status forex-macd

# View logs
sudo journalctl -u forex-macd -f

# Disable auto-start on boot
sudo systemctl disable forex-macd

# Enable auto-start on boot
sudo systemctl enable forex-macd
```

### 📊 Log Files

- Service logs: `logs/service.log`
- Service errors: `logs/service-error.log`
- Strategy logs: `logs/strategy.log`
- Server logs: `logs/server.log`
- Systemd journal: `sudo journalctl -u forex-macd`

---

## Method 2: Screen Session (Simple)

### ✅ Advantages
- Simple and lightweight
- Easy to attach and view output
- No root privileges required
- Easy to understand

### 📝 Setup Instructions

1. **Install screen (if not already installed):**
   ```bash
   sudo apt-get install screen
   ```

2. **Make the script executable:**
   ```bash
   chmod +x run_in_screen.sh
   ```

3. **Start the dashboard:**
   ```bash
   ./run_in_screen.sh start
   ```

### 🎮 Screen Management Commands

```bash
# Start the dashboard
./run_in_screen.sh start

# Stop the dashboard
./run_in_screen.sh stop

# Attach to the running session (view output)
./run_in_screen.sh attach

# Check status
./run_in_screen.sh status

# List all screen sessions
screen -list
```

### 💡 Screen Tips

- When attached to a screen session, press `Ctrl+A` then `D` to detach (without stopping)
- The session continues running in the background after detaching
- You can close your terminal and the session will keep running

---

## Method 3: Tmux Session (Alternative)

### ✅ Advantages
- More features than screen
- Better window management
- Persistent sessions

### 📝 Setup Instructions

1. **Install tmux (if not already installed):**
   ```bash
   sudo apt-get install tmux
   ```

2. **Create a new tmux session:**
   ```bash
   cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
   tmux new-session -d -s forex-macd
   ```

3. **Send commands to the session:**
   ```bash
   # Activate virtual environment and start strategy
   tmux send-keys -t forex-macd "source ../.venv/bin/activate" C-m
   tmux send-keys -t forex-macd "python3 forex_macd_strategy.py &" C-m
   tmux send-keys -t forex-macd "sleep 3" C-m
   tmux send-keys -t forex-macd "python3 serve_forex_macd.py" C-m
   ```

### 🎮 Tmux Management Commands

```bash
# List sessions
tmux list-sessions

# Attach to session
tmux attach-session -t forex-macd

# Kill session
tmux kill-session -t forex-macd

# Detach from session (when attached)
# Press: Ctrl+B then D
```

---

## Method 4: Nohup (Basic)

### ✅ Advantages
- No additional software needed
- Very simple

### ⚠️ Disadvantages
- No easy way to view output
- Manual process management
- No automatic restart

### 📝 Instructions

```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy

# Activate virtual environment
source ../.venv/bin/activate

# Start strategy in background
nohup python3 forex_macd_strategy.py > logs/strategy.log 2>&1 &
echo $! > pids/strategy.pid

# Wait for strategy to initialize
sleep 3

# Start server in background
nohup python3 serve_forex_macd.py > logs/server.log 2>&1 &
echo $! > pids/server.pid

# Check processes
ps aux | grep -E "forex_macd_strategy|serve_forex_macd"
```

### 🛑 Stopping Nohup Processes

```bash
# Kill strategy
kill $(cat pids/strategy.pid)

# Kill server
kill $(cat pids/server.pid)

# Or kill all related processes
pkill -f forex_macd_strategy
pkill -f serve_forex_macd
```

---

## 🌐 Internet Access with Ngrok

Make your dashboard accessible from anywhere on the internet using ngrok tunneling.

### Method A: Screen with Internet Access (Recommended)

**Setup:**
```bash
# Install screen (one-time)
sudo apt-get install screen

# Make script executable
chmod +x run_with_internet.sh

# Start with internet access
./run_with_internet.sh start
```

**Management Commands:**
```bash
# Get public URL
./run_with_internet.sh url

# Check status
./run_with_internet.sh status

# Attach to session
./run_with_internet.sh attach

# Stop all services
./run_with_internet.sh stop
```

### Method B: Direct Start with Internet

**Setup:**
```bash
# Make script executable
chmod +x start_with_internet.sh

# Start all services including ngrok
./start_with_internet.sh start
```

**Management Commands:**
```bash
# Get public URL
./start_with_internet.sh url

# Check status
./start_with_internet.sh status

# Restart services
./start_with_internet.sh restart

# Stop services
./start_with_internet.sh stop
```

### ✅ Benefits of Internet Access

- Access your dashboard from any device, anywhere
- Share the URL with others
- No port forwarding or router configuration needed
- HTTPS encryption by default
- Works even behind firewalls and NAT

### 📱 Accessing Your Dashboard

After starting with internet access:

1. **Get your public URL:**
   ```bash
   ./run_with_internet.sh url
   ```

2. **You'll receive an HTTPS URL like:**
   ```
   https://abc123.ngrok-free.app/forex_macd_dashboard.html
   ```

3. **Access from anywhere:**
   - Open the URL on your phone
   - Share with team members
   - Access from work/home/anywhere

### ⚠️ Important Notes

- The ngrok URL changes each time you restart (free tier)
- For a permanent URL, upgrade to ngrok paid plan
- The dashboard remains accessible even when you close your laptop
- Both local and internet access work simultaneously

---

## 🔧 Troubleshooting

### Dashboard Not Accessible

1. **Check if processes are running:**
   ```bash
   ps aux | grep -E "forex_macd_strategy|serve_forex_macd"
   ```

2. **Check if port 8003 is in use:**
   ```bash
   sudo netstat -tulpn | grep 8003
   # or
   sudo lsof -i :8003
   ```

3. **Check logs for errors:**
   ```bash
   tail -f logs/server.log
   tail -f logs/strategy.log
   ```

### Service Won't Start

1. **Check systemd status:**
   ```bash
   sudo systemctl status forex-macd
   ```

2. **View detailed logs:**
   ```bash
   sudo journalctl -u forex-macd -n 50 --no-pager
   ```

3. **Check file permissions:**
   ```bash
   ls -la start_forex_service.sh
   # Should be executable (x flag)
   ```

### Port Already in Use

1. **Find what's using the port:**
   ```bash
   sudo lsof -i :8003
   ```

2. **Kill the process:**
   ```bash
   sudo kill -9 <PID>
   ```

### Virtual Environment Issues

1. **Verify virtual environment exists:**
   ```bash
   ls -la ../.venv/bin/activate
   ```

2. **Recreate if needed:**
   ```bash
   cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r Forex_MACD_Strategy/requirements.txt
   ```

### Screen Session Issues

1. **List all screen sessions:**
   ```bash
   screen -list
   ```

2. **Force kill a stuck session:**
   ```bash
   screen -S forex-macd -X quit
   ```

3. **Reattach to detached session:**
   ```bash
   screen -r forex-macd
   ```

---

## 📱 Accessing Dashboard

Once running, access your dashboard at:

- **Local:** http://localhost:8003/forex_macd_dashboard.html
- **Network (if ngrok is running):** Your ngrok URL

---

## 🔄 Auto-Start on System Boot

### Systemd (Recommended)
```bash
sudo systemctl enable forex-macd
```

### Cron (Alternative)
Add to crontab:
```bash
crontab -e
```

Add this line:
```
@reboot /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy/start_forex_service.sh start
```

---

## 📞 Support

If you encounter issues:

1. Check the relevant log files
2. Verify all dependencies are installed
3. Ensure the virtual environment is activated
4. Check that no other process is using port 8003
5. Review the troubleshooting section above

---

## 🎯 Recommended Approach

For most users, we recommend:

1. **Development/Testing:** Use Screen method (simple, easy to debug)
2. **Production/Always-On:** Use Systemd method (robust, auto-restart, auto-start on boot)
3. **Quick Testing:** Use Nohup method (no setup required)

Choose the method that best fits your needs!
