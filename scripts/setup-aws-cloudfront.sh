#!/bin/bash
set -e

# AWS CloudFront + S3 Setup Script for DTCC Web
# This script creates all necessary AWS resources via CLI

# Configuration - EDIT THESE VALUES
BUCKET_NAME="dtcc-web-production"
AWS_REGION="eu-north-1"
DISTRIBUTION_COMMENT="DTCC Web Platform"
# CUSTOM_DOMAIN="dtcc.yourdomain.com"  # Optional: Uncomment and set your custom domain
# ACM_CERT_ARN="arn:aws:acm:us-east-1:..."  # Optional: Required if using custom domain

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AWS CloudFront + S3 Setup for DTCC Web${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Create S3 Bucket
echo -e "${GREEN}[1/6] Creating S3 bucket: ${BUCKET_NAME}${NC}"
if aws s3 mb s3://${BUCKET_NAME} --region ${AWS_REGION} 2>/dev/null; then
    echo "✅ Bucket created successfully"
else
    echo "⚠️  Bucket may already exist (continuing...)"
fi

# Block all public access
echo "Blocking public access..."
aws s3api put-public-access-block \
    --bucket ${BUCKET_NAME} \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
    --region ${AWS_REGION}

# Enable versioning (optional but recommended for rollbacks)
echo "Enabling versioning..."
aws s3api put-bucket-versioning \
    --bucket ${BUCKET_NAME} \
    --versioning-configuration Status=Enabled \
    --region ${AWS_REGION}

echo "✅ S3 bucket configured"
echo ""

# Step 2: Create Origin Access Control (OAC)
echo -e "${GREEN}[2/6] Creating CloudFront Origin Access Control${NC}"
OAC_CONFIG=$(cat <<EOF
{
    "Name": "DTCC-S3-OAC",
    "Description": "Origin Access Control for DTCC S3 bucket",
    "SigningProtocol": "sigv4",
    "SigningBehavior": "always",
    "OriginAccessControlOriginType": "s3"
}
EOF
)

OAC_ID=$(aws cloudfront create-origin-access-control \
    --origin-access-control-config "$OAC_CONFIG" \
    --query 'OriginAccessControl.Id' \
    --output text 2>/dev/null || echo "")

if [ -z "$OAC_ID" ]; then
    echo "⚠️  OAC may already exist. Listing existing OACs:"
    aws cloudfront list-origin-access-controls --query 'OriginAccessControlList.Items[?Name==`DTCC-S3-OAC`].Id' --output text
    echo "You can use an existing OAC ID or delete it and re-run this script"
    read -p "Enter OAC ID to use (or press Enter to exit): " OAC_ID
    if [ -z "$OAC_ID" ]; then
        exit 1
    fi
fi

echo "✅ OAC created/retrieved: ${OAC_ID}"
echo ""

# Step 3: Create Response Headers Policy
echo -e "${GREEN}[3/6] Creating CloudFront Response Headers Policy${NC}"
HEADERS_POLICY_CONFIG=$(cat <<'EOF'
{
    "Name": "DTCC-Security-Headers",
    "Comment": "Security headers for DTCC web platform",
    "SecurityHeadersConfig": {
        "ContentSecurityPolicy": {
            "ContentSecurityPolicy": "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; frame-src 'self' https://www.youtube-nocookie.com https://www.youtube.com; child-src 'self' https://www.youtube-nocookie.com https://www.youtube.com; connect-src 'self'; img-src 'self' https: data: blob:; media-src 'self' https:; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; upgrade-insecure-requests",
            "Override": false
        },
        "ContentTypeOptions": {
            "Override": false
        },
        "FrameOptions": {
            "FrameOption": "DENY",
            "Override": false
        },
        "ReferrerPolicy": {
            "ReferrerPolicy": "strict-origin-when-cross-origin",
            "Override": false
        },
        "XSSProtection": {
            "Protection": true,
            "ModeBlock": true,
            "Override": false
        }
    },
    "CustomHeadersConfig": {
        "Items": [
            {
                "Header": "Permissions-Policy",
                "Value": "geolocation=(), microphone=(), camera=()",
                "Override": true
            }
        ]
    }
}
EOF
)

HEADERS_POLICY_ID=$(aws cloudfront create-response-headers-policy \
    --response-headers-policy-config "$HEADERS_POLICY_CONFIG" \
    --query 'ResponseHeadersPolicy.Id' \
    --output text 2>/dev/null || echo "")

if [ -z "$HEADERS_POLICY_ID" ]; then
    echo "⚠️  Headers policy may already exist. Listing existing policies:"
    aws cloudfront list-response-headers-policies --type custom --query 'ResponseHeadersPolicyList.Items[?ResponseHeadersPolicy.ResponseHeadersPolicyConfig.Name==`DTCC-Security-Headers`].ResponseHeadersPolicy.Id' --output text
    echo "You can use an existing policy ID or delete it and re-run this script"
    read -p "Enter Headers Policy ID to use (or press Enter to exit): " HEADERS_POLICY_ID
    if [ -z "$HEADERS_POLICY_ID" ]; then
        exit 1
    fi
fi

echo "✅ Response Headers Policy created/retrieved: ${HEADERS_POLICY_ID}"
echo ""

# Step 4: Create CloudFront Distribution
echo -e "${GREEN}[4/6] Creating CloudFront Distribution${NC}"

# Get AWS Account ID for bucket policy later
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build distribution config
DISTRIBUTION_CONFIG=$(cat <<EOF
{
    "CallerReference": "dtcc-web-$(date +%s)",
    "Comment": "${DISTRIBUTION_COMMENT}",
    "Enabled": true,
    "HttpVersion": "http2and3",
    "IsIPV6Enabled": true,
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-${BUCKET_NAME}",
                "DomainName": "${BUCKET_NAME}.s3.${AWS_REGION}.amazonaws.com",
                "OriginPath": "",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                },
                "OriginAccessControlId": "${OAC_ID}",
                "ConnectionAttempts": 3,
                "ConnectionTimeout": 10
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-${BUCKET_NAME}",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 3,
            "Items": ["GET", "HEAD", "OPTIONS"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "Compress": true,
        "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
        "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf",
        "ResponseHeadersPolicyId": "${HEADERS_POLICY_ID}",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "TrustedKeyGroups": {
            "Enabled": false,
            "Quantity": 0
        }
    },
    "CacheBehaviors": {
        "Quantity": 2,
        "Items": [
            {
                "PathPattern": "/assets/*",
                "TargetOriginId": "S3-${BUCKET_NAME}",
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                    "CachedMethods": {
                        "Quantity": 2,
                        "Items": ["GET", "HEAD"]
                    }
                },
                "Compress": true,
                "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
                "ResponseHeadersPolicyId": "${HEADERS_POLICY_ID}",
                "TrustedSigners": {
                    "Enabled": false,
                    "Quantity": 0
                },
                "TrustedKeyGroups": {
                    "Enabled": false,
                    "Quantity": 0
                }
            },
            {
                "PathPattern": "/content/*",
                "TargetOriginId": "S3-${BUCKET_NAME}",
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                    "CachedMethods": {
                        "Quantity": 2,
                        "Items": ["GET", "HEAD"]
                    }
                },
                "Compress": true,
                "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                "ResponseHeadersPolicyId": "${HEADERS_POLICY_ID}",
                "TrustedSigners": {
                    "Enabled": false,
                    "Quantity": 0
                },
                "TrustedKeyGroups": {
                    "Enabled": false,
                    "Quantity": 0
                }
            }
        ]
    },
    "CustomErrorResponses": {
        "Quantity": 0
    },
    "PriceClass": "PriceClass_100",
    "ViewerCertificate": {
        "CloudFrontDefaultCertificate": true,
        "MinimumProtocolVersion": "TLSv1.2_2021"
    }
}
EOF
)

echo "Creating distribution (this takes 5-15 minutes)..."
DISTRIBUTION_OUTPUT=$(aws cloudfront create-distribution \
    --distribution-config "$DISTRIBUTION_CONFIG" \
    --output json)

DISTRIBUTION_ID=$(echo "$DISTRIBUTION_OUTPUT" | jq -r '.Distribution.Id')
DISTRIBUTION_DOMAIN=$(echo "$DISTRIBUTION_OUTPUT" | jq -r '.Distribution.DomainName')

if [ -z "$DISTRIBUTION_ID" ]; then
    echo "❌ Failed to create distribution"
    exit 1
fi

echo "✅ CloudFront Distribution created!"
echo "   Distribution ID: ${DISTRIBUTION_ID}"
echo "   Domain: ${DISTRIBUTION_DOMAIN}"
echo "   Status: Deploying (takes ~15 minutes)"
echo ""

# Step 5: Update S3 Bucket Policy
echo -e "${GREEN}[5/6] Updating S3 bucket policy for CloudFront OAC${NC}"
BUCKET_POLICY=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": {
        "Sid": "AllowCloudFrontServicePrincipalReadOnly",
        "Effect": "Allow",
        "Principal": {
            "Service": "cloudfront.amazonaws.com"
        },
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::${BUCKET_NAME}/*",
        "Condition": {
            "StringEquals": {
                "AWS:SourceArn": "arn:aws:cloudfront::${AWS_ACCOUNT_ID}:distribution/${DISTRIBUTION_ID}"
            }
        }
    }
}
EOF
)

echo "$BUCKET_POLICY" | aws s3api put-bucket-policy \
    --bucket ${BUCKET_NAME} \
    --policy file:///dev/stdin

echo "✅ S3 bucket policy updated"
echo ""

# Step 6: Save configuration
echo -e "${GREEN}[6/6] Saving configuration${NC}"
CONFIG_FILE=".aws-cloudfront-config"
cat > "$CONFIG_FILE" <<EOF
# AWS CloudFront Configuration for DTCC Web
# Generated: $(date)

S3_BUCKET=${BUCKET_NAME}
AWS_REGION=${AWS_REGION}
CLOUDFRONT_DISTRIBUTION_ID=${DISTRIBUTION_ID}
CLOUDFRONT_DOMAIN=${DISTRIBUTION_DOMAIN}
CLOUDFRONT_OAC_ID=${OAC_ID}
RESPONSE_HEADERS_POLICY_ID=${HEADERS_POLICY_ID}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}
EOF

echo "✅ Configuration saved to ${CONFIG_FILE}"
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}           Setup Complete! 🚀           ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "📋 Configuration Summary:"
echo "   S3 Bucket:        ${BUCKET_NAME}"
echo "   Region:           ${AWS_REGION}"
echo "   Distribution ID:  ${DISTRIBUTION_ID}"
echo "   CloudFront URL:   https://${DISTRIBUTION_DOMAIN}"
echo ""
echo -e "${YELLOW}⏳ CloudFront is deploying (takes ~15 minutes)${NC}"
echo ""
echo "📝 Next Steps:"
echo "1. Add GitHub Secrets to your repository:"
echo "   AWS_ACCESS_KEY_ID"
echo "   AWS_SECRET_ACCESS_KEY"
echo "   S3_BUCKET=${BUCKET_NAME}"
echo "   CLOUDFRONT_DISTRIBUTION_ID=${DISTRIBUTION_ID}"
echo ""
echo "2. Check deployment status:"
echo "   aws cloudfront get-distribution --id ${DISTRIBUTION_ID} --query 'Distribution.Status'"
echo ""
echo "3. When status is 'Deployed', test your site:"
echo "   curl -I https://${DISTRIBUTION_DOMAIN}"
echo ""
echo "4. Deploy your site:"
echo "   Go to GitHub Actions → 'Deploy to AWS S3 + CloudFront' → Run workflow"
echo ""

# Optional: Check distribution status
read -p "Do you want to wait and monitor deployment status? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Monitoring deployment status (checks every 30 seconds)..."
    while true; do
        STATUS=$(aws cloudfront get-distribution --id ${DISTRIBUTION_ID} --query 'Distribution.Status' --output text)
        echo "$(date '+%H:%M:%S') - Status: ${STATUS}"

        if [ "$STATUS" == "Deployed" ]; then
            echo ""
            echo -e "${GREEN}✅ CloudFront distribution is now deployed!${NC}"
            echo "🌍 Your site is live at: https://${DISTRIBUTION_DOMAIN}"
            break
        fi

        sleep 30
    done
fi

echo ""
echo "Done! 🎉"
