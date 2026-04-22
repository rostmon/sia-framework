# Contributing to SIA Framework

Thank you for your interest in contributing to the Sovereign Systemic Integrity Architecture (SIA) Framework. This document outlines the process for contributing code, documentation, and governance rule packs.

---

## 🚦 Before You Start

1. **Check existing issues** — your feature or bug may already be tracked.
2. **Open an issue first** for significant features or API changes so we can align on design before you invest coding time.
3. **Read the architecture** — understand the [three-layer sovereign stack](README.md#️-architecture-the-sovereign-stack) before adding to the governance pipeline.

---

## 🛠️ Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/sia-framework.git
cd sia-framework

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Verify the install
sia --help
pytest tests/ -v
```

---

## 📋 Contribution Types

### 🐛 Bug Fixes
- Identify the affected article/module in the commit message
- Add a regression test to `tests/test_poc.py` that reproduces the bug
- Submit a PR with a description of the root cause and fix

### ✨ New Features
- Open an issue first to discuss scope and design
- Features that add new EU AI Act article coverage are highest priority
- Include tests in both `tests/test_poc.py` (integration) and `tests/test_phase2.py` (unit)

### 📜 New Governance Rule Packs
- Add YAML rules to `configs/blueprints/` following the naming convention `{industry}_v{n}.yaml`
- Document the regulatory basis for each rule (article reference is mandatory)
- Test using `sia validate` CLI and the `RuleEvaluationEngine` test suite

### 🔌 New Model Adapters
- Inherit from `ModelAdapter` in `src/sia/adapters/base.py`
- Implement `generate()`, `agenerate()`, and `astream()` — all three are required
- Add confidence normalization (logprobs → 0.0–1.0 float)
- Place in `src/sia/adapters/{provider}_adapter.py`
- Add optional dependency in `pyproject.toml` under `[project.optional-dependencies]`

---

## 📐 Code Standards

### Style

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/
```

### Type Hints
- All public API functions must have complete type annotations
- Use `from __future__ import annotations` for forward references

### Docstrings
- All public classes and methods require docstrings
- Cite the EU AI Act article in the docstring where applicable

---

## 🧪 Testing Requirements

All PRs must maintain or improve test coverage.

```bash
# Run full test suite
pytest tests/ -v

# Run specific tests
pytest tests/test_poc.py -v -k "Art.5"

# Run with coverage
pytest tests/ --cov=sia --cov-report=term-missing
```

**Test guidelines:**
- `test_poc.py` — EU AI Act article integration tests (assert on `SIAResponse` fields)
- `test_phase2.py` — Unit tests for individual modules
- New governance rules **must** have a corresponding test case in `test_poc.py`
- Tests must pass with `MockAdapter` — no API keys required in CI

---

## 🏗️ Project Governance

### Priority Order for Development
1. EU AI Act hard compliance (runtime_gate rules — critical path)
2. Audit trail integrity (traceability, ledger)
3. Human oversight mechanisms (HITL, webhooks)
4. Observability and reporting
5. Developer experience (CLI, adapters, docs)

### Non-Negotiable Constraints
- **No secrets in code** — API keys must always be read from environment variables
- **No persistent state in core engine** — The `RuleEvaluationEngine` must be stateless between requests
- **SHA-256 ledger is immutable** — Ledger entries may never be modified or deleted programmatically
- **Deployment assertions must raise `SIAConfigError`** — Never silently pass

---

## 📤 Pull Request Process

1. Ensure all tests pass: `pytest tests/ -v`
2. Format code: `black src/ tests/ && isort src/ tests/`
3. Update `README.md` if you changed the public API
4. Write a clear PR description referencing the issue number
5. PRs are reviewed within 5 business days

---

## 📜 License

By contributing to SIA Framework, you agree that your contributions will be licensed under the [MIT License](LICENSE).
