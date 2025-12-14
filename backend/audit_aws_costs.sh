#!/bin/bash
# AWS Cost Audit Script

REGION="us-west-1"

echo "=========================================="
echo "AWS Cost Audit - Checking Active Resources"
echo "=========================================="
echo ""

echo "1. RDS INSTANCES"
echo "-------------------"
aws rds describe-db-instances --region $REGION \
  --query 'DBInstances[].{Identifier:DBInstanceIdentifier,Status:DBInstanceStatus,Engine:Engine,Class:DBInstanceClass}' \
  --output table 2>&1 | head -20 || echo "⚠️  No permission or no instances"

echo ""
echo "2. RDS SNAPSHOTS"
echo "-------------------"
aws rds describe-db-snapshots --region $REGION \
  --query 'DBSnapshots[?Status==`available`].{SnapshotId:DBSnapshotIdentifier,Size:AllocatedStorage,Date:SnapshotCreateTime}' \
  --output table 2>&1 | head -20 || echo "⚠️  No permission or no snapshots"

echo ""
echo "3. CLOUDWATCH LOG GROUPS"
echo "-------------------"
aws logs describe-log-groups --region $REGION \
  --query 'logGroups[].{Name:logGroupName,Retention:retentionInDays,SizeMB:round(storedBytes/1024/1024,2)}' \
  --output table 2>&1 | head -30

echo ""
echo "4. NAT GATEWAYS"
echo "-------------------"
aws ec2 describe-nat-gateways --region $REGION \
  --filter "Name=state,Values=available,pending" \
  --query 'NatGateways[].{Id:NatGatewayId,State:State}' \
  --output table 2>&1 | head -10 || echo "⚠️  No permission or no NAT Gateways"

echo ""
echo "5. VPC ENDPOINTS"
echo "-------------------"
aws ec2 describe-vpc-endpoints --region $REGION \
  --query 'VpcEndpoints[].{Id:VpcEndpointId,Service:ServiceName,State:State}' \
  --output table 2>&1 | head -10 || echo "⚠️  No permission or no endpoints"

echo ""
echo "6. UNATTACHED ELASTIC IPs"
echo "-------------------"
aws ec2 describe-addresses --region $REGION \
  --filter "Name=domain,Values=vpc" \
  --query 'Addresses[?AssociationId==null].{AllocationId:AllocationId,PublicIp:PublicIp}' \
  --output table 2>&1 | head -10 || echo "⚠️  No permission or no unattached IPs"

echo ""
echo "=========================================="
echo "Audit Complete"
echo "=========================================="
echo ""
echo "💡 Tip: Check AWS Cost Explorer for detailed cost breakdown:"
echo "   https://console.aws.amazon.com/cost-management/home#/cost-explorer"
