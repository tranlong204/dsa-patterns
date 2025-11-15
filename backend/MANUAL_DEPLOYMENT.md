# Manual AWS Lambda Deployment Guide

Since your AWS user doesn't have permissions to create Lambda/API Gateway resources, here's a step-by-step guide to deploy manually via AWS Console.

## Prerequisites

1. **IAM Role for Lambda**: You need a Lambda execution role. If you don't have one, ask your AWS admin to create it, or if you have permissions:
   - Go to IAM Console → Roles → Create role
   - Select "AWS service" → "Lambda"
   - Attach policy: `AWSLambdaBasicExecutionRole`
   - Name: `lambda-execution-role`
   - Note the Role ARN (e.g., `arn:aws:iam::494253214513:role/lambda-execution-role`)

2. **Deployment Package**: Already created at `backend/lambda-deployment.zip` (23MB)

## Step 1: Create Lambda Function

1. Go to [AWS Lambda Console](https://us-west-1.console.aws.amazon.com/lambda/home?region=us-west-1)
2. Click "Create function"
3. Choose "Author from scratch"
4. Configure:
   - **Function name**: `dsa-patterns-api`
   - **Runtime**: Python 3.13
   - **Architecture**: x86_64
   - **Execution role**: Use existing role → Select `lambda-execution-role` (or the role ARN you have)
5. Click "Create function"

## Step 2: Upload Code

1. In the Lambda function page, scroll to "Code source"
2. Click "Upload from" → ".zip file"
3. Upload `backend/lambda-deployment.zip`
4. Wait for upload to complete

## Step 3: Configure Environment Variables

1. In Lambda function → Configuration → Environment variables
2. Click "Edit" and add:

```
RDS_HOST = dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com
RDS_PORT = 5432
RDS_DATABASE = dsa-patterns
RDS_USER = postgres
RDS_PASSWORD = Long12345!
JWT_SECRET_KEY = Oc60ycNe0ucMofxxPvH9pT0fXC8-Agd8jKwpnALjEHQ
JWT_ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 43200
DEFAULT_USERNAME = admin
DEFAULT_PASSWORD_HASH = $2b$12$EybwHvjhIltteJ0O47FcWezGycdkgIh0.eKV0t/wjoJjqo2IcnkJq
CORS_ORIGIN_REGEX = https://.*\.vercel\.app
```

3. Click "Save"

## Step 4: Configure Function Settings

1. Go to Configuration → General configuration → Edit
2. Set:
   - **Timeout**: 30 seconds
   - **Memory**: 512 MB
3. Click "Save"

## Step 5: Set Handler

1. Go to Configuration → Runtime settings → Edit
2. Set **Handler**: `lambda_handler.handler`
3. Click "Save"

## Step 6: Create API Gateway

1. Go to [API Gateway Console](https://us-west-1.console.aws.amazon.com/apigateway/home?region=us-west-1)
2. Click "Create API"
3. Choose "REST API" → "Build"
4. Configure:
   - **Protocol**: REST
   - **Create new API**: New API
   - **API name**: `dsa-patterns-api`
   - **Endpoint Type**: Regional
5. Click "Create API"

## Step 7: Configure API Gateway Resources

1. In API Gateway, you should see the root resource `/`
2. Create proxy resource:
   - Click "Actions" → "Create Resource"
   - Check "Configure as proxy resource"
   - Resource name: `{proxy+}`
   - Resource path: `{proxy+}`
   - Click "Create Resource"

3. Create method:
   - Select the `{proxy+}` resource
   - Click "Actions" → "Create Method" → Select "ANY"
   - Integration type: Lambda Function
   - Lambda Region: `us-west-1`
   - Lambda Function: `dsa-patterns-api`
   - Check "Use Lambda Proxy integration"
   - Click "Save" → "OK" (when prompted to give API Gateway permission)

4. Also create ANY method on root `/`:
   - Select root resource `/`
   - Click "Actions" → "Create Method" → Select "ANY"
   - Same settings as above

## Step 8: Enable CORS

1. Select the `{proxy+}` resource
2. Click "Actions" → "Enable CORS"
3. Configure:
   - Access-Control-Allow-Origin: `*` (or your Vercel domain)
   - Access-Control-Allow-Headers: `*`
   - Access-Control-Allow-Methods: `*`
4. Click "Enable CORS and replace existing CORS headers"

## Step 9: Deploy API

1. Click "Actions" → "Deploy API"
2. Configure:
   - **Deployment stage**: `[New Stage]`
   - **Stage name**: `prod`
   - **Stage description**: Production
3. Click "Deploy"

## Step 10: Get API URL

After deployment, you'll see:
- **Invoke URL**: `https://YOUR_API_ID.execute-api.us-west-1.amazonaws.com/prod`

Copy this URL - this is your API Gateway endpoint!

## Step 11: Test the API

```bash
# Test health endpoint
curl https://YOUR_API_ID.execute-api.us-west-1.amazonaws.com/prod/health

# Test login
curl -X POST https://YOUR_API_ID.execute-api.us-west-1.amazonaws.com/prod/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## Step 12: Update Frontend

Update `api.js`:

```javascript
const API_BASE_URL = 'https://YOUR_API_ID.execute-api.us-west-1.amazonaws.com/prod';
```

Or set via URL parameter: `?api=https://YOUR_API_ID.execute-api.us-west-1.amazonaws.com/prod`

## Troubleshooting

### Lambda can't connect to RDS
- Check RDS security group allows inbound from Lambda (or 0.0.0.0/0 for public RDS)
- Verify RDS is publicly accessible
- Check Lambda VPC configuration if RDS is in a VPC

### CORS errors
- Make sure CORS is enabled in API Gateway
- Check `CORS_ORIGIN_REGEX` environment variable matches your frontend domain

### Cold start
- First request may take 2-5 seconds
- Subsequent requests should be faster

## Required IAM Permissions

If you need to request permissions from your AWS admin, you need:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:GetFunction",
        "lambda:AddPermission"
      ],
      "Resource": "arn:aws:lambda:us-west-1:494253214513:function:dsa-patterns-api"
    },
    {
      "Effect": "Allow",
      "Action": [
        "apigateway:*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:GetRole"
      ],
      "Resource": "arn:aws:iam::494253214513:role/lambda-execution-role"
    }
  ]
}
```

