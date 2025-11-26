# LinkedIn Posts Workflow Triggers GitHub Pages Deploy

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automatically deploy to GitHub Pages when LinkedIn posts are updated via the scheduled/manual workflow.

**Architecture:** Use GitHub Actions `workflow_call` to chain workflows. The LinkedIn workflow will call the deploy workflow after successfully committing new posts. This avoids the GITHUB_TOKEN limitation where pushes don't trigger other workflows.

**Tech Stack:** GitHub Actions

---

## Task 1: Add workflow_call trigger to deploy.yml

**Files:**
- Modify: `.github/workflows/deploy.yml:1-6`

**Step 1: Update the deploy workflow triggers**

Add `workflow_call` to the `on:` block so it can be called by other workflows:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:
  workflow_call:
```

**Step 2: Verify syntax**

Run: `cd /Users/vasnas/scratch/dtcc-web && cat .github/workflows/deploy.yml | head -10`

Expected: The `on:` block should now include `workflow_call:`

**Step 3: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "feat(ci): allow deploy workflow to be called by other workflows"
```

---

## Task 2: Add deploy job to LinkedIn workflow

**Files:**
- Modify: `.github/workflows/update-linkedin-posts.yml`

**Step 1: Add the deploy job at the end of the file**

After the `fetch-linkedin-posts` job, add a new job that calls the deploy workflow:

```yaml
  deploy:
    needs: fetch-linkedin-posts
    if: needs.fetch-linkedin-posts.outputs.has_changes == 'true'
    uses: ./.github/workflows/deploy.yml
    secrets: inherit
```

**Step 2: Add output to fetch-linkedin-posts job**

The deploy job needs to know if changes were made. Add `outputs` to the `fetch-linkedin-posts` job definition:

Find this line:
```yaml
  fetch-linkedin-posts:
    runs-on: ubuntu-latest
```

Replace with:
```yaml
  fetch-linkedin-posts:
    runs-on: ubuntu-latest
    outputs:
      has_changes: ${{ steps.check_changes.outputs.has_changes }}
```

**Step 3: Verify the full workflow structure**

Run: `cat .github/workflows/update-linkedin-posts.yml | grep -E "(jobs:|fetch-linkedin-posts:|deploy:|needs:|outputs:|has_changes)"`

Expected output should show:
- `jobs:`
- `fetch-linkedin-posts:` with `outputs:`
- `deploy:` with `needs: fetch-linkedin-posts`

**Step 4: Commit**

```bash
git add .github/workflows/update-linkedin-posts.yml
git commit -m "feat(ci): trigger GitHub Pages deploy after LinkedIn posts update"
```

---

## Task 3: Test the workflow

**Step 1: Push changes to main**

```bash
git push origin main
```

**Step 2: Manually trigger LinkedIn workflow to test**

Go to GitHub Actions > "Update LinkedIn Posts" > Run workflow > Enable "Force update"

**Step 3: Verify both jobs run**

Expected:
1. `fetch-linkedin-posts` job completes
2. `deploy` job triggers and completes
3. GitHub Pages is updated

---

## Summary of Changes

| File | Change |
|------|--------|
| `.github/workflows/deploy.yml` | Add `workflow_call` trigger |
| `.github/workflows/update-linkedin-posts.yml` | Add job output + deploy job |

Total: 2 files modified, ~10 lines added
