#!/bin/bash

# Script to clean up duplicate GitHub Pages artifacts
# Run this if you encounter "Multiple artifacts named 'github-pages'" error

echo "Cleaning up GitHub Pages artifacts..."

# You'll need to have GitHub CLI (gh) installed and authenticated
# Install with: brew install gh
# Authenticate with: gh auth login

# Get the repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

if [ -z "$REPO" ]; then
    echo "Error: Could not determine repository. Make sure you're in a git repository and gh is authenticated."
    exit 1
fi

echo "Working on repository: $REPO"

# List all artifacts
echo "Fetching artifacts..."
ARTIFACTS=$(gh api "/repos/$REPO/actions/artifacts" --jq '.artifacts[] | select(.name == "github-pages") | .id')

if [ -z "$ARTIFACTS" ]; then
    echo "No github-pages artifacts found."
    exit 0
fi

# Count artifacts
COUNT=$(echo "$ARTIFACTS" | wc -l | tr -d ' ')
echo "Found $COUNT github-pages artifact(s)"

if [ "$COUNT" -gt 1 ]; then
    echo "Multiple artifacts found. Cleaning up old ones..."

    # Keep only the most recent artifact
    # Get all artifacts sorted by creation date, skip the first (newest)
    OLD_ARTIFACTS=$(gh api "/repos/$REPO/actions/artifacts" \
        --jq '.artifacts[] | select(.name == "github-pages") | "\(.created_at)|\(.id)"' \
        | sort -r | tail -n +2 | cut -d'|' -f2)

    for ARTIFACT_ID in $OLD_ARTIFACTS; do
        echo "Deleting artifact ID: $ARTIFACT_ID"
        gh api -X DELETE "/repos/$REPO/actions/artifacts/$ARTIFACT_ID"
    done

    echo "Cleanup complete!"
else
    echo "Only one artifact found. No cleanup needed."
fi

# Cancel any pending workflow runs
echo ""
echo "Checking for pending workflow runs..."
PENDING_RUNS=$(gh run list --workflow=deploy.yml --status=in_progress --json databaseId -q '.[].databaseId')

if [ -n "$PENDING_RUNS" ]; then
    echo "Found pending workflow runs. Cancelling..."
    for RUN_ID in $PENDING_RUNS; do
        echo "Cancelling run ID: $RUN_ID"
        gh run cancel "$RUN_ID"
    done
fi

echo ""
echo "Done! You can now re-run your deployment workflow."