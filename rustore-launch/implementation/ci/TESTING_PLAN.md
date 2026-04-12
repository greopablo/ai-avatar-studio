# TESTING PLAN
## AI Avatar Studio

### TEST PYRAMID
```
        /\
       /  \
      /API \        <- Fewer, slower, more thorough
     /------\
    /Integration\  <- Some, testing components together
   /------------\
  /   Unit Tests  \  <- Many, fast, isolated
 /________________\
```

### QUALITY GATES
| Stage | Gate | Tool |
|-------|------|------|
| Lint | No errors | flake8, black, mypy |
| Unit | 80% coverage | pytest, coverage |
| Integration | All pass | pytest |
| Build | Image created | docker |

### TOOLS
- pytest (Python)
- Appium (mobile)
- Allure (reporting)
- GitHub Actions (CI/CD)

### COMMANDS
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# All tests with coverage
pytest --cov=. --cov-report=html
```
