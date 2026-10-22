"""Apply a hub change described in a GitHub issue to tools.json.

Accepts either the ```json block the hub writes, or the "Add a tool" issue form.
Writes result/summary to $GITHUB_OUTPUT and a reply for the issue to /tmp/hub_reply.md.
"""
import json, os, re, sys, unicodedata

TOOLS = "tools.json"
STATUSES = {"operational": "Operational", "beta": "Beta", "development": "In development",
            "demo": "Demo", "planned": "Planned"}
TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}

body = os.environ.get("ISSUE_BODY") or ""
author = os.environ.get("ISSUE_AUTHOR", "")
trusted = os.environ.get("AUTHOR_ASSOC", "") in TRUSTED
collab_only = (os.environ.get("COLLABORATORS_ONLY") or "").lower() == "true"


class Reject(Exception):
    pass


def finish(ok, summary, reply):
    with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
        f.write(f"result={'ok' if ok else 'error'}\n")
        f.write("summary=" + summary.replace("\n", " ")[:120] + "\n")
    with open("/tmp/hub_reply.md", "w") as f:
        f.write(reply + "\n")
    print(summary)
    sys.exit(0)


def clean(v, limit, field):
    v = "" if v is None else str(v)
    v = "".join(ch for ch in v if unicodedata.category(ch)[0] != "C" or ch in "\n")
    v = v.strip()
    if len(v) > limit:
        raise Reject(f"{field} is too long (limit {limit} characters).")
    return v


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:32]
    return s or "item"


def unique_id(base, data):
    taken = {t["id"] for t in data["tools"]} | {c["id"] for c in data["categories"]}
    i, cand = 2, slug(base)
    while cand in taken:
        cand = f"{slug(base)}-{i}"
        i += 1
    return cand


def parse_body(text):
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError as e:
            raise Reject(f"The change block isn't valid JSON ({e.msg}). Edit the issue to fix it.")
    # Issue form: "### Label\n\nvalue"
    fields = {}
    for label, value in re.findall(r"^###\s+(.+?)\s*\n+(.*?)(?=^###\s|\Z)", text, re.S | re.M):
        value = value.strip()
        fields[label.strip().lower()] = "" if value == "_No response_" else value
    if not fields.get("tool name"):
        raise Reject("I couldn't find a tool in this issue. Use the hub's Add a tool button or the Add a tool issue form.")
    status_label = fields.get("status", "Beta").lower()
    status = next((k for k, v in STATUSES.items() if v.lower() == status_label), "beta")
    return {"action": "add", "tool": {
        "name": fields.get("tool name"), "url": fields.get("link", ""), "icon": fields.get("icon", ""),
        "description": fields.get("what it does", ""), "category": fields.get("category", ""),
        "status": status, "owner": fields.get("owner", ""),
        "tags": [t.strip() for t in fields.get("tags", "").split(",") if t.strip()]}}


def clean_tool(raw, data, new_category=None):
    if not isinstance(raw, dict):
        raise Reject("The change has no tool details.")
    name = clean(raw.get("name"), 80, "Name")
    if not name:
        raise Reject("The tool needs a name.")
    url = clean(raw.get("url"), 300, "Link")
    if url and not re.match(r"^https?://[^\s]+$", url, re.I):
        raise Reject("The link needs to start with https:// or http://.")
    status = raw.get("status") or "beta"
    if status not in STATUSES:
        raise Reject(f"Status must be one of: {', '.join(STATUSES)}.")
    cat = clean(raw.get("category"), 60, "Category")
    cat_ids = {c["id"] for c in data["categories"]}
    if new_category and cat == new_category["id"]:
        pass
    elif cat not in cat_ids:
        by_name = {c["name"].lower(): c["id"] for c in data["categories"]}
        if cat.lower() in by_name:
            cat = by_name[cat.lower()]
        else:
            raise Reject(f"There's no category called \"{cat}\". Pick one of: "
                         + ", ".join(c["name"] for c in data["categories"]) + ".")
    tags = raw.get("tags") or []
    if not isinstance(tags, list):
        tags = [t.strip() for t in str(tags).split(",")]
    tags = [clean(t, 30, "Each tag") for t in tags if str(t).strip()][:8]
    return {"name": name, "icon": clean(raw.get("icon"), 8, "Icon"), "url": url, "category": cat,
            "status": status, "owner": clean(raw.get("owner"), 60, "Owner"),
            "description": clean(raw.get("description"), 400, "Description"), "tags": tags}


def clean_category(raw, data, existing_id=None):
    name = clean(raw.get("name"), 40, "Category name")
    if not name:
        raise Reject("The category needs a name.")
    color = (raw.get("color") or "#8392A8").strip()
    if not re.match(r"^#[0-9a-fA-F]{6}$", color):
        raise Reject("Category color must look like #4FA3E0.")
    for c in data["categories"]:
        if c["name"].lower() == name.lower() and c["id"] != existing_id:
            raise Reject(f"A category called \"{c['name']}\" already exists.")
    return {"name": name, "color": color, "blurb": clean(raw.get("blurb"), 120, "Category description")}


def can_change(tool):
    return trusted or (author and tool.get("addedBy") == author)


def main():
    if collab_only and not trusted:
        raise Reject("This hub only accepts changes from repo collaborators. Ask the owner to add you.")
    with open(TOOLS, encoding="utf-8") as f:
        data = json.load(f)
    ch = parse_body(body)
    action = ch.get("action")
    tools = data["tools"]

    if action == "add":
        newcat = None
        if ch.get("newCategory"):
            newcat = clean_category(ch["newCategory"], data)
            newcat["id"] = unique_id(newcat["name"], data)
            ch.setdefault("tool", {})["category"] = newcat["id"]
            data["categories"].append(newcat)
        tool = clean_tool(ch.get("tool"), data, newcat)
        if any(t["name"].lower() == tool["name"].lower() for t in tools):
            raise Reject(f"\"{tool['name']}\" is already on the hub. Use Edit on its tile instead.")
        tool = {"id": unique_id(tool["name"], data), **tool, "addedBy": author}
        tools.append(tool)
        summary = f"Hub: add {tool['name']}"
        reply = f"✅ Added **{tool['name']}**. It'll show on the hub in about a minute."

    elif action == "update":
        t = next((x for x in tools if x["id"] == ch.get("id")), None)
        if not t:
            raise Reject("That tool isn't on the hub anymore.")
        if not can_change(t):
            raise Reject(f"Only repo collaborators or the person who added **{t['name']}** can edit it.")
        newcat = None
        if ch.get("newCategory"):
            newcat = clean_category(ch["newCategory"], data)
            newcat["id"] = unique_id(newcat["name"], data)
            ch.setdefault("tool", {})["category"] = newcat["id"]
            data["categories"].append(newcat)
        new = clean_tool(ch.get("tool"), data, newcat)
        if any(x["name"].lower() == new["name"].lower() and x["id"] != t["id"] for x in tools):
            raise Reject(f"Another tool is already called \"{new['name']}\".")
        t.update(new)
        summary = f"Hub: edit {t['name']}"
        reply = f"✅ Updated **{t['name']}**. The change shows in about a minute."

    elif action == "delete":
        t = next((x for x in tools if x["id"] == ch.get("id")), None)
        if not t:
            raise Reject("That tool is already gone.")
        if not can_change(t):
            raise Reject(f"Only repo collaborators or the person who added **{t['name']}** can delete it.")
        data["tools"] = [x for x in tools if x["id"] != t["id"]]
        summary = f"Hub: remove {t['name']}"
        reply = f"✅ Removed **{t['name']}** from the hub."

    elif action in ("update-category", "delete-category"):
        if not trusted:
            raise Reject("Only repo collaborators can change categories.")
        c = next((x for x in data["categories"] if x["id"] == ch.get("id")), None)
        if not c:
            raise Reject("That category isn't on the hub anymore.")
        if action == "delete-category":
            if any(t["category"] == c["id"] for t in tools):
                raise Reject(f"Move or delete the tools in **{c['name']}** first.")
            data["categories"] = [x for x in data["categories"] if x["id"] != c["id"]]
            summary, reply = f"Hub: remove category {c['name']}", f"✅ Removed the **{c['name']}** category."
        else:
            c.update(clean_category(ch.get("category") or {}, data, c["id"]))
            order = ch.get("order")
            ids = [x["id"] for x in data["categories"]]
            if isinstance(order, list) and sorted(order) == sorted(ids):
                data["categories"].sort(key=lambda x: order.index(x["id"]))
            summary, reply = f"Hub: edit category {c['name']}", f"✅ Updated the **{c['name']}** category."
    else:
        raise Reject("I don't recognize that change. Use the buttons on the hub to make one.")

    with open(TOOLS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    finish(True, summary, reply)


try:
    main()
except Reject as e:
    finish(False, "Hub change rejected", f"⚠️ {e}\n\nEdit this issue to fix it and I'll try again.")
