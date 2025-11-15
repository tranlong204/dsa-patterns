#!/bin/bash
# Prepare deployment package for AWS Lambda

set -e

echo "Preparing Lambda deployment package..."

cd "$(dirname "$0")"

# Create deployment directory
rm -rf lambda-package
mkdir -p lambda-package

# Copy application code
echo "Copying application code..."
cp -r app lambda-package/
cp lambda_handler.py lambda-package/
cp -r __pycache__ lambda-package/ 2>/dev/null || true

# Install dependencies for Linux (requires Docker)
echo ""
echo "To build for Lambda, you need to install dependencies for Linux x86_64."
echo "Options:"
echo "1. Use Docker (recommended):"
echo "   docker run --rm -v \$(pwd):/var/task public.ecr.aws/sam/build-python3.13:latest pip install -r requirements.txt -t lambda-package/"
echo ""
echo "2. Use AWS Lambda Layers (easier):"
echo "   - Use pre-built psycopg2 layer from: https://github.com/jetbridge/psycopg2-lambda-layer"
echo ""
echo "3. Build manually on Linux EC2 instance"
echo ""

# For now, create a requirements file
echo "Creating deployment package structure..."
echo "Note: Dependencies need to be installed for Linux x86_64 architecture"

# Create a .zip file structure info
cat > lambda-package/README.txt << EOF
Lambda Deployment Package

To complete the package:
1. Install dependencies for Linux x86_64:
   docker run --rm -v \$(pwd):/var/task public.ecr.aws/sam/build-python3.13:latest pip install -r requirements.txt -t lambda-package/

2. Or use AWS Lambda Layers for psycopg2-binary

3. Zip the package:
   cd lambda-package && zip -r ../lambda-deployment.zip .
EOF

echo "✓ Package structure created in lambda-package/"
echo ""
echo "Next: Install dependencies for Linux, then zip and upload to Lambda"

