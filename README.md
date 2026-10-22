# Eastern Range Weather Ops Hub

One page that links every in-house weather tool built for Eastern Range operations, grouped by category, with tester feedback.

Live site: `https://<your-github-user>.github.io/ER_Weather_Ops_Hub/`

## Files

| File | What it is |
|---|---|
| `index.html` | The hub page. You shouldn't need to touch it. |
| `tools.json` | The list of categories and tools. **This is the file you edit.** |
| `.nojekyll` | Tells GitHub Pages to serve the files as-is. |

## Add a tool

**Option A, from the hub:** click **Add a tool**, fill in the form and save. The hub shows the new `tools.json`; click **Copy**, then **Edit tools.json on GitHub**, paste over the contents and commit. If you don't have write access, GitHub opens a pull request for the owner to approve.

**Option B, on GitHub:** open `tools.json`, click the pencil, and add an entry to `tools`:

```json
{
  "id": "upper-winds",
  "name": "Upper-Level Winds Board",
  "icon": "🎯",
  "url": "https://yourname.github.io/UpperWinds/",
  "category": "launch",
  "status": "beta",
  "owner": "",
  "description": "One or two sentences on what it does and when to use it.",
  "tags": ["winds aloft", "GFS"]
}
```

- `id`: short, unique, no spaces.
- `category`: the `id` of an entry in `categories` (add a new category there if you need one).
- `status`: `operational`, `beta`, `development`, `demo` or `planned`.
- `owner`: leave blank to use the GitHub account in the `url` (`yourname.github.io/...` or `github.com/yourname/...`). Fill it in to override, e.g. for a tool hosted somewhere else.

Changes go live about a minute after you commit. Reload the hub to see them.

## Feedback

On GitHub Pages, **Post as GitHub issue** opens a pre-filled issue titled `[Feedback] <type>: <tool>`. Testers need a GitHub account that can see this repo. To get automatic labels, create `feedback`, `bug`, `idea`, `works` and `question` labels under **Issues → Labels** (labels are applied only for people with triage access; everyone else's issues are still findable by the `[Feedback]` title).

The hub figures out the repo from its own address. If you host it on a custom domain, set `"repo": "owner/ER_Weather_Ops_Hub"` (and `"branch"` if it isn't `main`) at the top of `tools.json`.
