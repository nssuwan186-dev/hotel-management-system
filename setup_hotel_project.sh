#!/bin/bash
# Quick Setup Script for Hotel Management Project

echo "🏨 HOTEL MANAGEMENT PROJECT - AI INTEGRATION"
echo "============================================="

# Step 1: Clone project
echo "📥 Step 1: Cloning project..."
cd /root/ai_projects
git clone https://github.com/nssuwan186-dev/hotel-management.git
cd hotel-management

# Step 2: Analyze project structure
echo "🔍 Step 2: Analyzing project structure..."
ls -la
echo ""
echo "📦 Package.json contents:"
cat package.json | head -20

# Step 3: Setup AI development environment
echo ""
echo "🤖 Step 3: Setting up AI environment..."
source /root/ai_env/bin/activate

# Step 4: Install dependencies
echo "📚 Step 4: Installing dependencies..."
npm install

# Step 5: Create AI-enhanced components
echo "🚀 Step 5: Ready for AI-enhanced development!"
echo ""
echo "💡 Next steps:"
echo "1. ai code 'analyze existing hotel management code structure'"
echo "2. ai code 'create React hotel booking form with date picker'"
echo "3. ai code 'create Express.js room management API'"
echo "4. ai code 'create customer registration form'"
echo "5. ai code 'create admin dashboard with charts'"
echo ""
echo "✅ Project ready for AI-powered development!"
