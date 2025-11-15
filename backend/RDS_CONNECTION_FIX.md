# RDS Connection Issue Fix

## Problem
Lambda is trying to connect to RDS but getting connection timeouts. This is a network/security group configuration issue.

## Solution

### Option 1: Update RDS Security Group (Recommended)

1. Go to [RDS Console](https://us-west-1.console.aws.amazon.com/rds/home?region=us-west-1#databases:)
2. Select your RDS instance: `dsa-patterns`
3. Click on the **VPC security group** link
4. In the Security Group, click **Edit inbound rules**
5. Add a rule:
   - **Type**: PostgreSQL
   - **Protocol**: TCP
   - **Port**: 5432
   - **Source**: 
     - Option A: `0.0.0.0/0` (allows from anywhere - for public RDS)
     - Option B: The Lambda function's VPC security group (if Lambda is in a VPC)
     - Option C: Your IP address for testing
6. Click **Save rules**

### Option 2: Check RDS Public Accessibility

1. In RDS Console, select your instance
2. Check **Connectivity & security** tab
3. Ensure **Publicly accessible** is set to **Yes**
4. If not, you'll need to modify the instance (this may cause downtime)

### Option 3: Lambda VPC Configuration (If RDS is in a VPC)

If your RDS is in a VPC and not publicly accessible:

1. Go to Lambda Console → `dsa-patterns-api` → Configuration → VPC
2. Configure Lambda to be in the same VPC as RDS
3. Add the same subnets and security groups
4. This will allow Lambda to reach RDS through the VPC

## Verify Connection

After updating the security group, test the connection:

```bash
API_URL="https://5n2tv37eki.execute-api.us-west-1.amazonaws.com/prod"
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Test update
curl -X PUT "$API_URL/api/problems/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test RDS Connection"}'
```

## Current Status

✅ Code is now correctly using RDS (runtime selection)
✅ Lambda environment variables are set correctly
❌ Network connection blocked (security group issue)

Once the security group is updated, the connection should work and data will persist to RDS instead of Supabase.

