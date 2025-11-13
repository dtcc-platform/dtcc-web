#!/bin/bash
set -e

DISTRIBUTION_ID="E1XLSUXZBHBUJG"
FUNCTION_NAME="dtcc-directory-index"

echo "========================================="
echo "Fixing CloudFront Function"
echo "========================================="
echo ""

# Step 1: Create correct function code
echo "[1/4] Creating correct function code..."
cat > /tmp/cloudfront-function.js << 'EOF'
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // If URI ends with /, append index.html
    if (uri.endsWith('/')) {
        request.uri = uri + 'index.html';
    }
    // If URI is a directory path without trailing slash (e.g., /gallery)
    // and has no file extension, add /index.html
    else if (uri.lastIndexOf('.') < uri.lastIndexOf('/')) {
        request.uri = uri + '/index.html';
    }

    return request;
}
EOF
echo "✅ Function code created"
echo ""

# Step 2: Update the function
echo "[2/4] Updating CloudFront function..."
ETAG=$(aws cloudfront describe-function --name ${FUNCTION_NAME} --query 'ETag' --output text)

aws cloudfront update-function \
  --name ${FUNCTION_NAME} \
  --function-code fileb:///tmp/cloudfront-function.js \
  --function-config "Comment=Append index.html to directory requests,Runtime=cloudfront-js-2.0" \
  --if-match ${ETAG} > /dev/null

echo "✅ Function updated"
echo ""

# Step 3: Publish the function
echo "[3/4] Publishing function..."
NEW_ETAG=$(aws cloudfront describe-function --name ${FUNCTION_NAME} --query 'ETag' --output text)

aws cloudfront publish-function \
  --name ${FUNCTION_NAME} \
  --if-match ${NEW_ETAG} > /dev/null

echo "✅ Function published"
echo ""

# Step 4: Wait for CloudFront distribution to deploy
echo "[4/4] Waiting for CloudFront distribution to deploy..."
echo "This can take 5-10 minutes..."
echo ""

COUNTER=0
while true; do
    STATUS=$(aws cloudfront get-distribution --id ${DISTRIBUTION_ID} --query 'Distribution.Status' --output text)
    echo "$(date '+%H:%M:%S') - Status: ${STATUS}"

    if [ "$STATUS" == "Deployed" ]; then
        echo ""
        echo "✅ CloudFront distribution is deployed!"
        break
    fi

    sleep 30
    COUNTER=$((COUNTER + 1))

    if [ $COUNTER -gt 40 ]; then
        echo ""
        echo "⚠️  Deployment is taking longer than expected (>20 minutes)"
        echo "Check manually: aws cloudfront get-distribution --id ${DISTRIBUTION_ID} --query 'Distribution.Status'"
        break
    fi
done

echo ""
echo "========================================="
echo "Fix Complete! 🎉"
echo "========================================="
echo ""
echo "Test your site:"
echo "  https://d1ftjxxdv5es83.cloudfront.net/"
echo "  https://d1ftjxxdv5es83.cloudfront.net/gallery/"
echo "  https://d1ftjxxdv5es83.cloudfront.net/projects/"
echo ""
echo "All directory URLs should now work correctly!"
echo ""
