#!/bin/bash
set -e

echo "🚀 Deploying Events API to AWS..."

# Check if AWS credentials are set via environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ AWS credentials not found in environment variables."
    echo "Please export the following:"
    echo "  export AWS_ACCESS_KEY_ID=your_access_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "  export AWS_REGION=us-east-1  # optional, defaults to us-east-1"
    exit 1
fi

echo "✓ Using AWS credentials from environment variables"

# Install infrastructure dependencies
echo "📦 Installing CDK dependencies..."
cd infrastructure
pip install -r requirements.txt

# Bootstrap CDK (only needed once per account/region)
echo "🔧 Bootstrapping CDK (if needed)..."
npx aws-cdk bootstrap || true

# Deploy the stack
echo "☁️  Deploying stack..."
npx aws-cdk deploy --require-approval never

echo "✅ Deployment complete!"
echo ""
echo "Your API is now live. Check the outputs above for the API URL."
