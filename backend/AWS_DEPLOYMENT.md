# AWS Lambda + API Gateway + RDS Deployment Guide

This guide will help you deploy the DSA Patterns backend to AWS using Lambda, API Gateway, and RDS PostgreSQL.

## Prerequisites

1. AWS Account (free tier eligible)
2. AWS CLI installed and configured
3. SAM CLI installed (`pip install aws-sam-cli`)
4. Python 3.13

## Step 1: Create RDS PostgreSQL Database

### Option A: Using AWS Console (Recommended for Free Tier)

1. Go to AWS RDS Console
2. Click "Create database"
3. Choose:
   - **Engine**: PostgreSQL
   - **Version**: 15.4 (or latest)
   - **Template**: Free tier
   - **Instance class**: db.t3.micro
   - **Storage**: 20 GB (free tier)
   - **Database name**: `dsapatterns`
   - **Master username**: `admin` (or your choice)
   - **Master password**: Create a strong password
4. **Important for Free Tier**: Set "Publicly accessible" to **Yes** (for simplicity)
5. Create database
6. Note the **Endpoint** and **Port** from the database details

### Option B: Using AWS CLI

```bash
aws rds create-db-instance \
  --db-instance-identifier dsapatterns-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20 \
  --publicly-accessible \
  --backup-retention-period 7
```

## Step 2: Set Up Database Schema

1. Connect to your RDS database using a PostgreSQL client (pgAdmin, DBeaver, or psql)
2. Run the SQL from `supabase_migration.sql` to create tables
3. Verify tables are created:
   ```sql
   SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
   ```

## Step 3: Migrate Data from Supabase

1. Set up environment variables in a `.env` file:
   ```env
   # Supabase (source)
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   
   # RDS (destination)
   RDS_HOST=your-rds-endpoint.region.rds.amazonaws.com
   RDS_PORT=5432
   RDS_DATABASE=dsapatterns
   RDS_USER=admin
   RDS_PASSWORD=your_rds_password
   ```

2. Run migration script:
   ```bash
   cd backend
   python migrate_to_rds.py
   ```

## Step 4: Prepare for Lambda Deployment

1. Generate bcrypt hash for default password:
   ```python
   import bcrypt
   password = "admin123"  # or your password
   hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
   print(hashed)
   ```

2. Get your JWT secret key (or generate a new one)

## Step 5: Deploy with SAM

### Option A: Simplified Deployment (Public RDS)

For free tier with public RDS, use this simplified approach:

1. Create `template-simple.yaml` (see below)
2. Build and deploy:
   ```bash
   cd backend
   sam build
   sam deploy --guided
   ```

### Option B: Full VPC Deployment

If you want RDS in a private subnet (more secure):

1. Use the provided `template.yaml`
2. Build and deploy:
   ```bash
   cd backend
   sam build
   sam deploy --guided
   ```

During `sam deploy --guided`, you'll be prompted for:
- Stack name: `dsa-patterns-api`
- AWS Region: Choose your region (e.g., `us-east-1`)
- DatabasePassword: Your RDS password
- JWTSecretKey: Your JWT secret
- DefaultPasswordHash: Bcrypt hash from Step 4
- CORSOriginRegex: `https://.*\.vercel\.app` (or your frontend domain)

## Step 6: Update Frontend API URL

After deployment, SAM will output the API Gateway URL. Update your frontend:

1. In `api.js`, update the default `API_BASE_URL`:
   ```javascript
   const API_BASE_URL = 'https://your-api-id.execute-api.region.amazonaws.com/prod';
   ```

2. Or set it via URL parameter: `?api=https://your-api-id.execute-api.region.amazonaws.com/prod`

## Step 7: Test the Deployment

1. Test health endpoint:
   ```bash
   curl https://your-api-id.execute-api.region.amazonaws.com/prod/health
   ```

2. Test login:
   ```bash
   curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```

## Simplified Template (Public RDS)

Create `template-simple.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: DSA Patterns API - Simplified for Public RDS

Parameters:
  DatabaseEndpoint:
    Type: String
    Description: RDS endpoint (e.g., dsapatterns-db.xxxxx.rds.amazonaws.com)
  DatabaseName:
    Type: String
    Default: dsapatterns
  DatabaseUsername:
    Type: String
    Default: admin
  DatabasePassword:
    Type: String
    NoEcho: true
  JWTSecretKey:
    Type: String
    NoEcho: true
  DefaultPasswordHash:
    Type: String
    NoEcho: true
  CORSOriginRegex:
    Type: String
    Default: 'https://.*\.vercel\.app'

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.13
    Environment:
      Variables:
        RDS_HOST: !Ref DatabaseEndpoint
        RDS_PORT: '5432'
        RDS_DATABASE: !Ref DatabaseName
        RDS_USER: !Ref DatabaseUsername
        RDS_PASSWORD: !Ref DatabasePassword
        JWT_SECRET_KEY: !Ref JWTSecretKey
        JWT_ALGORITHM: HS256
        ACCESS_TOKEN_EXPIRE_MINUTES: '43200'
        DEFAULT_USERNAME: admin
        DEFAULT_PASSWORD_HASH: !Ref DefaultPasswordHash
        CORS_ORIGIN_REGEX: !Ref CORSOriginRegex

Resources:
  DSAPatternsAPI:
    Type: AWS::Serverless::Function
    Properties:
      Handler: lambda_handler.handler
      CodeUri: .
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

  DSAAPI:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Cors:
        AllowMethods: "'*'"
        AllowHeaders: "'*'"
        AllowOrigin: "'*'"
        MaxAge: "'600'"

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${DSAAPI}.execute-api.${AWS::Region}.amazonaws.com/prod/'
```

## Troubleshooting

### Lambda can't connect to RDS

1. Check security groups allow Lambda to access RDS (port 5432)
2. If using VPC, ensure Lambda is in the same VPC as RDS
3. Check RDS is publicly accessible (for simple setup)

### Cold Start Issues

- Lambda cold starts can be 2-5 seconds
- Consider using provisioned concurrency (not free tier)
- Or use API Gateway caching

### Database Connection Pooling

- Current setup uses connection pooling
- For high traffic, consider RDS Proxy (not free tier)

## Cost Estimation (Free Tier)

- **Lambda**: 1M requests/month free
- **API Gateway**: 1M requests/month free
- **RDS**: 750 hours/month free (db.t3.micro)
- **Data Transfer**: 100 GB/month free

**Total**: $0/month for first 12 months (new AWS account)

## Next Steps

1. Set up CloudWatch alarms for monitoring
2. Configure automatic backups
3. Set up CI/CD pipeline
4. Consider using AWS Secrets Manager for sensitive data

