# Webhook bridge: contribute form → GitHub Issues

Cloudflare Worker that receives direct form POSTs from the Oslo Mental Health Map /contribute page
and creates a GitHub Issue for each submission, then redirects the visitor back
to /contribute/?submitted=true.

## Flow

```
/contribute (HTML form POST)
  → this Worker (parses fields, creates issue)
  → GitHub Issues API
  → redirect → /contribute/?submitted=true
```

## One-time setup

### 1. Create a GitHub fine-grained PAT

Go to **GitHub → Settings → Developer settings → Personal access tokens →
Fine-grained tokens → Generate new token**.

- Resource owner: `henrfo`
- Repository access: only `Oslo_Mental_Health_Map`
- Permissions:
  - Repository permissions → **Issues: Read and write**
  - Repository permissions → **Metadata: Read-only**

Copy the token — you'll need it in step 3.

### 2. Deploy the Worker

```bash
npm install -g wrangler
wrangler login
cd scripts/webhook-bridge
wrangler deploy
```

The Worker deploys to `https://omhm-webhook-bridge.openmritools.workers.dev`, the URL in the form `action` in `contribute.html`.

### 3. Add Worker secrets

```bash
wrangler secret put GITHUB_TOKEN
# paste the PAT from step 1

wrangler secret put GITHUB_REPO
# enter: henrfo/Oslo_Mental_Health_Map
```

### 4. Test

Submit a test entry via the site's /contribute page. Verify:
- Browser redirects to `/contribute/?submitted=true` with the success message
- A GitHub Issue appears under the Issues tab with the correct title and label

## Updating the issue format

Edit `worker.js` and redeploy with `wrangler deploy`. No GitHub Actions involved —
the Worker talks to the GitHub Issues API directly.
