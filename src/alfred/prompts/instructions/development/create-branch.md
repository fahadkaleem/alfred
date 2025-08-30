# Create Feature Branch

Set up a Git branch for your development work on task {{ task_id }}.

## Prerequisites
- Task should be assigned to you
- Task should be in "In Progress" or similar active status
- You should be in the project repository

## Branch Naming Convention

Follow your team's branch naming convention. Common patterns:
- `feature/TASK-ID` - for new features
- `bugfix/TASK-ID` - for bug fixes
- `hotfix/TASK-ID` - for urgent fixes
- `chore/TASK-ID` - for maintenance tasks

## Steps

### 1. Ensure Clean Working Directory
```bash
# Check current status
git status

# If you have uncommitted changes, stash them
git stash push -m "WIP: Stashing before creating {{ task_id }} branch"
```

### 2. Update Main Branch
```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main
```

### 3. Create Feature Branch
```bash
# Create and switch to new branch
git checkout -b feature/{{ task_id }}

# Verify you're on the new branch
git branch --show-current
```

### 4. Push Branch to Remote
```bash
# Push the branch and set upstream
git push -u origin feature/{{ task_id }}
```

### 5. Verify Setup
```bash
# Confirm branch tracking
git branch -vv

# Should show something like:
# * feature/{{ task_id }}  abc1234 [origin/feature/{{ task_id }}] Initial branch
```

## Best Practices

1. **Branch from main/master**: Always create feature branches from the latest main
2. **Keep branches focused**: One task = one branch
3. **Regular commits**: Commit work frequently with clear messages
4. **Reference task ID**: Include {{ task_id }} in commit messages
5. **Push regularly**: Don't let work accumulate locally

## Commit Message Format
```
{{ task_id }}: Brief description of change

Longer explanation if needed.
```

## If Things Go Wrong

### Branch already exists locally
```bash
# Delete local branch and recreate
git branch -D feature/{{ task_id }}
git checkout -b feature/{{ task_id }}
```

### Branch already exists remotely
```bash
# Fetch and checkout existing branch
git fetch origin
git checkout -t origin/feature/{{ task_id }}
```

### Need to switch branches with uncommitted work
```bash
# Stash your changes
git stash push -m "WIP: {{ task_id }}"

# Switch branches
git checkout other-branch

# Later, return and apply stash
git checkout feature/{{ task_id }}
git stash pop
```

## Next Steps

After creating your branch:
1. Make your code changes
2. Commit regularly with descriptive messages
3. Push changes to keep remote updated
4. Open a pull request when ready for review

Remember: The branch name will appear in pull requests and git history, so keep it professional and descriptive.