#!/bin/bash
set -e

# AWS CloudFront + S3 Teardown Script for DTCC Web
# This script removes all resources created by setup-aws-cloudfront.sh

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}========================================${NC}"
echo -e "${RED}AWS CloudFront + S3 Teardown${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will DELETE all resources!${NC}"
echo ""

# Load configuration
CONFIG_FILE=".aws-cloudfront-config"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: ${CONFIG_FILE}"
    echo "Please run setup-aws-cloudfront.sh first or manually specify resources"
    exit 1
fi

source "$CONFIG_FILE"

echo "Resources to be deleted:"
echo "  - CloudFront Distribution: ${CLOUDFRONT_DISTRIBUTION_ID}"
echo "  - S3 Bucket: ${S3_BUCKET}"
echo "  - Response Headers Policy: ${RESPONSE_HEADERS_POLICY_ID}"
echo "  - Origin Access Control: ${CLOUDFRONT_OAC_ID}"
echo ""

read -p "Are you ABSOLUTELY sure? Type 'delete' to confirm: " CONFIRM
if [ "$CONFIRM" != "delete" ]; then
    echo "Aborted."
    exit 0
fi

echo ""

# Step 1: Disable CloudFront Distribution
echo -e "${BLUE}[1/5] Disabling CloudFront distribution...${NC}"
CURRENT_CONFIG=$(aws cloudfront get-distribution-config --id ${CLOUDFRONT_DISTRIBUTION_ID})
ETAG=$(echo "$CURRENT_CONFIG" | jq -r '.ETag')
DIST_CONFIG=$(echo "$CURRENT_CONFIG" | jq '.DistributionConfig | .Enabled = false')

echo "$DIST_CONFIG" | aws cloudfront update-distribution \
    --id ${CLOUDFRONT_DISTRIBUTION_ID} \
    --distribution-config file:///dev/stdin \
    --if-match ${ETAG} > /dev/null

echo "✅ Distribution disabled (waiting for deployment...)"
echo "   This can take 15-20 minutes..."

# Wait for distribution to be disabled
while true; do
    STATUS=$(aws cloudfront get-distribution --id ${CLOUDFRONT_DISTRIBUTION_ID} --query 'Distribution.Status' --output text)
    ENABLED=$(aws cloudfront get-distribution --id ${CLOUDFRONT_DISTRIBUTION_ID} --query 'Distribution.DistributionConfig.Enabled' --output text)

    echo "   Status: ${STATUS}, Enabled: ${ENABLED}"

    if [ "$STATUS" == "Deployed" ] && [ "$ENABLED" == "False" ]; then
        break
    fi

    sleep 30
done

echo "✅ Distribution disabled and deployed"
echo ""

# Step 2: Delete CloudFront Distribution
echo -e "${BLUE}[2/5] Deleting CloudFront distribution...${NC}"
ETAG=$(aws cloudfront get-distribution --id ${CLOUDFRONT_DISTRIBUTION_ID} --query 'ETag' --output text)
aws cloudfront delete-distribution --id ${CLOUDFRONT_DISTRIBUTION_ID} --if-match ${ETAG}
echo "✅ CloudFront distribution deleted"
echo ""

# Step 3: Empty and Delete S3 Bucket
echo -e "${BLUE}[3/5] Emptying and deleting S3 bucket...${NC}"
echo "   Removing all objects..."
aws s3 rm s3://${S3_BUCKET} --recursive

echo "   Removing all versions (if versioning enabled)..."
aws s3api list-object-versions \
    --bucket ${S3_BUCKET} \
    --output json \
    --query 'Versions[].{Key:Key,VersionId:VersionId}' | \
    jq -r '.[] | "--key \"\(.Key)\" --version-id \"\(.VersionId)\""' | \
    xargs -I {} sh -c "aws s3api delete-object --bucket ${S3_BUCKET} {}" 2>/dev/null || true

echo "   Deleting bucket..."
aws s3 rb s3://${S3_BUCKET} --force
echo "✅ S3 bucket deleted"
echo ""

# Step 4: Delete Response Headers Policy
echo -e "${BLUE}[4/5] Deleting Response Headers Policy...${NC}"
POLICY_ETAG=$(aws cloudfront get-response-headers-policy --id ${RESPONSE_HEADERS_POLICY_ID} --query 'ETag' --output text 2>/dev/null || echo "")
if [ -n "$POLICY_ETAG" ]; then
    aws cloudfront delete-response-headers-policy --id ${RESPONSE_HEADERS_POLICY_ID} --if-match ${POLICY_ETAG}
    echo "✅ Response Headers Policy deleted"
else
    echo "⚠️  Response Headers Policy not found (may already be deleted)"
fi
echo ""

# Step 5: Delete Origin Access Control
echo -e "${BLUE}[5/5] Deleting Origin Access Control...${NC}"
OAC_ETAG=$(aws cloudfront get-origin-access-control --id ${CLOUDFRONT_OAC_ID} --query 'ETag' --output text 2>/dev/null || echo "")
if [ -n "$OAC_ETAG" ]; then
    aws cloudfront delete-origin-access-control --id ${CLOUDFRONT_OAC_ID} --if-match ${OAC_ETAG}
    echo "✅ Origin Access Control deleted"
else
    echo "⚠️  Origin Access Control not found (may already be deleted)"
fi
echo ""

# Remove config file
rm -f "$CONFIG_FILE"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      Teardown Complete! 🗑️             ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "All AWS resources have been deleted."
echo "Configuration file removed: ${CONFIG_FILE}"
echo ""
