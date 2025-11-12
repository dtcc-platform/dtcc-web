# LinkedIn Posts Automation Setup

This guide explains how to set up automated LinkedIn posts fetching for the DTCC website.

## Prerequisites

1. LinkedIn API access token with read permissions for your organization
2. GitHub repository admin access to add secrets

## Setting Up the LinkedIn Access Token

### Step 1: Add the Secret to GitHub

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:
   - **Name:** `LINKEDIN_ACCESS_TOKEN`
   - **Value:** Your LinkedIn API access token
5. Click **Add secret**

### Step 2: Verify the Workflow

The workflow file `.github/workflows/update-linkedin-posts.yml` is already configured to:

- Fetch up to 20 most recent LinkedIn posts
- Download and store images locally
- Update the JSON file only if changes are detected
- Run manually or on a weekly schedule (Mondays at 9 AM UTC)

## Running the LinkedIn Update

### Manual Trigger

1. Go to the **Actions** tab in your GitHub repository
2. Select **"Update LinkedIn Posts"** from the left sidebar
3. Click **"Run workflow"** button
4. Options:
   - **Force update**: Check this to update even if no changes are detected
   - **Branch**: Select the branch to run on (usually `main`)
5. Click the green **"Run workflow"** button

### Automatic Schedule

The workflow runs automatically every Monday at 9 AM UTC. You can modify this schedule in the workflow file by changing the cron expression.

## What the Workflow Does

1. **Fetches LinkedIn Posts**: Uses the API to get the 20 most recent posts
2. **Downloads Images**: Saves images locally in `public/content/social/linkedin-images/`
3. **Updates JSON**: Updates `public/content/social/linkedin_posts_complete.json`
4. **Detects Changes**: Only commits if there are actual changes
5. **Commits Updates**: Automatically commits and pushes changes with a descriptive message

## Monitoring

After each run, check the workflow summary for:
- Number of posts fetched
- Changes detected
- Posts with media/images
- Any errors encountered

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify the `LINKEDIN_ACCESS_TOKEN` secret is correctly set
   - Check if the token has expired
   - Ensure the token has read permissions for your organization

2. **No Posts Found**
   - Verify the organization ID in the script (currently: `100491988`)
   - Check if the organization has published posts

3. **Image Download Failures**
   - Check network connectivity
   - Verify image URLs are accessible
   - Review the workflow logs for specific error messages

### Script Configuration

The LinkedIn scraping script (`scripts/linkedin_scrape.py`) is configured to:
- Fetch 20 posts (line 157: `"count": 20`)
- Sort by last modified date
- Download images locally
- Include post metadata

To modify the number of posts fetched, edit line 157 in the script.

## Security Notes

- Never commit the LinkedIn access token directly in code
- Keep the token in GitHub secrets only
- Rotate the token periodically for security
- Limit token permissions to read-only access

## Local Testing

To test the script locally:

```bash
# Set the environment variable
export LINKEDIN_ACCESS_TOKEN="your-token-here"

# Run the script
python3 scripts/linkedin_scrape.py
```

## Website Display

The fetched LinkedIn posts are displayed on the website's Social Feed component, which shows:
- Initially 6 posts
- "Load More" button to show additional posts (up to 20)
- Post images, dates, and summaries
- Links to view full posts on LinkedIn