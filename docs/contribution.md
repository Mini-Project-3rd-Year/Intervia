# Intervia — Git & GitHub Workflow

> **Read this before writing a single line of code.**  
> Following this workflow keeps `main` always deployable and makes code reviews fast.

---

## 👥 Team

| Member | Role | GitHub Handle |
|--------|------|---------------|
| Sanskruti | AI Agents · Backend · 3D Avatar | `@sanskruti` |
| Teammate B | Frontend UI / Pages | `@teammate-b` |
| Teammate C | Auth · Database · DevOps | `@teammate-c` |
| Teammate D | Voice · Analytics · History | `@teammate-d` |

> Update the handles above with real GitHub usernames.

---

## 🌿 Branch Strategy

```
main                  ← always stable, always deployable
│
├── feature/issue-3-resume-intelligence-backend
├── feature/issue-4-resume-upload-ui
├── feature/issue-8-langgraph-interview-agent
├── fix/vite-hmr-refresh-runtime
└── chore/update-dependencies
```

### Branch Types

| Prefix | Use for |
|--------|---------|
| `feature/` | New feature from a GitHub issue |
| `fix/` | Bug fix |
| `chore/` | Dependency updates, config changes, refactoring |
| `docs/` | Documentation only |

### Branch Naming Convention

```
<type>/issue-<number>-<short-description>
```

**Examples:**
```bash
feature/issue-1-auth-backend
feature/issue-4-resume-upload-ui
feature/issue-8-langgraph-interview-agent
fix/issue-99-websocket-disconnect-crash
chore/upgrade-vite-v9
docs/api-endpoint-reference
```

> ⚠️ **Rules:**
> - All lowercase, words separated by hyphens
> - Always include the issue number
> - No spaces, no slashes in the description part

---

## 🔄 Step-by-Step Daily Workflow

### Step 1 — Get assigned to an issue

1. Go to the **[Issues tab](https://github.com/Mini-Project-3rd-Year/Intervia/issues)**
2. Find your assigned issue (or pick an unassigned one and assign yourself)
3. Read the entire issue — tasks, acceptance criteria, and file paths
4. Leave a comment: `"Starting work on this 🚀"` so teammates know

---

### Step 2 — Sync your local `main` before creating a branch

> **Do this every single time before starting new work.**

```bash
# 1. Switch to main
git checkout main

# 2. Pull latest changes from GitHub
git pull origin main
```

---

### Step 3 — Create your feature branch FROM main

```bash
# Replace with your actual issue number and description
git checkout -b feature/issue-3-resume-intelligence-backend
```

Verify you are on the right branch:
```bash
git branch
# Should show: * feature/issue-3-resume-intelligence-backend
```

---

### Step 4 — Do your work

- Write code, follow the tasks in the issue checklist
- Make **small, focused commits** as you go (don't wait until the end)
- Each commit should do one clear thing

#### Commit Message Format

```
<type>(<scope>): <short description>

<optional longer explanation>
```

**Types:** `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `style`

**Examples:**
```bash
git commit -m "feat(resume): add PDF text extraction using PyMuPDF"
git commit -m "feat(resume): implement ResumeAgent with structured output"
git commit -m "feat(api): add POST /api/v1/resumes endpoint"
git commit -m "test(resume): add fixture PDF and test for resume parsing"
git commit -m "fix(resume): handle empty PDF pages without crashing"
git commit -m "docs(resume): add docstrings to ResumeAgent.run()"
```

> ✅ Good commit: `"feat(auth): add JWT token verification dependency"`  
> ❌ Bad commit: `"changes"`, `"wip"`, `"stuff"`, `"fix"`

---

### Step 5 — Push your branch to GitHub regularly

Push at the end of every work session (or anytime you want a cloud backup):

```bash
# First push (creates the branch on GitHub)
git push -u origin feature/issue-3-resume-intelligence-backend

# Subsequent pushes on the same branch
git push
```

> Push frequently — if your laptop dies, your work is safe on GitHub.

---

### Step 6 — Keep your branch up to date with main

If other teammates merge their work while you're working, you need to pull those changes into your branch to avoid conflicts later.

Do this **at least once a day**:

```bash
# 1. Make sure your current work is committed
git status          # should be clean, or stash it:
git stash           # saves uncommitted changes temporarily

# 2. Pull latest main
git fetch origin
git rebase origin/main
# (or: git merge origin/main — both work, rebase gives cleaner history)

# 3. If you stashed, restore your work
git stash pop
```

If you see merge conflicts during rebase — see the **Resolving Conflicts** section below.

---

### Step 7 — Open a Pull Request (PR)

When your issue is done (all checkboxes ticked, acceptance criteria met):

1. Push your final commits:
   ```bash
   git push
   ```

2. Go to **GitHub → your repo → Pull Requests → New Pull Request**

3. Set:
   - **Base:** `main`
   - **Compare:** your feature branch

4. Fill in the PR template:

```markdown
## What this PR does
Implements the Resume Intelligence backend (Issue #3).
- PDF parsing via PyMuPDF
- ResumeAgent with Gemini structured output
- POST /api/v1/resumes endpoint
- Input validation (PDF only, max 10MB)

## Closes
Closes #3

## Checklist
- [x] All issue tasks completed
- [x] Tests written and passing (pytest tests/ -v)
- [x] No secrets or .env files committed
- [x] Code follows project conventions

## Screenshots / Evidence
(paste a curl response, test output, or screenshot if relevant)
```

5. **Assign a reviewer** — at minimum, assign Sanskruti (project lead)
6. **Link the issue**: in the PR body write `Closes #3` — GitHub will auto-close the issue when the PR merges

---

### Step 8 — Code Review

**As a reviewer:**
- Pull the branch and test it locally if it's a significant change
- Leave comments on specific lines if something needs changing
- Approve if everything looks good, or request changes

**As the author:**
- Address every comment
- Push fixes to the same branch (the PR updates automatically)
- Reply to each comment with `"Done ✅"` or explain why you disagree
- Don't merge your own PR — wait for approval

---

### Step 9 — Merge to main

Once the PR is approved:

1. Click **"Squash and merge"** (preferred) or **"Merge pull request"**
   - Squash and merge = all your commits become one clean commit on `main`
2. **Delete the feature branch** after merging (GitHub shows a button — click it)
3. The linked issue closes automatically (because of `Closes #3` in the PR)

---

### Step 10 — Clean up locally

After your PR is merged:

```bash
# Switch back to main
git checkout main

# Pull the merged changes
git pull origin main

# Delete your local branch (it's already deleted on GitHub)
git branch -d feature/issue-3-resume-intelligence-backend
```

---

## ⚡ Quick Reference Cheatsheet

```bash
# ── START NEW ISSUE ──────────────────────────────────────────
git checkout main
git pull origin main
git checkout -b feature/issue-<N>-<description>

# ── DURING WORK ──────────────────────────────────────────────
git add .
git commit -m "feat(<scope>): <what you did>"
git push                          # or: git push -u origin <branch> (first time)

# ── STAY UP TO DATE WITH MAIN ────────────────────────────────
git fetch origin
git rebase origin/main

# ── OPEN PR ──────────────────────────────────────────────────
git push
# → Go to GitHub and open PR from your branch to main

# ── AFTER PR IS MERGED ───────────────────────────────────────
git checkout main
git pull origin main
git branch -d feature/issue-<N>-<description>
```

---

## 🚨 Golden Rules

| # | Rule |
|---|------|
| 1 | **Never commit directly to `main`** — always use a feature branch |
| 2 | **Never force-push to `main`** (`git push --force` on main is forbidden) |
| 3 | **Never commit `.env`** — it is in `.gitignore` for a reason |
| 4 | **One issue = one branch = one PR** — don't mix multiple issues in one branch |
| 5 | **Always pull main before creating a new branch** |
| 6 | **All tests must pass** before opening a PR |
| 7 | **Write a meaningful commit message** — your teammates read them |
| 8 | **Link your PR to the issue** using `Closes #N` |

---

## 🔧 Resolving Merge Conflicts

Conflicts happen when two people edit the same lines. Don't panic.

```bash
# During a rebase, if you see:
# CONFLICT (content): Merge conflict in backend/app/main.py

# 1. Open the file — look for conflict markers:
<<<<<<< HEAD
your changes here
=======
teammate's changes here
>>>>>>> origin/main

# 2. Edit the file to keep the correct code (combine both if needed)
# 3. Remove ALL the conflict markers (<<<, ===, >>>)

# 4. Stage the resolved file
git add backend/app/main.py

# 5. Continue the rebase
git rebase --continue
```

If things get messy and you want to start over:
```bash
git rebase --abort    # goes back to where you were before the rebase
```

**Best practice to avoid conflicts:**
- Work on different files from your teammates when possible (issues are designed this way)
- Rebase on `main` daily so conflicts are small and easy to fix
- Communicate in the team group chat before editing shared files like `App.tsx` or `main.py`

---

## 🏷️ Using GitHub Issue Checkboxes

Each issue has a task checklist. As you complete tasks, **check them off directly on GitHub**:

1. Open the issue on GitHub
2. Click the **checkbox** next to a completed task
3. This updates the progress bar shown on the Issues list

This lets everyone see what's done at a glance without asking.

---

## 📌 Labels Reference

When creating or updating issues, use these labels:

| Label | Color | Use for |
|-------|-------|---------|
| `backend` | 🔵 Blue | FastAPI, Python, database |
| `frontend` | 🟣 Purple | React, TypeScript, UI |
| `ai` | 🟡 Amber | LLM agents, LangGraph, RAG |
| `priority: critical` | 🔴 Red | Blocking other work |
| `priority: high` | 🟠 Orange | Must be done this sprint |
| `priority: medium` | 🟢 Green | Normal priority |
| `in progress` | 🔷 Teal | Someone is actively working on this |
| `needs review` | 🟡 Yellow | PR is open, waiting for review |
| `blocked` | ⬛ Gray | Cannot proceed until another issue is done |

---

## 🔔 Communication

- When you **start** an issue → comment on it and add `in progress` label
- When you **open a PR** → post the PR link in the team chat
- When you're **blocked** → comment on the issue and add `blocked` label, then message the team
- When you **need a review** → tag the reviewer in the PR and in chat

---

*Following this workflow consistently means no lost work, no broken `main`, and smooth collaboration across all 4 teammates. 🚀*
