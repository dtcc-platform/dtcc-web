#!/bin/bash
set -e

# Add CloudFront Function to handle directory index (e.g., /gallery/ -> /gallery/index.html)

DISTRIBUTION_ID="E1XLSUXZBHBUJG"

echo "Creating CloudFront Function for directory index rewriting..."

# Step 1: Create CloudFront Function
FUNCTION_CODE='function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // Check if URI ends with /
    if (uri.endsWith("/")) {
        request.uri += "index.html";
    }
    // Check if URI has no extension (no dot in last segment)
    else if (!uri.includes(".") && uri.split("/").pop().indexOf(".") === -1) {
        request.uri += "/index.html";
    }

    return request;
}'

# Create the function
FUNCTION_OUTPUT=$(aws cloudfront create-function \
  --name dtcc-directory-index \
  --function-config "Comment=Append index.html to directory requests,Runtime=cloudfront-js-2.0" \
  --function-code "$(echo "$FUNCTION_CODE" | base64)" \
  --query 'FunctionSummary.FunctionMetadata.FunctionARN' \
  --output text 2>/dev/null || echo "")

if [ -z "$FUNCTION_OUTPUT" ]; then
    echo "Function may already exist. Getting existing function..."
    FUNCTION_ARN=$(aws cloudfront list-functions \
      --query "FunctionList.Items[?Name=='dtcc-directory-index'].FunctionMetadata.FunctionARN" \
      --output text)

    if [ -z "$FUNCTION_ARN" ]; then
        echo "❌ Failed to create or find function"
        exit 1
    fi
else
    FUNCTION_ARN="$FUNCTION_OUTPUT"
fi

echo "✅ Function ARN: ${FUNCTION_ARN}"

# Step 2: Publish the function
echo "Publishing function..."
ETAG=$(aws cloudfront describe-function \
  --name dtcc-directory-index \
  --query 'ETag' \
  --output text)

aws cloudfront publish-function \
  --name dtcc-directory-index \
  --if-match "$ETAG" > /dev/null

echo "✅ Function published"

# Step 3: Get current distribution config
echo "Updating CloudFront distribution..."
DIST_CONFIG=$(aws cloudfront get-distribution-config --id ${DISTRIBUTION_ID})
DIST_ETAG=$(echo "$DIST_CONFIG" | jq -r '.ETag')

# Step 4: Add function association to default cache behavior
UPDATED_CONFIG=$(echo "$DIST_CONFIG" | jq '.DistributionConfig.DefaultCacheBehavior.FunctionAssociations = {
    "Quantity": 1,
    "Items": [{
        "FunctionARN": "'${FUNCTION_ARN}'",
        "EventType": "viewer-request"
    }]
}')

# Extract just the DistributionConfig
DIST_CONFIG_ONLY=$(echo "$UPDATED_CONFIG" | jq '.DistributionConfig')

# Step 5: Update distribution
echo "$DIST_CONFIG_ONLY" | aws cloudfront update-distribution \
  --id ${DISTRIBUTION_ID} \
  --distribution-config file:///dev/stdin \
  --if-match ${DIST_ETAG} > /dev/null

echo "✅ Distribution updated"
echo ""
echo "Deployment in progress (takes ~5 minutes)..."
echo ""
echo "Check status:"
echo "  aws cloudfront get-distribution --id ${DISTRIBUTION_ID} --query 'Distribution.Status'"
echo ""
echo "Once deployed, test:"
echo "  https://d1ftjxxdv5es83.cloudfront.net/gallery/"
echo ""
