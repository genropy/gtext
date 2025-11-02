# Reporting Use Case

Examples of using gtext for dynamic report generation.

## Daily Status Report

````markdown
# Daily Status Report

**Date**: ```include
cli: date +"%Y-%m-%d"
```

## Git Activity

```include
cli: git log --since="24 hours ago" --pretty=format:"- %h %s" --no-merges
```

## Test Results

```include
cli: pytest --tb=no -q
```

## Code Coverage

```include
cli: pytest --cov --cov-report=term-missing | tail -20
```
````

## Weekly Summary

````markdown
# Weekly Summary

**Week**: ```include
cli: date +"%Y-W%V"
```

## Commits This Week

```include
cli: git log --since="1 week ago" --oneline | wc -l
``` commits

## Top Contributors

```include
cli: git shortlog -sn --since="1 week ago" | head -5
```

## Files Changed

```include
cli: git diff --stat HEAD~7..HEAD
```
````

## System Monitoring

````markdown
# System Status

**Generated**: ```include
cli: date
```

## Disk Usage

```include
cli: df -h
```

## Memory Usage

```include
cli: free -h
```

## Top Processes

```include
cli: ps aux --sort=-%mem | head -10
```
````

## Database Report

**Script** (`scripts/db_stats.py`):

```python
#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# Table stats
cursor.execute("""
    SELECT name, COUNT(*) as count
    FROM sqlite_master
    WHERE type='table'
""")

print("## Tables\n")
for name, count in cursor.fetchall():
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    rows = cursor.fetchone()[0]
    print(f"- **{name}**: {rows} rows")
```

**Report** (`db-report.md.gtext`):

````markdown
# Database Report

```include
cli: python scripts/db_stats.py
```
````

## Sales Dashboard

````markdown
# Sales Dashboard

**Period**: ```include
cli: date +"%B %Y"
```

## Total Sales

```include
cli: python scripts/sales_total.py --month current
```

## Top Products

```include
cli: python scripts/top_products.py --limit 10 --format markdown
```

## Regional Breakdown

```include
cli: python scripts/sales_by_region.py --format table
```
````

## CI/CD Pipeline Report

````markdown
# Pipeline Status

**Build**: ```include
cli: cat .build-number
```

## Test Results

```include
cli: cat test-results.txt
```

## Deployment Status

```include
cli: kubectl get pods -n production
```

## Recent Releases

```include
cli: git tag --sort=-creatordate | head -5
```
````

## Performance Report

````markdown
# Performance Metrics

## Load Times

```include
cli: python scripts/measure_load_times.py
```

## Response Times

```include
cli: python scripts/analyze_logs.py --metric response-time
```

## Error Rates

```include
cli: python scripts/error_rate.py --last 24h
```
````

## Next Steps

- [Documentation examples](documentation.md)
- [Code examples](code.md)
