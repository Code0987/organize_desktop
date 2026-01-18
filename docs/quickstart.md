# Quick Start Guide

Get up and running with Organize Desktop in 5 minutes!

## Step 1: Install

```bash
pip install organize-desktop
```

Or install from source:
```bash
git clone https://github.com/your-username/organize-desktop.git
cd organize-desktop
pip install -e .
```

## Step 2: Launch

```bash
organize-desktop
```

## Step 3: Create Your First Rule

1. Click **"Add Rule"** or press `Ctrl+R`
2. Name it: "Sort PDFs"
3. Add location: Click **Add Location** → Select `~/Downloads`
4. Add filter: Click **Add Filter** → Select **Extension** → Enter `pdf`
5. Add action: Click **Add Action** → Select **Move** → Enter `~/Documents/PDFs/`
6. Click **OK**

## Step 4: Test It

1. Press **F5** (Simulate)
2. Check the output log
3. See which files would be moved

## Step 5: Run It

1. Press **F6** (Run)
2. Confirm the action
3. Files are organized!

## What's Next?

- Read the full [User Guide](user_guide.md)
- Explore more [Filters](https://organize.readthedocs.io/en/latest/filters/)
- Learn about [Actions](https://organize.readthedocs.io/en/latest/actions/)
- Check out [Example Rules](examples.md)

## Common Tasks

### Sort Images
```yaml
rules:
  - name: Sort images by type
    locations: ~/Pictures
    filters:
      - extension:
          - jpg
          - png
          - gif
    actions:
      - move: ~/Pictures/Sorted/{extension.upper()}/
```

### Clean Old Downloads
```yaml
rules:
  - name: Move old downloads
    locations: ~/Downloads
    filters:
      - lastmodified:
          days: 30
    actions:
      - move: ~/Downloads/Archive/
```

### Find Duplicates
```yaml
rules:
  - name: Find duplicates
    locations: ~/Documents
    subfolders: true
    filters:
      - duplicate
    actions:
      - echo: "Duplicate: {path}"
```

## Need Help?

- Press **F1** for documentation
- Check the output log for errors
- Visit the [GitHub Issues](https://github.com/your-username/organize-desktop/issues)
