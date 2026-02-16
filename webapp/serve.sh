#!/bin/bash
cd "$(dirname "$0")"
echo "🏰 Forge Creator running at http://localhost:8888"
python3 -m http.server 8888
