#!/bin/bash
# Deployment script for AWS Lambda

set -e

echo "=========================================="
echo "DSA Patterns API - AWS Lambda Deployment"
echo "=========================================="
echo ""

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI not found. Installing..."
    pip3 install aws-sam-cli
fi

# Check AWS credentials
echo "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run: aws configure"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-west-1")

echo "✓ AWS Account: $AWS_ACCOUNT"
echo "✓ AWS Region: $AWS_REGION"
echo ""

# Get required values
read -sp "Enter RDS password: " RDS_PASSWORD
echo ""
read -sp "Enter JWT secret key (or press Enter to generate): " JWT_SECRET
echo ""

if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "Generated JWT secret key"
fi

read -sp "Enter default password hash (bcrypt) or press Enter to generate for 'admin123': " PASSWORD_HASH
echo ""

if [ -z "$PASSWORD_HASH" ]; then
    PASSWORD_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode())")
    echo "Generated password hash for 'admin123'"
fi

read -p "Enter CORS origin regex (default: https://.*\.vercel\.app): " CORS_REGEX
CORS_REGEX=${CORS_REGEX:-"https://.*\.vercel\.app"}

echo ""
echo "Building Lambda package..."
sam build --template template-simple.yaml

echo ""
echo "Deploying to AWS Lambda..."
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name dsa-patterns-api \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION \
    --parameter-overrides \
        DatabaseEndpoint=dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com \
        DatabaseName=dsa-patterns \
        DatabaseUsername=postgres \
        DatabasePassword="$RDS_PASSWORD" \
        JWTSecretKey="$JWT_SECRET" \
        DefaultPasswordHash="$PASSWORD_HASH" \
        CORSOriginRegex="$CORS_REGEX" \
    --confirm-changeset

echo ""
echo "=========================================="
echo "✓ Deployment complete!"
echo "=========================================="
echo ""
echo "Getting API Gateway URL..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name dsa-patterns-api \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

echo ""
echo "API Gateway URL: $API_URL"
echo ""
echo "Next steps:"
echo "1. Update your frontend api.js to use: $API_URL"
echo "2. Test the API: curl $API_URL/health"
echo ""

