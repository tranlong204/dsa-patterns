# Quick Deployment Guide - AWS Lambda

## Prerequisites

1. **AWS CLI configured**: `aws configure`
2. **SAM CLI installed**: `pip3 install aws-sam-cli` (or use Homebrew: `brew install aws-sam-cli`)
3. **RDS database ready**: Already set up at `dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com`

## Step 1: Install SAM CLI (if not installed)

```bash
# Option 1: Using pip (in virtual environment)
cd backend
source venv/bin/activate
pip install aws-sam-cli

# Option 2: Using Homebrew
brew install aws-sam-cli

# Verify installation
sam --version
```

## Step 2: Generate Required Values

### Generate JWT Secret Key
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Generate Password Hash (for admin123)
```bash
cd backend
source venv/bin/activate
python3 -c "import bcrypt; print(bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode())"
```

Save these values - you'll need them for deployment.

## Step 3: Build the Lambda Package

```bash
cd backend
sam build --template template-simple.yaml
```

## Step 4: Deploy to AWS

You'll need:
- RDS password (from your .env file)
- JWT secret key (from Step 2)
- Password hash (from Step 2)

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
        JWTSecretKey="YOUR_JWT_SECRET" \
        DefaultPasswordHash="YOUR_PASSWORD_HASH" \
        CORSOriginRegex="https://.*\.vercel\.app" \
    --confirm-changeset
```

Replace:
- `YOUR_RDS_PASSWORD` - Your RDS database password
- `YOUR_JWT_SECRET` - The JWT secret from Step 2
- `YOUR_PASSWORD_HASH` - The bcrypt hash from Step 2

## Step 5: Get API Gateway URL

After deployment completes, get the API URL:

```bash
aws cloudformation describe-stacks \
    --stack-name dsa-patterns-api \
    --region us-west-1 \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text
```

Or check the AWS Console:
1. Go to CloudFormation
2. Select stack `dsa-patterns-api`
3. Go to "Outputs" tab
4. Copy the `ApiUrl` value

## Step 6: Update Frontend

Update `api.js` to use the new API URL:

```javascript
const API_BASE_URL = (function() {
    const stored = localStorage.getItem('API_BASE_URL');
    return stored && stored.trim() !== '' ? stored : 'YOUR_API_GATEWAY_URL';
})();
```

Or set it via URL parameter: `?api=YOUR_API_GATEWAY_URL`

## Step 7: Test the Deployment

```bash
# Test health endpoint
curl https://YOUR_API_GATEWAY_URL/health

# Test login
curl -X POST https://YOUR_API_GATEWAY_URL/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## Troubleshooting

### Lambda can't connect to RDS
- Check RDS security group allows inbound connections on port 5432
- Verify RDS is publicly accessible (for simple setup)
- Check Lambda execution role has VPC permissions (if using VPC)

### Cold Start Issues
- First request may take 2-5 seconds (cold start)
- Subsequent requests should be faster

### CORS Errors
- Update `CORSOriginRegex` parameter to match your frontend domain
- Or set to `.*` for development (not recommended for production)

## Cost

- **Lambda**: 1M requests/month free
- **API Gateway**: 1M requests/month free  
- **RDS**: 750 hours/month free (db.t3.micro)
- **Total**: ~$0/month for first 12 months (new AWS account)

