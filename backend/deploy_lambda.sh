#!/bin/bash
# Complete Lambda deployment script

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "AWS Lambda Deployment"
echo "=========================================="
echo ""

# Check prerequisites
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run: aws configure"
    exit 1
fi

AWS_REGION=${AWS_REGION:-us-west-1}
FUNCTION_NAME="dsa-patterns-api"
STACK_NAME="dsa-patterns-api"

echo "Region: $AWS_REGION"
echo "Function: $FUNCTION_NAME"
echo ""

# Get required values
read -sp "Enter RDS password: " RDS_PASSWORD
echo ""
read -p "Enter JWT secret key [Oc60ycNe0ucMofxxPvH9pT0fXC8-Agd8jKwpnALjEHQ]: " JWT_SECRET
JWT_SECRET=${JWT_SECRET:-Oc60ycNe0ucMofxxPvH9pT0fXC8-Agd8jKwpnALjEHQ}

read -p "Enter password hash [$2b$12$EybwHvjhIltteJ0O47FcWezGycdkgIh0.eKV0t/wjoJjqo2IcnkJq]: " PASSWORD_HASH
PASSWORD_HASH=${PASSWORD_HASH:-$2b$12$EybwHvjhIltteJ0O47FcWezGycdkgIh0.eKV0t/wjoJjqo2IcnkJq}

read -p "Enter CORS origin regex [https://.*\.vercel\.app]: " CORS_REGEX
CORS_REGEX=${CORS_REGEX:-"https://.*\.vercel\.app"}

echo ""
echo "Building deployment package..."

# Clean up
rm -rf lambda-package lambda-deployment.zip
mkdir -p lambda-package

# Copy code
cp -r app lambda-package/
cp lambda_handler.py lambda-package/

# Install dependencies using Docker (for Linux)
echo "Installing dependencies for Linux..."
docker run --rm -v "$(pwd)":/var/task public.ecr.aws/sam/build-python3.13:latest \
    pip install -r requirements.txt -t lambda-package/ --quiet

# Create zip
echo "Creating deployment package..."
cd lambda-package
zip -r ../lambda-deployment.zip . > /dev/null
cd ..
PACKAGE_SIZE=$(ls -lh lambda-deployment.zip | awk '{print $5}')
echo "✓ Package created: lambda-deployment.zip ($PACKAGE_SIZE)"
echo ""

# Check if IAM role exists (needed for Lambda)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="lambda-execution-role"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

# Try to get or create the role
if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
    echo "✓ Using existing IAM role: $ROLE_ARN"
elif aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
    --output json &> /dev/null; then
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole &> /dev/null || true
    echo "✓ IAM role created: $ROLE_ARN"
else
    echo "⚠️  Cannot create IAM role (insufficient permissions)"
    echo "Please provide an existing Lambda execution role ARN, or create one manually:"
    echo "  - Go to IAM Console → Roles → Create role"
    echo "  - Select 'AWS service' → 'Lambda'"
    echo "  - Attach 'AWSLambdaBasicExecutionRole' policy"
    echo "  - Name it 'lambda-execution-role'"
    echo ""
    read -p "Enter existing Lambda role ARN (or press Enter to try default): " CUSTOM_ROLE_ARN
    if [ ! -z "$CUSTOM_ROLE_ARN" ]; then
        ROLE_ARN="$CUSTOM_ROLE_ARN"
    else
        echo "Using default role ARN: $ROLE_ARN"
        echo "If this fails, you'll need to create the role manually."
    fi
fi

# Deploy Lambda function
if aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION &> /dev/null; then
    echo "Updating Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --region $AWS_REGION \
        --zip-file fileb://lambda-deployment.zip \
        --output json > /dev/null
    
    echo "Updating environment variables..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --region $AWS_REGION \
        --environment "Variables={
            RDS_HOST=dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com,
            RDS_PORT=5432,
            RDS_DATABASE=dsa-patterns,
            RDS_USER=postgres,
            RDS_PASSWORD=${RDS_PASSWORD},
            JWT_SECRET_KEY=${JWT_SECRET},
            JWT_ALGORITHM=HS256,
            ACCESS_TOKEN_EXPIRE_MINUTES=43200,
            DEFAULT_USERNAME=admin,
            DEFAULT_PASSWORD_HASH=${PASSWORD_HASH},
            CORS_ORIGIN_REGEX=${CORS_REGEX}
        }" \
        --timeout 30 \
        --memory-size 512 \
        --output json > /dev/null
    
    FUNCTION_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION --query 'Configuration.FunctionArn' --output text)
else
    echo "Creating Lambda function..."
    FUNCTION_ARN=$(aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --region $AWS_REGION \
        --runtime python3.13 \
        --role $ROLE_ARN \
        --handler lambda_handler.handler \
        --zip-file fileb://lambda-deployment.zip \
        --timeout 30 \
        --memory-size 512 \
        --environment "Variables={
            RDS_HOST=dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com,
            RDS_PORT=5432,
            RDS_DATABASE=dsa-patterns,
            RDS_USER=postgres,
            RDS_PASSWORD=${RDS_PASSWORD},
            JWT_SECRET_KEY=${JWT_SECRET},
            JWT_ALGORITHM=HS256,
            ACCESS_TOKEN_EXPIRE_MINUTES=43200,
            DEFAULT_USERNAME=admin,
            DEFAULT_PASSWORD_HASH=${PASSWORD_HASH},
            CORS_ORIGIN_REGEX=${CORS_REGEX}
        }" \
        --output json | jq -r '.FunctionArn')
    
    echo "✓ Lambda function created"
fi

echo "✓ Lambda function ready: $FUNCTION_ARN"
echo ""

# Create or update API Gateway
echo "Setting up API Gateway..."

# Check if API exists
API_ID=$(aws apigateway get-rest-apis --region $AWS_REGION --query "items[?name=='dsa-patterns-api'].id" --output text 2>/dev/null || echo "")

if [ -z "$API_ID" ]; then
    echo "Creating API Gateway..."
    API_ID=$(aws apigateway create-rest-api \
        --name dsa-patterns-api \
        --region $AWS_REGION \
        --endpoint-configuration types=REGIONAL \
        --output json | jq -r '.id')
    
    # Get root resource
    ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $AWS_REGION --query 'items[?path==`/`].id' --output text)
    
    # Create proxy resource
    PROXY_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --region $AWS_REGION \
        --parent-id $ROOT_ID \
        --path-part '{proxy+}' \
        --output json | jq -r '.id')
    
    # Create ANY method
    aws apigateway put-method \
        --rest-api-id $API_ID \
        --region $AWS_REGION \
        --resource-id $PROXY_ID \
        --http-method ANY \
        --authorization-type NONE \
        --output json > /dev/null
    
    # Set up integration
    aws apigateway put-integration \
        --rest-api-id $API_ID \
        --region $AWS_REGION \
        --resource-id $PROXY_ID \
        --http-method ANY \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${FUNCTION_ARN}/invocations" \
        --output json > /dev/null
    
    # Create root ANY method too
    aws apigateway put-method \
        --rest-api-id $API_ID \
        --region $AWS_REGION \
        --resource-id $ROOT_ID \
        --http-method ANY \
        --authorization-type NONE \
        --output json > /dev/null
    
    aws apigateway put-integration \
        --rest-api-id $API_ID \
        --region $AWS_REGION \
        --resource-id $ROOT_ID \
        --http-method ANY \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${FUNCTION_ARN}/invocations" \
        --output json > /dev/null
    
    # Grant API Gateway permission to invoke Lambda
    aws lambda add-permission \
        --function-name $FUNCTION_NAME \
        --region $AWS_REGION \
        --statement-id apigateway-invoke \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn "arn:aws:execute-api:${AWS_REGION}:${ACCOUNT_ID}:${API_ID}/*/*" \
        --output json > /dev/null
    
    # Deploy API
    aws apigateway create-deployment \
        --rest-api-id $API_ID \
        --region $AWS_REGION \
        --stage-name prod \
        --output json > /dev/null
    
    echo "✓ API Gateway created"
else
    echo "API Gateway already exists, updating..."
    # Update integration if needed
    ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $AWS_REGION --query 'items[?path==`/`].id' --output text)
    PROXY_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $AWS_REGION --query 'items[?path==`/{proxy+}`].id' --output text)
    
    if [ ! -z "$PROXY_ID" ]; then
        aws apigateway put-integration \
            --rest-api-id $API_ID \
            --region $AWS_REGION \
            --resource-id $PROXY_ID \
            --http-method ANY \
            --type AWS_PROXY \
            --integration-http-method POST \
            --uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${FUNCTION_ARN}/invocations" \
            --output json > /dev/null
    fi
    
    # Redeploy
    aws apigateway create-deployment \
        --rest-api-id $API_ID \
        --region $AWS_REGION \
        --stage-name prod \
        --output json > /dev/null
fi

API_URL="https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com/prod"

echo ""
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "API Gateway URL: $API_URL"
echo ""
echo "Test the API:"
echo "  curl $API_URL/health"
echo ""
echo "Update your frontend api.js with:"
echo "  const API_BASE_URL = '$API_URL';"
echo ""

