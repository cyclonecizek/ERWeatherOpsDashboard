# Eastern Range Weather Ops Hub

One page that links every in-house weather tool built for Eastern Range operations, grouped by category, with tester feedback.

Live site: `https://cyclonecizek.github.io/ER_Weather_Ops_Hub/`

## How adding a tool works

Anyone with a GitHub account can add a tool, and nobody has to copy anything by hand:

1. On the hub, click **Add a tool**, fill in the form and click **Continue on GitHub**.
2. GitHub opens a pre-filled issue. Click **Submit new issue**.
3. A GitHub Action checks the entry, adds it to `tools.json`, commits it and closes the issue with a ✅ comment.
4. About a minute later the tool is on the hub for everyone. A hub left open picks up the change by itself.

Editing or deleting a tool, or changing a category, works the same way from the pencil buttons on the hub.

People can also skip the hub and use **Issues → New issue → Add a tool**.

If something's wrong with a submission (bad link, unknown category, duplicate name), the Action leaves the issue open with a ⚠️ comment explaining what to fix. Editing the issue retries it.

### Who can change what

| Change | Who |
|---|---|
| Add a tool | Anyone with a GitHub account |
| Edit or delete a tool | Repo collaborators, or whoever added that tool |
| Edit, reorder or delete categories | Repo collaborators |

To limit everything to collaborators, go to **Settings → Secrets and variables → Actions → Variables** and add `HUB_COLLABORATORS_ONLY` = `true`.

Every change is a commit that names its issue, so anything can be undone from the repo history.

## Files

| File | What it is |
|---|---|
| `index.html` | The hub page |
| `tools.json` | The categories and tools. The Action edits this; you can also edit it by hand. |
| `.github/workflows/hub-from-issue.yml` | The Action that applies `[Hub]` issues |
| `.github/scripts/apply_hub_issue.py` | Validation and editing logic the Action runs |
| `.github/ISSUE_TEMPLATE/add-tool.yml` | The Add a tool issue form |
| `.nojekyll` | Tells GitHub Pages to serve the files as-is |

### Tool fields

- `status`: `operational`, `beta`, `development`, `demo` or `planned`.
- `owner`: leave blank to use the GitHub account in the link (`yourname.github.io/...` or `github.com/yourname/...`).
- `addedBy`: filled in by the Action with the GitHub user who added the tool.

## Feedback

**Post as GitHub issue** opens a pre-filled issue titled `[Feedback] <type>: <tool>`. These are left alone by the Action. Create `feedback`, `bug`, `idea`, `works` and `question` labels under **Issues → Labels** if you want them labeled (labels only apply for people with triage access).

## Setup checklist

- **Settings → Pages:** Deploy from a branch, `main`, `/ (root)`.
- **Settings → Actions → General → Workflow permissions:** if Action runs fail with a permission error on push or comment, choose **Read and write permissions**.
- **Issues** must be turned on (Settings → General → Features).
- If `main` has branch protection that blocks direct pushes, the Action can't commit.
- On a custom domain, set `"repo": "owner/ER_Weather_Ops_Hub"` at the top of `tools.json`.
