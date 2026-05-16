#!/bin/bash
# Enhanced Echo Chamber Explorer with LangChain Agents

echo "🚀 Starting Enhanced Echo Chamber Explorer..."
echo "🤖 Activating LangChain environment..."

cd /mnt/c/Users/User
source langchain-env/bin/activate

cd echo-chamber-explorer

echo "📦 Installing additional requirements..."
pip install flask > /dev/null 2>&1

echo "🗄️ Initializing enhanced database..."
python -c "
import sys
sys.path.append('src')
from app_enhanced_simple import init_db
init_db()
print('✅ Database initialized')
"

echo "🌐 Starting enhanced web server..."
echo "📍 Access at: http://localhost:5000"
echo ""

python app_working_enhanced.py
