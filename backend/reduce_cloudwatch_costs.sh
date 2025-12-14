#!/bin/bash
# Script to reduce CloudWatch costs

set -e

FUNCTION_NAME="dsa-patterns-api"
REGION="us-west-1"

echo "=========================================="
echo "Reducing CloudWatch Costs"
echo "=========================================="
echo ""

# Get Lambda function name
LOG_GROUP_NAME="/aws/lambda/$FUNCTION_NAME"

echo "Checking CloudWatch log group: $LOG_GROUP_NAME"

# Check if log group exists
if aws logs describe-log-groups \
    --log-group-name-prefix $LOG_GROUP_NAME \
    --region $REGION \
    --query "logGroups[?logGroupName=='$LOG_GROUP_NAME']" \
    --output json | jq -e '. | length > 0' > /dev/null 2>&1; then
    
    echo "Log group exists. Setting retention to 1 day (minimum)..."
    
    # Set retention to 1 day (minimum, reduces storage costs)
    aws logs put-retention-policy \
        --log-group-name $LOG_GROUP_NAME \
        --retention-in-days 1 \
        --region $REGION
    
    echo "✅ Log retention set to 1 day"
    echo ""
    echo "Note: CloudWatch free tier includes:"
    echo "  - 5GB log ingestion per month"
    echo "  - 5GB log storage per month"
    echo "  - 10 custom metrics per month"
    echo ""
    echo "If you want to completely disable logging, you can delete the log group:"
    echo "  aws logs delete-log-group --log-group-name $LOG_GROUP_NAME --region $REGION"
    echo ""
    echo "However, this will make debugging harder. 1 day retention is recommended."
else
    echo "Log group does not exist yet. It will be created automatically when Lambda runs."
    echo "You can set retention policy after first Lambda invocation."
fi

