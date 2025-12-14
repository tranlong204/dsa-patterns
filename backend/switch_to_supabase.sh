#!/bin/bash
# Script to switch Lambda from RDS to Supabase

set -e

FUNCTION_NAME="dsa-patterns-api"
REGION="us-west-1"

echo "=========================================="
echo "Switching Lambda to Supabase"
echo "=========================================="
echo ""

# Check if Supabase credentials are provided
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "Please provide Supabase credentials:"
    read -p "SUPABASE_URL: " SUPABASE_URL
    read -sp "SUPABASE_KEY: " SUPABASE_KEY
    echo ""
fi

echo "Updating Lambda environment variables..."

# Get current environment variables
CURRENT_ENV=$(aws lambda get-function-configuration \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Environment.Variables' \
    --output json)

# Keep non-RDS variables
JWT_SECRET_KEY=$(echo $CURRENT_ENV | jq -r '.JWT_SECRET_KEY')
JWT_ALGORITHM=$(echo $CURRENT_ENV | jq -r '.JWT_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES=$(echo $CURRENT_ENV | jq -r '.ACCESS_TOKEN_EXPIRE_MINUTES')
DEFAULT_USERNAME=$(echo $CURRENT_ENV | jq -r '.DEFAULT_USERNAME')
DEFAULT_PASSWORD_HASH=$(echo $CURRENT_ENV | jq -r '.DEFAULT_PASSWORD_HASH')
CORS_ORIGIN_REGEX=$(echo $CURRENT_ENV | jq -r '.CORS_ORIGIN_REGEX')

# Update Lambda environment variables
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --environment "Variables={
        SUPABASE_URL=$SUPABASE_URL,
        SUPABASE_KEY=$SUPABASE_KEY,
        JWT_SECRET_KEY=$JWT_SECRET_KEY,
        JWT_ALGORITHM=$JWT_ALGORITHM,
        ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES,
        DEFAULT_USERNAME=$DEFAULT_USERNAME,
        DEFAULT_PASSWORD_HASH=$DEFAULT_PASSWORD_HASH,
        CORS_ORIGIN_REGEX=$CORS_ORIGIN_REGEX
    }" \
    --output json > /dev/null

echo "✅ Lambda environment variables updated"
echo ""
echo "Removed RDS variables:"
echo "  - RDS_HOST"
echo "  - RDS_PORT"
echo "  - RDS_DATABASE"
echo "  - RDS_USER"
echo "  - RDS_PASSWORD"
echo ""
echo "Added Supabase variables:"
echo "  - SUPABASE_URL"
echo "  - SUPABASE_KEY"
echo ""
echo "Lambda will now use Supabase instead of RDS."

