# CLAUDE.md

## Project

- **Name**: AI-Note-Taker
- **Description**: Meeting Recorder
- **Type**: API / CLI / Library / ML-Training / Full-stack
- **Status**: Active development

## Default Stack (for new projects)

When starting a new project with no existing code, use these defaults:

- **Language**: Python 3.11+
- **API framework**: FastAPI + Pydantic v2
- **Database ORM**: SQLAlchemy (async)
- **Vector DB**: ChromaDB (swap to Pinecone/Qdrant if specified)
- **LLM framework**: LangChain (swap to LlamaIndex if specified)
- **Async HTTP**: httpx (not requests)
- **Logging**: loguru (not print or stdlib logging)
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Linting/Formatting**: ruff (not black, flake8, or isort separately)
- **Package manager**: miniconda (conda + pip); one conda env per project
- **Containerization**: Docker, docker-compose

For existing projects, discover the stack from project files (`environment.yml`, imports, `pyproject.toml`) instead.

## New Project Bootstrap

When starting from an empty folder, execute these steps in order:

```bash
# 1. Check if an environment is already available for this project, if Not, then Create conda environment
conda create -n ai-note-taker python=3.11 -y
conda activate ai-note-taker

# 2. Initialize git
git init
echo "__pycache__/\n.env\n*.pyc\n.mypy_cache/\n.pytest_cache/\n.ruff_cache/\ndist/\n*.egg-info/\ndata/\nresults/\nreports/\ntasks/" > .gitignore

# 3. Check if an environment is already available for this project, if Not, then Create GitHub repo and link remote
gh repo create AI Note Taker --private --source=. --push

# 4. Scaffold project structure (see Project Structure section)
# 5. Install initial dependencies as you build
# 6. First commit
git add .
git commit -m "feat: initial project scaffold"
git push -u origin main
```

After bootstrap, follow the normal Workflow for all subsequent work.

## Commands

```bash
# Environment Setup (new project — no environment.yml exists yet)
conda create -n ai-note-taker python=3.11 -y
conda activate ai-note-taker

# Environment Setup (existing project — environment.yml exists)
conda env create -f environment.yml
conda activate ai-note-taker

# Dev
uvicorn app.main:app --reload --port 8000

# Test
pytest -xvs                          # verbose, stop on first failure
pytest --cov=src --cov-report=term   # with coverage

# Lint & Format
ruff check . --fix
ruff format .

# Type check
mypy src/ --ignore-missing-imports

# Dependency Installation (during development)
conda install -c conda-forge [package]   # prefer conda-forge
pip install [package]                    # fallback if not in conda

# Dependency Export (end of session / before commit)
pip freeze > requirements.txt
conda env export --no-builds > environment.yml
```

## Workflow

The workflow is split into three sequential modes. Complete each mode fully before moving to the next.

### Phase 0 — Environment Setup

If no conda env exists for this project, create one. If `environment.yml` exists, use it; otherwise create a fresh env with Python 3.11.

---

### Phase 1 — Plan Mode

> Goal: Understand the problem, design the approach, and get approval before writing any code.

1. Read the relevant code and understand the current state of the codebase.
2. Think through the problem. Write a detailed plan in `tasks/todo.md` as a checklist of todo items.
3. Each item should be small, specific, and independently completable.
4. Check in with me before starting work — I will verify and approve the plan.

---

### Phase 2 — Build Mode

> Goal: Implement the plan step by step, committing after every successful change.

5. Complete the todos one by one, marking them off as you go.
6. At every step, give me a high-level explanation of what you changed.
7. Keep every change simple and minimal. Avoid big rewrites.
8. Write tests for every new feature or change (`pytest -xvs`). Do not consider a step complete until its tests pass.
9. Run linting and formatting after each step: `ruff check . --fix && ruff format .`
10. **Commit the code to Git after each successful step.** Use conventional commit messages. Do not batch multiple steps into a single commit.
11. Install dependencies on-the-fly as needed (`conda install` first, `pip install` as fallback).
12. At the end of Build Mode, export dependencies: `pip freeze > requirements.txt` and `conda env export --no-builds > environment.yml`.

---

### Phase 3 — Secure Mode

> Goal: Audit the code you just wrote for security vulnerabilities and best practices.

13. Go through the code you just wrote and confirm it follows security best practices. Check that no sensitive data is left in the frontend, and that there are no vulnerabilities an attacker could exploit.
14. Run the full test suite (`pytest --cov=src --cov-report=term`) and confirm all tests pass with adequate coverage.
15. Run type checking: `mypy src/ --ignore-missing-imports`.
16. If any issues are found, fix them immediately and commit the fix.

---

### Phase 4 — Explain Mode

> Goal: Teach and document what was built.

17. Explain the functionality and code you just built in detail with visually appealing diagrams. Walk me through what you changed and how it works. Act like you are a senior engineer teaching me.
18. Add a review section in `tasks/todo.md` summarizing the changes in detail and add diagrams and figures wherever needed.

## Coding Standards

- Type hints on all function signatures and return types.
- Docstrings on all public functions (Google style).
- Async by default for I/O-bound operations.
- Pydantic models for all API request/response schemas.
- Repository pattern for data access; business logic in service layer.
- Environment variables via `pydantic-settings`; never hardcode secrets.
- Use `pathlib.Path` over `os.path`.
- Imports: stdlib → third-party → local (ruff handles ordering).

## Error Handling

- Custom exception classes inheriting from a base `AppError`.
- FastAPI exception handlers for consistent JSON error responses.
- Always log errors with context before re-raising.
- Never use bare `except:` — catch specific exceptions.

## Testing

- Every new feature needs tests before it's complete.
- Test file naming: `test_{module_name}.py` in `tests/` mirroring `src/` structure.
- Use fixtures in `conftest.py`; avoid test interdependence.
- Mock external services; never call real APIs in unit tests.
- Minimum coverage target: 80%.

## Git

- Commit messages: conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`).
- One logical change per commit.
- Branch naming: `feat/short-description`, `fix/short-description`.
- Do NOT commit `.env`, secrets, or large data files.
- GitHub CLI (`gh`) is available. Use it for repo creation, PRs, and issue management.
- Default repo visibility: **private** (unless I specify otherwise).

## Project Structure

```
project-root/
├── CLAUDE.md
├── README.md
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── environment.yml           # conda environment definition
├── .env.example
├── docker-compose.yml
├── data/                     # datasets (git-ignored)
│   └── README.md             # describes how to obtain/download the data
├── results/                  # generated outputs: images, plots, metrics (git-ignored)
│   └── README.md             # describes what outputs to expect
├── reports/                  # assignment reports and generated docs (git-ignored)
│   └── README.md             # describes what reports are generated
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Settings via pydantic-settings
│   ├── models/               # SQLAlchemy / domain models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── routers/              # FastAPI route handlers
│   ├── services/             # Business logic layer
│   ├── repositories/         # Data access layer
│   └── utils/                # Shared utilities
├── tests/
│   ├── conftest.py
│   └── ...
├── tasks/                    # task tracking and plans (git-ignored)
│   └── todo.md               # Active task tracking
└── docs/
    └── architecture.md       # High-level design decisions
```

**Git-ignored folders:** `data/`, `results/`, `reports/`, and `tasks/` must be in `.gitignore`. Only their `README.md` files are committed (use `git add -f data/README.md results/README.md reports/README.md`).

## Forbidden Patterns

- Do NOT commit datasets (`data/`), generated outputs (`results/`), reports (`reports/`), or task files (`tasks/`) to git.
- Do NOT use `print()` for logging; use `loguru`.
- Do NOT use `requests` for async code; use `httpx` with async client.
- Do NOT install packages globally; always install inside the project's conda env.
- Do NOT forget to export dependencies at end of session.
- Do NOT delete or overwrite existing tests without explicit approval.
- Do NOT use wildcard imports (`from module import *`).
- Do NOT store state in global mutable variables.

## When Stuck

- If a task is ambiguous, ask me before guessing.
- If you encounter an error you can't resolve in 2 attempts, show me the error and what you tried.
- For complex design decisions, propose 2-3 options with trade-offs; let me choose.
- For domain-specific questions, check `docs/` first; ask me if not documented.

## Notes

<!-- Add project-specific notes below this line -->
