# LinkedIn Posts Automation Setup

This guide explains how to set up automated LinkedIn posts fetching for the DTCC website.

## Prerequisites

1. LinkedIn application with programmatic refresh-token access and read permissions for your organization
2. GitHub repository admin access to add secrets

## Setting Up LinkedIn Credentials

### Step 1: Add the Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of these secrets using **Add secret**:
   - `LINKEDIN_CLIENT_ID`: your LinkedIn application client ID
   - `LINKEDIN_CLIENT_SECRET`: your LinkedIn application client secret
   - `LINKEDIN_REFRESH_TOKEN`: the refresh token obtained through local authorization

Each import exchanges the refresh token for a fresh access token and keeps it in
memory. `LINKEDIN_ACCESS_TOKEN` is no longer used by the importer. Tokens are not
printed in workflow logs or saved in repository files.

### Step 2: Verify the Workflow

The workflow file `.github/workflows/update-linkedin-posts.yml` is already configured to:

- Fetch up to 20 most recent LinkedIn posts
- Download and store images locally
- Update the JSON file only if changes are detected
- Run manually or daily at midnight UTC

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

The workflow is scheduled daily at midnight UTC; GitHub may delay scheduled runs.
If GitHub has disabled it for repository inactivity, use **Enable workflow** on
its Actions page. Updating the code does not itself verify or re-enable a disabled
workflow.

## What the Workflow Does

1. **Renews access and fetches LinkedIn posts**: Uses the stored refresh token to obtain an access token, then gets the 20 most recent posts
2. **Downloads Images**: Saves images locally in `public/content/social/linkedin-images/`
3. **Updates JSON**: Updates `public/content/social/linkedin_posts_complete.json`
4. **Detects Changes**: Only commits if there are actual changes
5. **Commits Updates**: Automatically commits and pushes changes with a descriptive message

Requests have connect/read timeouts and at most three attempts for temporary
connection failures, timeouts, rate limits, and transient server errors. Retry
delays are capped at 60 seconds. Authentication errors fail immediately. Failed
requests or invalid responses fail the job and preserve the existing feed JSON.
JSON and downloaded images are written to temporary files before replacement.

Optional image and reshare-parent lookups retain their existing fallback behavior;
their failures are logged and do not abort an otherwise valid posts fetch.

## Monitoring

After each run, check the workflow summary for:
- Number of posts fetched
- Changes detected
- Posts with media/images
- Any errors encountered

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify all three credential secrets are correctly set
   - Run **Refresh LinkedIn Token** to check that renewal works; this reports success or failure without printing tokens or changing secrets
   - An expired, revoked, or replaced refresh token requires local reauthorization and a secure update to `LINKEDIN_REFRESH_TOKEN`
   - Ensure the token has read permissions for your organization

Programmatic refresh tokens normally last one year. Exchanging them for access
tokens does not extend that lifetime. To reauthorize, run
`python3 scripts/linkedin_auth.py` in a private local terminal with the client
credentials configured, complete the LinkedIn authorization, and save the returned
refresh token in GitHub secrets. Do not run that interactive helper in Actions or
paste its output into logs or issues. See [LinkedIn's refresh-token documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens).

2. **No Posts Found**
   - Verify the organization ID in the script (currently: `100491988`)
   - Check if the organization has published posts

3. **Image Download Failures**
   - Check network connectivity
   - Verify image URLs are accessible
   - Review the workflow logs for specific error messages

### Script Configuration

The LinkedIn scraping script (`scripts/linkedin_scrape.py`) is configured to:
- Fetch 20 posts (`"count": 20`)
- Request the newest posts by creation date, then sort the merged feed by publication date
- Download images locally
- Include post metadata

To modify the number of posts fetched, edit `count` in the script's request parameters.

## Security Notes

- Never commit the LinkedIn access token directly in code
- Keep the token in GitHub secrets only
- Rotate the token periodically for security
- Limit token permissions to read-only access

## Local Testing

To test the script locally:

```bash
# Configure the same three credentials in your private local environment
export LINKEDIN_CLIENT_ID="your-client-id"
export LINKEDIN_CLIENT_SECRET="your-client-secret"
export LINKEDIN_REFRESH_TOKEN="your-refresh-token"

# Run the script
python3 scripts/linkedin_scrape.py
```

Run offline regression tests with `python3 -B -m unittest discover -s scripts/tests -v`.
They use temporary feed files and simulated HTTP responses, and need no credentials.

## Website Display

The fetched LinkedIn posts are displayed on the website's Social Feed component, which shows:
- Initially 6 posts
- "Load More" button to show additional posts (up to 20)
- Post images, dates, and summaries
- Links to view full posts on LinkedIn
