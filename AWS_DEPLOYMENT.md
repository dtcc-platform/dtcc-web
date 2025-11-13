# AWS S3 + CloudFront Deployment Guide

This guide explains how to deploy the DTCC web platform to AWS S3 and CloudFront.

## Overview

The DTCC web platform supports dual deployment:
- **GitHub Pages**: Automatic deployment on push to main (existing workflow)
- **AWS S3 + CloudFront**: Manual deployment via GitHub Actions (this guide)

## Architecture

```
GitHub Actions → Build (base: '/') → S3 Bucket (eu-north-1) → CloudFront Distribution → Users
```

**Key Features:**
- ✅ No CORS issues (same-origin architecture)
- ✅ No Lambda@Edge needed (static headers via CloudFront Response Headers Policy)
- ✅ Optimized caching (HTML: 5min, Assets: 1year, Content: 5min)
- ✅ Automatic compression via CloudFront
- ✅ Manual deployment trigger for control

---

## Prerequisites

### 1. AWS Account Setup

You'll need:
- AWS Account with billing enabled
- IAM user with S3 and CloudFront permissions
- Access keys (Access Key ID + Secret Access Key)

### 2. Create IAM User for GitHub Actions

```bash
# Create IAM user
aws iam create-user --user-name github-actions-dtcc-deploy

# Attach required policies
aws iam attach-user-policy \
  --user-name github-actions-dtcc-deploy \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-user-policy \
  --user-name github-actions-dtcc-deploy \
  --policy-arn arn:aws:iam::aws:policy/CloudFrontFullAccess

# Create access keys
aws iam create-access-key --user-name github-actions-dtcc-deploy
```

**Save the output!** You'll need:
- `AccessKeyId`
- `SecretAccessKey`

**Security Note:** For production, use a more restrictive IAM policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation"
      ],
      "Resource": "arn:aws:cloudfront::*:distribution/*"
    }
  ]
}
```

---

## AWS Resources Setup

### Step 1: Create S3 Bucket

```bash
# Create bucket in eu-north-1 (Stockholm)
aws s3 mb s3://dtcc-web-production --region eu-north-1

# Block all public access (CloudFront will access privately)
aws s3api put-public-access-block \
  --bucket dtcc-web-production \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
  --region eu-north-1

# Enable versioning (optional but recommended)
aws s3api put-bucket-versioning \
  --bucket dtcc-web-production \
  --versioning-configuration Status=Enabled \
  --region eu-north-1
```

### Step 2: Create CloudFront Distribution

#### Option A: AWS Console (Easiest)

1. Go to CloudFront Console: https://console.aws.amazon.com/cloudfront/
2. Click "Create Distribution"
3. Configure:

**Origin:**
- Origin domain: `dtcc-web-production.s3.eu-north-1.amazonaws.com`
- Name: `S3-dtcc-web`
- Origin access: **Origin access control settings (recommended)**
  - Click "Create new OAC" → Create
- Enable Origin Shield: No (optional for cost savings)

**Default Cache Behavior:**
- Viewer protocol policy: **Redirect HTTP to HTTPS**
- Allowed HTTP methods: **GET, HEAD, OPTIONS**
- Cache policy: **CachingDisabled** (we set cache via S3 metadata)
- Origin request policy: **CORS-S3Origin**
- Response headers policy: **Create new policy** (see Step 3)
- Compress objects automatically: **Yes**

**Settings:**
- Price class: **Use all edge locations** (or select Europe/US for cost savings)
- Alternate domain name (CNAME): `dtcc.yourdomain.com` (optional)
- Custom SSL certificate: **Request certificate via ACM** (if using custom domain)
- Default root object: `index.html`

4. Click "Create Distribution"
5. **Important**: Copy the Distribution ID (e.g., `E1234567890ABC`)

#### Option B: CloudFormation (Infrastructure as Code)

See `cloudformation/cloudfront-distribution.yml` template (create this file if needed for full automation).

### Step 3: Create Response Headers Policy

1. Go to CloudFront → Policies → Response headers
2. Click "Create response headers policy"
3. Configure:

**Policy details:**
- Name: `DTCC-Security-Headers`
- Description: `Security headers for DTCC web platform`

**Security headers:**
- Content Security Policy:
  - ✅ Enable
  - Value: `default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; frame-src 'self' https://www.youtube-nocookie.com https://www.youtube.com; child-src 'self' https://www.youtube-nocookie.com https://www.youtube.com; connect-src 'self'; img-src 'self' https: data: blob:; media-src 'self' https:; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; upgrade-insecure-requests`
  - Override: No

- X-Frame-Options:
  - ✅ Enable
  - Value: **DENY**
  - Override: No

- X-Content-Type-Options:
  - ✅ Enable
  - Override: No

- Referrer-Policy:
  - ✅ Enable
  - Value: **strict-origin-when-cross-origin**
  - Override: No

- X-XSS-Protection:
  - ✅ Enable
  - Protection: **Enabled**
  - Mode block: **Yes**
  - Override: No

**Custom headers:**
- Add custom header:
  - Header name: `Permissions-Policy`
  - Value: `geolocation=(), microphone=(), camera=()`
  - Override: Yes

4. Click "Create"
5. Go back to your CloudFront distribution → Behaviors → Edit default behavior
6. Select your new "DTCC-Security-Headers" policy
7. Save changes

### Step 4: Update S3 Bucket Policy for CloudFront OAC

After creating the CloudFront distribution with OAC, CloudFront will provide you with a bucket policy. Apply it:

```bash
# AWS Console will show the policy - copy and apply it
# Or use this template (replace DISTRIBUTION-ID and AWS-ACCOUNT-ID):
```

```json
{
  "Version": "2012-10-17",
  "Statement": {
    "Sid": "AllowCloudFrontServicePrincipalReadOnly",
    "Effect": "Allow",
    "Principal": {
      "Service": "cloudfront.amazonaws.com"
    },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::dtcc-web-production/*",
    "Condition": {
      "StringEquals": {
        "AWS:SourceArn": "arn:aws:cloudfront::YOUR-AWS-ACCOUNT-ID:distribution/YOUR-DISTRIBUTION-ID"
      }
    }
  }
}
```

Apply the policy:
```bash
aws s3api put-bucket-policy \
  --bucket dtcc-web-production \
  --policy file://bucket-policy.json \
  --region eu-north-1
```

---

## GitHub Configuration

### Configure GitHub Secrets

1. Go to your GitHub repository: https://github.com/dtcc-platform/dtcc-web
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click "New repository secret" for each:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AWS_ACCESS_KEY_ID` | Your IAM user access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Your IAM user secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `S3_BUCKET` | Your S3 bucket name | `dtcc-web-production` |
| `CLOUDFRONT_DISTRIBUTION_ID` | Your CloudFront distribution ID | `E1234567890ABC` |

**Security Best Practices:**
- ✅ Never commit these values to git
- ✅ Rotate access keys every 90 days
- ✅ Use least-privilege IAM policies
- ✅ Consider using OIDC instead of long-lived keys (see Advanced section)

---

## Deploying to AWS

### Manual Deployment via GitHub Actions

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select "Deploy to AWS S3 + CloudFront" workflow
4. Click "Run workflow"
5. Options:
   - **Branch**: main (or your target branch)
   - **Invalidate CloudFront cache**: ✅ Yes (recommended)
6. Click "Run workflow"

### Monitor Deployment

The workflow will:
1. ✅ Checkout code
2. ✅ Install dependencies
3. ✅ Build with `DEPLOY_TARGET=cloudfront` (base: '/')
4. ✅ Upload hashed assets to S3 (1-year cache)
5. ✅ Upload HTML files to S3 (5-minute cache)
6. ✅ Upload content JSON to S3 (5-minute cache)
7. ✅ Invalidate CloudFront cache (optional)

**Deployment time:** ~2-5 minutes

### Verify Deployment

After deployment completes:

```bash
# Check S3 bucket contents
aws s3 ls s3://dtcc-web-production/ --recursive --human-readable

# Check CloudFront distribution status
aws cloudfront get-distribution --id YOUR-DISTRIBUTION-ID

# Test the website
curl -I https://YOUR-CLOUDFRONT-DOMAIN/
```

Visit your CloudFront URL or custom domain to verify the deployment.

---

## Cache Strategy

### Cache Configuration by File Type

| Path Pattern | Cache Duration | Cache-Control Header | Reasoning |
|--------------|----------------|---------------------|-----------|
| `/*.html` | 5 minutes | `public, max-age=300, must-revalidate` | HTML changes frequently with content updates |
| `/assets/*` | 1 year | `public, max-age=31536000, immutable` | Hashed filenames = safe to cache forever |
| `/content/*` | 5 minutes | `public, max-age=300` | JSON content may update periodically |
| Other files | CloudFront default | N/A | Images, videos, etc. |

### Cache Invalidation

**When to invalidate:**
- After deploying new HTML content
- After updating JSON data in `/content/`
- After critical bug fixes

**Cost:** First 1,000 paths/month are **free**, then $0.005 per path.

**Best Practice:** Only invalidate non-hashed files (HTML, JSON). Hashed assets (`/assets/*`) never need invalidation.

---

## Troubleshooting

### Issue: S3 Access Denied

**Symptoms:** `403 Forbidden` errors when accessing files via CloudFront

**Solution:**
1. Verify S3 bucket policy allows CloudFront OAC access
2. Check that public access is blocked (CloudFront should be the only access point)
3. Ensure CloudFront OAC is configured correctly

```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket dtcc-web-production --region eu-north-1
```

### Issue: CloudFront Invalidation Fails

**Symptoms:** Workflow fails at invalidation step

**Solution:**
1. Verify `CLOUDFRONT_DISTRIBUTION_ID` secret is set correctly
2. Check IAM user has `cloudfront:CreateInvalidation` permission
3. Ensure distribution ID format is correct (e.g., `E1234567890ABC`)

### Issue: Website Shows Old Content

**Symptoms:** Changes don't appear after deployment

**Solution:**
1. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
2. Wait for CloudFront cache to expire (5 minutes for HTML)
3. Manually trigger invalidation via workflow or AWS Console
4. Check S3 bucket to verify new files were uploaded

```bash
# Verify latest files in S3
aws s3 ls s3://dtcc-web-production/assets/ --recursive | tail -20
```

### Issue: CSP Violations in Browser Console

**Symptoms:** Content Security Policy errors blocking resources

**Solution:**
1. Verify CloudFront Response Headers Policy is attached to distribution
2. Check policy configuration matches expected CSP
3. Wait 5-10 minutes for CloudFront configuration to propagate

### Issue: Deployment Fails with "Invalid Cache-Control"

**Symptoms:** `aws s3 sync` command fails

**Solution:**
1. Ensure AWS CLI is up to date: `aws --version`
2. Verify cache-control syntax in workflow file
3. Check AWS credentials have `s3:PutObject` permission

---

## Cost Estimation

### Monthly Cost Breakdown (Assumptions: 10,000 visits, 100GB transfer)

| Service | Usage | Cost (USD) |
|---------|-------|------------|
| **S3 Storage** | 10GB | $0.23 |
| **S3 Requests** | ~500K GET requests | $0.20 |
| **CloudFront Transfer** | 100GB to internet | $8.50 |
| **CloudFront Requests** | ~500K HTTPS requests | $0.50 |
| **Invalidations** | ~100 paths/month | $0.00 (free tier) |
| **Total** | | **~$9.43/month** |

**Free Tier Benefits (First 12 months):**
- CloudFront: 1TB data transfer out, 10M HTTP/HTTPS requests
- S3: 5GB storage, 20K GET requests, 2K PUT requests

**Scaling:** Costs scale linearly with traffic. For 100K visits, expect ~$50-80/month.

---

## Advanced Configuration

### Option 1: Custom Domain with HTTPS

1. **Request SSL Certificate in ACM (us-east-1 only for CloudFront):**
```bash
aws acm request-certificate \
  --domain-name dtcc.yourdomain.com \
  --validation-method DNS \
  --region us-east-1
```

2. **Add CNAME record for validation** (via your DNS provider)

3. **Update CloudFront distribution:**
   - Add alternate domain name: `dtcc.yourdomain.com`
   - Select ACM certificate

4. **Add DNS CNAME record** pointing to CloudFront distribution domain

### Option 2: Multiple Cache Behaviors (Advanced Caching)

For better performance, configure separate cache behaviors:

| Path Pattern | Cache Policy | TTL | Compress |
|--------------|-------------|-----|----------|
| `/assets/*` | Managed-CachingOptimized | 1 year | Yes |
| `/content/*` | Custom-5MinCache | 5 min | Yes |
| `/*.html` | Managed-CachingDisabled | No cache | Yes |
| `/videos/*` | Managed-CachingOptimized | 7 days | No |

### Option 3: Use OIDC Instead of Access Keys (Most Secure)

Replace long-lived AWS access keys with GitHub OIDC:

1. **Create IAM Identity Provider:**
```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

2. **Create IAM Role with trust policy**
3. **Update workflow** to use `aws-actions/configure-aws-credentials@v4` with `role-to-assume`

**Benefits:**
- ✅ No long-lived credentials
- ✅ Automatic rotation
- ✅ Better security posture
- ✅ AWS recommended approach

---

## Monitoring & Maintenance

### CloudWatch Metrics

Monitor your deployment:
- **S3:** Storage, requests, data transfer
- **CloudFront:** Cache hit ratio, requests, data transfer, error rates

```bash
# Get CloudFront metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --dimensions Name=DistributionId,Value=YOUR-DISTRIBUTION-ID \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-31T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

### Cost Monitoring

Set up billing alerts:
```bash
# Create SNS topic for billing alerts
aws sns create-topic --name billing-alerts --region us-east-1

# Subscribe to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT-ID:billing-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

Then create CloudWatch billing alarm via AWS Console.

---

## Dual Deployment Workflow

The platform supports both GitHub Pages and AWS deployments:

### GitHub Pages (Automatic)
- **Trigger:** Push to main branch
- **Workflow:** `.github/workflows/deploy.yml`
- **Base URL:** `/dtcc-web/`
- **Domain:** `https://dtcc-platform.github.io/dtcc-web/`
- **Purpose:** Development, staging, preview

### AWS S3 + CloudFront (Manual)
- **Trigger:** Manual workflow dispatch
- **Workflow:** `.github/workflows/deploy-aws.yml`
- **Base URL:** `/`
- **Domain:** CloudFront distribution or custom domain
- **Purpose:** Production deployment

**Configuration:** Both workflows use the same codebase. The `DEPLOY_TARGET` environment variable controls the base path.

---

## Security Checklist

Before deploying to production:

- [ ] S3 bucket has public access blocked
- [ ] CloudFront OAC is configured (not legacy OAI)
- [ ] IAM user has minimal permissions (least privilege)
- [ ] AWS credentials are stored as GitHub Secrets (not committed to git)
- [ ] CloudFront Response Headers Policy is attached
- [ ] CSP headers are configured correctly
- [ ] SSL certificate is valid (if using custom domain)
- [ ] CloudWatch billing alerts are set up
- [ ] S3 versioning is enabled (for rollback capability)
- [ ] Deployment has been tested on staging/preview

---

## Rollback Procedure

If a deployment breaks the site:

### Option 1: S3 Versioning (If Enabled)
```bash
# List versions
aws s3api list-object-versions --bucket dtcc-web-production

# Restore previous version
aws s3api copy-object \
  --copy-source dtcc-web-production/index.html?versionId=VERSION-ID \
  --bucket dtcc-web-production \
  --key index.html
```

### Option 2: Redeploy Previous Commit
1. Identify working commit: `git log`
2. Check out previous commit: `git checkout COMMIT-HASH`
3. Trigger AWS deployment workflow
4. After verification, merge fix to main

### Option 3: Emergency Rollback via GitHub Pages
If AWS deployment is broken, users can temporarily access the GitHub Pages deployment at:
`https://dtcc-platform.github.io/dtcc-web/`

---

## Support & Resources

### Documentation
- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [GitHub Actions with AWS](https://github.com/aws-actions)

### Useful Commands
```bash
# Build locally for CloudFront
DEPLOY_TARGET=cloudfront npm run build

# Preview build locally
npm run preview

# Check build size
du -sh dist/

# Analyze bundle
open dist/stats.html

# List CloudFront distributions
aws cloudfront list-distributions

# Get distribution config
aws cloudfront get-distribution-config --id DISTRIBUTION-ID
```

---

## Next Steps

After successful deployment:

1. **Set up custom domain** (optional but recommended)
2. **Configure CloudWatch alarms** for monitoring
3. **Enable S3 logging** for audit trail
4. **Set up automated backups** of S3 bucket
5. **Consider WAF** for additional security (optional, adds cost)
6. **Optimize cache behaviors** based on real traffic patterns
7. **Review and rotate IAM credentials** regularly

---

**Last Updated:** 2025-01-13
**Maintained By:** DTCC Platform Team
