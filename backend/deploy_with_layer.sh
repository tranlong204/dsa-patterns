#!/bin/bash
# Deploy using AWS CLI (assumes psycopg2 will come from Lambda Layer)

set -e

echo "=========================================="
echo "Deploying to AWS Lambda"
echo "=========================================="

cd "$(dirname "$0")"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run: aws configure"
    exit 1
fi

AWS_REGION=${AWS_REGION:-us-west-1}
FUNCTION_NAME="dsa-patterns-api"

echo "Region: $AWS_REGION"
echo "Function: $FUNCTION_NAME"
echo ""

# Create deployment package (code only, dependencies from layer)
echo "Creating deployment package..."
rm -rf lambda-package lambda-deployment.zip
mkdir -p lambda-package

# Copy application code
cp -r app lambda-package/
cp lambda_handler.py lambda-package/

# Create zip
cd lambda-package
zip -r ../lambda-deployment.zip . > /dev/null
cd ..

echo "✓ Package created: lambda-deployment.zip"
echo ""

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION &> /dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --region $AWS_REGION \
        --zip-file fileb://lambda-deployment.zip \
        --output json | jq -r '.FunctionArn'
else
    echo "Creating new function..."
    # Create function (will need to add layer and env vars separately)
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --region $AWS_REGION \
        --runtime python3.13 \
        --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
        --handler lambda_handler.handler \
        --zip-file fileb://lambda-deployment.zip \
        --timeout 30 \
        --memory-size 512 \
        --output json | jq -r '.FunctionArn'
    
    echo ""
    echo "⚠️  Note: You need to:"
    echo "1. Add psycopg2 Lambda Layer"
    echo "2. Set environment variables"
    echo "3. Create API Gateway"
fi

echo ""
echo "Next steps:"
echo "1. Add psycopg2 layer to the function"
echo "2. Set environment variables (see DEPLOY_SIMPLE.md)"
echo "3. Create API Gateway endpoint"

