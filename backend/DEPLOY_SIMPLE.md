# Simple AWS Lambda Deployment Guide

Since building `psycopg2-binary` for Lambda requires Linux, here are the easiest deployment options:

## Option 1: Use AWS Lambda Layers (Recommended - Easiest)

### Step 1: Use Pre-built psycopg2 Layer

1. Go to AWS Lambda Console → Layers
2. Create a new layer using this ARN (for us-east-1):
   ```
   arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py39:1
   ```
   Or find a compatible layer for your region at: https://github.com/jetbridge/psycopg2-lambda-layer

### Step 2: Create Lambda Function

1. Go to AWS Lambda Console
2. Create function:
   - **Function name**: `dsa-patterns-api`
   - **Runtime**: Python 3.13
   - **Architecture**: x86_64
   - **Handler**: `lambda_handler.handler`

### Step 3: Upload Code

1. Install dependencies locally (without psycopg2):
   ```bash
   cd backend
   pip install -r requirements.txt --target package/ --platform manylinux2014_x86_64 --only-binary=:all: --no-deps
   # Then manually add psycopg2 from layer
   ```

2. Or use this simpler approach:
   - Create a zip with just your code (no dependencies)
   - Add the psycopg2 layer to your function
   - Install other dependencies using Lambda Layers or package them

### Step 4: Add Lambda Layer

In Lambda function → Layers → Add a layer:
- Choose "Specify an ARN"
- Enter the psycopg2 layer ARN for your region

### Step 5: Set Environment Variables

Add these environment variables in Lambda:

```
RDS_HOST=dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=dsa-patterns
RDS_USER=postgres
RDS_PASSWORD=your_rds_password
JWT_SECRET_KEY=Oc60ycNe0ucMofxxPvH9pT0fXC8-Agd8jKwpnALjEHQ
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
DEFAULT_USERNAME=admin
DEFAULT_PASSWORD_HASH=$2b$12$EybwHvjhIltteJ0O47FcWezGycdkgIh0.eKV0t/wjoJjqo2IcnkJq
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
```

### Step 6: Create API Gateway

1. Go to API Gateway Console
2. Create REST API
3. Create resource: `{proxy+}`
4. Create method: `ANY`
5. Integration: Lambda Function → `dsa-patterns-api`
6. Enable CORS
7. Deploy API (stage: `prod`)

## Option 2: Use Docker to Build (If Docker Available)

```bash
cd backend

# Build dependencies in Docker
docker run --rm -v $(pwd):/var/task public.ecr.aws/sam/build-python3.13:latest \
  pip install -r requirements.txt -t lambda-package/

# Copy your code
cp -r app lambda-package/
cp lambda_handler.py lambda-package/

# Create zip
cd lambda-package
zip -r ../lambda-deployment.zip .
```

Then upload `lambda-deployment.zip` to Lambda.

## Option 3: Use GitHub Actions (CI/CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Lambda

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt -t package/
      - name: Package
        run: |
          cd backend
          cp -r app package/
          cp lambda_handler.py package/
          cd package
          zip -r ../lambda-deployment.zip .
      - name: Deploy to Lambda
        uses: appleboy/lambda-action@master
        with:
          function_name: dsa-patterns-api
          zip_file: backend/lambda-deployment.zip
          region: us-west-1
          access_key_id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          secret_access_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Quick Test After Deployment

```bash
# Test health endpoint
curl https://YOUR_API_GATEWAY_URL/health

# Test login
curl -X POST https://YOUR_API_GATEWAY_URL/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## Update Frontend

After getting your API Gateway URL, update `api.js`:

```javascript
const API_BASE_URL = 'https://YOUR_API_ID.execute-api.us-west-1.amazonaws.com/prod';
```

Or set via URL: `?api=https://YOUR_API_ID.execute-api.us-west-1.amazonaws.com/prod`

