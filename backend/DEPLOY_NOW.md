# Quick Deploy to AWS Lambda

## Pre-deployment Checklist

✅ RDS Database: `dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com`  
✅ Database Name: `dsa-patterns`  
✅ Database User: `postgres`  
✅ Data Migrated: 1,432 problems + user data

## Required Values

You'll need these values for deployment:

1. **RDS Password**: (from your .env file)
2. **JWT Secret**: `Oc60ycNe0ucMofxxPvH9pT0fXC8-Agd8jKwpnALjEHQ`
3. **Password Hash**: `$2b$12$EybwHvjhIltteJ0O47FcWezGycdkgIh0.eKV0t/wjoJjqo2IcnkJq`

## Deployment Steps

### Step 1: Build (if Docker is available)

```bash
cd backend
source venv/bin/activate
sam build --template template-simple.yaml --use-container
```

### Step 2: Build (without Docker - alternative)

If Docker isn't available, we'll need to use Python 3.13 on x86_64. You can:
- Use AWS Cloud9
- Use GitHub Actions
- Or deploy manually via AWS Console

### Step 3: Deploy

```bash
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name dsa-patterns-api \
    --capabilities CAPABILITY_IAM \
    --region us-west-1 \
    --parameter-overrides \
        DatabaseEndpoint=dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com \
        DatabaseName=dsa-patterns \
        DatabaseUsername=postgres \
        DatabasePassword="YOUR_RDS_PASSWORD" \
        JWTSecretKey="Oc60ycNe0ucMofxxPvH9pT0fXC8-Agd8jKwpnALjEHQ" \
        DefaultPasswordHash="$2b$12$EybwHvjhIltteJ0O47FcWezGycdkgIh0.eKV0t/wjoJjqo2IcnkJq" \
        CORSOriginRegex="https://.*\.vercel\.app" \
    --confirm-changeset
```

Replace `YOUR_RDS_PASSWORD` with your actual RDS password.

## Alternative: Manual Deployment via AWS Console

If SAM build fails, you can deploy manually:

1. **Create Lambda Function**:
   - Go to AWS Lambda Console
   - Create function: `dsa-patterns-api`
   - Runtime: Python 3.13
   - Architecture: x86_64

2. **Upload Code**:
   - Package all files from `backend/` directory
   - Create a zip file with all dependencies
   - Upload to Lambda

3. **Set Environment Variables**:
   - RDS_HOST: `dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com`
   - RDS_PORT: `5432`
   - RDS_DATABASE: `dsa-patterns`
   - RDS_USER: `postgres`
   - RDS_PASSWORD: (your password)
   - JWT_SECRET_KEY: `Oc60ycNe0ucMofxxPvH9pT0fXC8-Agd8jKwpnALjEHQ`
   - JWT_ALGORITHM: `HS256`
   - ACCESS_TOKEN_EXPIRE_MINUTES: `43200`
   - DEFAULT_USERNAME: `admin`
   - DEFAULT_PASSWORD_HASH: `$2b$12$EybwHvjhIltteJ0O47FcWezGycdkgIh0.eKV0t/wjoJjqo2IcnkJq`
   - CORS_ORIGIN_REGEX: `https://.*\.vercel\.app`

4. **Set Handler**: `lambda_handler.handler`

5. **Create API Gateway**:
   - Create REST API
   - Create resource: `{proxy+}`
   - Create method: ANY
   - Integration type: Lambda Function
   - Select your Lambda function
   - Enable CORS

## After Deployment

Get your API URL and update the frontend:

```bash
aws cloudformation describe-stacks \
    --stack-name dsa-patterns-api \
    --region us-west-1 \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text
```

Then update `api.js` with the new URL.

