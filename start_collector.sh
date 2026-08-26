#!/bin/bash

# 1. Activate the virtual environment
echo "🟢 Activating virtual environment..."
source venv/bin/activate

# 2. Navigate to the data collector folder
cd data_collector || exit

# 3. Find and display the local IP address (works on macOS)
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

echo "🚀 Data Collector is live!"
echo "📱 On your tablet, go to: http://$LOCAL_IP:8000"
echo "💻 On this computer, go to: http://localhost:8000"
echo "🛑 Press Ctrl+C to stop the server."

# 4. Start the server
python3 -m http.server 8000