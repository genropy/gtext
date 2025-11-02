# Code Management Use Case

Examples of using gtext for code generation and management.

## License Headers

### Problem

Add license headers to all source files.

### Solution

**License template** (`templates/license-header.py`):

```python
# Copyright (c) 2024 Your Company
# Licensed under MIT License
# See LICENSE file for details
```

**Source file** (`src/module.py.gtext`):

```python
```include
../templates/license-header.py
```

"""Module documentation."""

def my_function():
    pass
```

**Generate:**

```bash
gtext cast-all src/**/*.py.gtext
```

## Shared Imports

### Problem

Many files need the same imports.

### Solution

**Common imports** (`templates/common-imports.py`):

```python
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
```

**Source file** (`src/processor.py.gtext`):

````python
```include
../templates/common-imports.py
```

class Processor:
    def process(self, data: List[Dict]) -> Optional[Any]:
        logger.info("Processing data")
        # Implementation
````

## Generated Code

### Problem

Generate boilerplate code from definitions.

### Solution

**Model definition** (`models.yaml`):

```yaml
models:
  - name: User
    fields:
      - name: id
        type: int
      - name: username
        type: str
      - name: email
        type: str
```

**Generator script** (`scripts/gen_models.py`):

```python
#!/usr/bin/env python3
import yaml
import sys

def generate_model(model):
    fields = "\n    ".join(
        f"{f['name']}: {f['type']}"
        for f in model['fields']
    )
    return f"""
class {model['name']}:
    {fields}
"""

with open("models.yaml") as f:
    data = yaml.safe_load(f)

for model in data['models']:
    print(generate_model(model))
```

**Output file** (`src/models.py.gtext`):

````python
# Auto-generated models - do not edit manually

```include
cli: python scripts/gen_models.py
```
````

## Configuration Files

### Problem

Generate configuration from templates and environment.

### Solution

**Template** (`config.yaml.gtext`):

````yaml
app:
  name: MyApp
  version: ```include
cli: cat VERSION
```
  environment: ```include
cli: echo $ENV
```

database:
  host: ```include
cli: echo $DB_HOST
```
````

**Generate:**

```bash
ENV=production DB_HOST=db.prod.com gtext cast config.yaml.gtext
```

## SQL Schema Generation

### Problem

Generate database schema from definitions.

### Solution

**Schema generator** (`scripts/gen_schema.py`):

```python
#!/usr/bin/env python3
import json

schema = {
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER PRIMARY KEY"},
                {"name": "username", "type": "TEXT NOT NULL"},
                {"name": "email", "type": "TEXT UNIQUE"}
            ]
        }
    ]
}

for table in schema["tables"]:
    columns = ",\n  ".join(
        f"{col['name']} {col['type']}"
        for col in table["columns"]
    )
    print(f"CREATE TABLE {table['name']} (\n  {columns}\n);")
```

**Schema file** (`schema.sql.gtext`):

````sql
-- Auto-generated database schema

```include
cli: python scripts/gen_schema.py
```
````

## Test Fixtures

### Problem

Generate test fixtures from real data.

### Solution

**Fixture generator** (`scripts/gen_fixtures.py`):

```python
#!/usr/bin/env python3
import json

# Fetch real data
users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

print("# Test fixtures")
print()
print("test_users = " + json.dumps(users, indent=2))
```

**Test file** (`tests/fixtures.py.gtext`):

````python
```include
cli: python scripts/gen_fixtures.py
```
````

## API Client Generation

### Problem

Generate API client from OpenAPI spec.

### Solution

**Generator** (`scripts/gen_client.py`):

```python
#!/usr/bin/env python3
import yaml

with open("openapi.yaml") as f:
    spec = yaml.safe_load(f)

for path, methods in spec["paths"].items():
    for method, details in methods.items():
        func_name = details["operationId"]
        print(f"""
def {func_name}(client):
    ''''{details['summary']}'''
    return client.{method}('{path}')
""")
```

**Client file** (`client.py.gtext`):

````python
# Auto-generated API client

class APIClient:
    ```include
cli: python scripts/gen_client.py
```
````

## Next Steps

- See [Documentation examples](documentation.md)
- See [Report examples](reports.md)
