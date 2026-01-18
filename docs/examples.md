# Example Rules

This page contains ready-to-use rules for common file organization tasks.

## Download Management

### Sort Downloads by File Type

```yaml
rules:
  - name: "Sort Downloads by File Type"
    locations: ~/Downloads
    filters:
      - extension:
          - pdf
          - doc
          - docx
          - xls
          - xlsx
          - ppt
          - pptx
    actions:
      - move: ~/Documents/Downloads/{extension.upper()}/

  - name: "Sort Downloaded Images"
    locations: ~/Downloads
    filters:
      - extension:
          - jpg
          - jpeg
          - png
          - gif
          - webp
    actions:
      - move: ~/Pictures/Downloads/

  - name: "Sort Downloaded Videos"
    locations: ~/Downloads
    filters:
      - extension:
          - mp4
          - mkv
          - avi
          - mov
    actions:
      - move: ~/Videos/Downloads/
```

### Clean Up Old Downloads

```yaml
rules:
  - name: "Archive old downloads"
    locations: ~/Downloads
    filters:
      - lastmodified:
          days: 30
          mode: older
    actions:
      - move: ~/Downloads/Archive/{lastmodified.year}/{lastmodified.month:02d}/
```

### Remove Incomplete Downloads

```yaml
rules:
  - name: "Remove incomplete downloads"
    locations: ~/Downloads
    filters:
      - extension:
          - crdownload
          - part
          - tmp
    actions:
      - trash
```

## Photo Organization

### Sort Photos by Date Taken

```yaml
rules:
  - name: "Sort photos by EXIF date"
    locations:
      - path: ~/Pictures
        max_depth: null
    filters:
      - extension:
          - jpg
          - jpeg
      - exif: image.datetime
    actions:
      - move: ~/Pictures/Sorted/{exif.image.datetime.year}/{exif.image.datetime.month:02d}/
```

### Organize Screenshots

```yaml
rules:
  - name: "Organize Screenshots"
    locations: ~/Desktop
    filters:
      - name:
          startswith: Screen
      - extension:
          - png
          - jpg
    actions:
      - move: ~/Pictures/Screenshots/{created.year}/
```

### Find and Remove Duplicate Photos

```yaml
rules:
  - name: "Find duplicate photos"
    locations:
      - ~/Pictures
    subfolders: true
    filters:
      - extension:
          - jpg
          - jpeg
          - png
      - duplicate:
          detect_original_by: created
    actions:
      - echo: "Duplicate: {path} (original: {duplicate.original})"
      - trash
```

## Document Management

### Sort Invoices by Date

```yaml
rules:
  - name: "Organize Invoices"
    locations: ~/Downloads
    filters:
      - extension: pdf
      - filecontent: "(?i)invoice|rechnung|facture"
    actions:
      - move: ~/Documents/Invoices/{created.year}/{created.month:02d}/
```

### Organize by PDF Content

```yaml
rules:
  - name: "Sort invoices by vendor"
    locations: ~/Documents/Inbox
    filters:
      - extension: pdf
      - filecontent: "(?P<vendor>Amazon|Apple|Google|Microsoft)"
    actions:
      - move: ~/Documents/Invoices/{filecontent.vendor}/
```

### Archive Old Documents

```yaml
rules:
  - name: "Archive old documents"
    locations:
      - path: ~/Documents
        max_depth: 2
    filters:
      - extension:
          - pdf
          - doc
          - docx
      - lastmodified:
          years: 2
          mode: older
    actions:
      - move: ~/Documents/Archive/{lastmodified.year}/
```

## Desktop Cleanup

### Clean Desktop Files

```yaml
rules:
  - name: "Move files off desktop"
    locations: ~/Desktop
    filters:
      - extension:
          - pdf
          - doc
          - docx
          - txt
    actions:
      - move: ~/Documents/From Desktop/

  - name: "Move images off desktop"
    locations: ~/Desktop
    filters:
      - extension:
          - jpg
          - jpeg
          - png
          - gif
    actions:
      - move: ~/Pictures/From Desktop/
```

### Delete Empty Folders

```yaml
rules:
  - name: "Delete empty folders"
    locations:
      - path: ~/Desktop
        max_depth: null
    targets: dirs
    filters:
      - empty
    actions:
      - delete
```

## Media Organization

### Sort Music Files

```yaml
rules:
  - name: "Organize music files"
    locations: ~/Downloads
    filters:
      - extension:
          - mp3
          - flac
          - m4a
          - wav
    actions:
      - move: ~/Music/Unsorted/
```

### Organize eBooks

```yaml
rules:
  - name: "Sort eBooks"
    locations: ~/Downloads
    filters:
      - extension:
          - epub
          - mobi
          - azw3
          - pdf
      - filecontent: "(?i)chapter|contents|index"
    actions:
      - move: ~/Documents/Books/
```

## Development Files

### Clean Up Build Artifacts

```yaml
rules:
  - name: "Remove Python cache"
    locations:
      - path: ~/Projects
        max_depth: null
    targets: dirs
    filters:
      - name:
          equals: __pycache__
    actions:
      - delete

  - name: "Remove node_modules"
    locations:
      - path: ~/Projects
        max_depth: null
    targets: dirs
    filters:
      - name:
          equals: node_modules
    actions:
      - echo: "Found node_modules: {path}"
      # - delete  # Uncomment to actually delete
```

### Organize Project Archives

```yaml
rules:
  - name: "Archive old project zips"
    locations: ~/Downloads
    filters:
      - extension:
          - zip
          - tar.gz
          - rar
      - size: "> 50 MB"
    actions:
      - move: ~/Documents/Project Archives/
```

## Backup Rules

### Create Backup Copies

```yaml
rules:
  - name: "Backup important files"
    locations: ~/Documents/Important
    subfolders: true
    filters:
      - lastmodified:
          days: 1
          mode: newer
    actions:
      - copy: ~/Backup/Documents/{relative_path}/
```

### Sync to Archive

```yaml
rules:
  - name: "Archive modified files"
    locations:
      - path: ~/Projects
        max_depth: 2
    filters:
      - extension:
          - py
          - js
          - ts
      - lastmodified:
          hours: 24
          mode: newer
    actions:
      - copy: ~/Backup/Code/{today().strftime('%Y-%m-%d')}/{relative_path}/
```

## Advanced Examples

### Using Python Filters

```yaml
rules:
  - name: "Custom Python filter"
    locations: ~/Downloads
    filters:
      - extension: pdf
      - python: |
          # Only match files larger than 1MB with 'report' in the name
          return (
              path.stat().st_size > 1_000_000 and 
              'report' in path.stem.lower()
          )
    actions:
      - move: ~/Documents/Reports/
```

### Conditional Actions with Python

```yaml
rules:
  - name: "Dynamic file organization"
    locations: ~/Downloads
    filters:
      - created
    actions:
      - python: |
          from pathlib import Path
          import shutil
          
          # Create folder based on weekday
          day = created.strftime('%A')
          dest = Path.home() / 'Sorted' / day
          dest.mkdir(parents=True, exist_ok=True)
          
          if not simulate:
              shutil.move(str(path), str(dest / path.name))
          print(f"Would move to: {dest}")
```

### Using Tags for Selective Execution

```yaml
rules:
  - name: "Quick cleanup"
    tags:
      - quick
      - daily
    locations: ~/Downloads
    filters:
      - lastmodified:
          days: 7
    actions:
      - echo: "Recent file: {path.name}"

  - name: "Deep cleanup"
    tags:
      - deep
      - weekly
    locations:
      - path: ~/Downloads
        max_depth: null
    filters:
      - lastmodified:
          days: 30
    actions:
      - move: ~/Downloads/Archive/
```

Run with: `--tags=quick` or `--tags=deep`

## Tips for Creating Rules

1. **Start with simulation**: Always test with F5 first
2. **Use echo for debugging**: Add `- echo: "{path}"` to see matches
3. **Be specific with filters**: Multiple filters = fewer false matches
4. **Use relative paths**: `{relative_path}` preserves folder structure
5. **Handle conflicts**: Set `on_conflict` for move/copy actions
6. **Tag your rules**: Makes it easy to run subsets of rules

## More Resources

- [organize documentation](https://organize.readthedocs.io)
- [Filter reference](https://organize.readthedocs.io/en/latest/filters/)
- [Action reference](https://organize.readthedocs.io/en/latest/actions/)
