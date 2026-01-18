#!/bin/bash
# Quality check script for development

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "${GREEN}==>${NC} $1"
}

echo_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Change to backend directory
cd "$(dirname "$0")/../backend" || exit 1

case "${1:-check}" in
    format)
        echo_step "Running Black formatter..."
        uv run black .
        echo_step "Running Ruff formatter..."
        uv run ruff format .
        echo_step "Sorting imports with Ruff..."
        uv run ruff check --select I --fix .
        ;;

    lint)
        echo_step "Running Ruff linter..."
        uv run ruff check .
        ;;

    lint-fix)
        echo_step "Running Ruff linter with auto-fix..."
        uv run ruff check --fix .
        ;;

    type)
        echo_step "Running mypy type checker..."
        uv run mypy .
        ;;

    test)
        echo_step "Running pytest with coverage..."
        uv run pytest
        ;;

    check)
        echo_step "Running all quality checks..."
        echo ""

        echo_step "1. Checking code formatting..."
        if uv run black --check .; then
            echo -e "${GREEN}✓ Black formatting passed${NC}"
        else
            echo_error "Black formatting failed. Run: ./scripts/quality.sh format"
            exit 1
        fi

        echo ""
        echo_step "2. Running linter..."
        if uv run ruff check .; then
            echo -e "${GREEN}✓ Ruff linting passed${NC}"
        else
            echo_error "Ruff linting failed. Run: ./scripts/quality.sh lint-fix"
            exit 1
        fi

        echo ""
        echo_step "3. Running type checker..."
        if uv run mypy .; then
            echo -e "${GREEN}✓ Type checking passed${NC}"
        else
            echo_warning "Type checking found issues"
        fi

        echo ""
        echo_step "4. Running tests..."
        if uv run pytest; then
            echo -e "${GREEN}✓ All tests passed${NC}"
        else
            echo_error "Tests failed"
            exit 1
        fi

        echo ""
        echo -e "${GREEN}✓ All quality checks passed!${NC}"
        ;;

    fix)
        echo_step "Auto-fixing all issues..."
        ./scripts/quality.sh format
        ./scripts/quality.sh lint-fix
        echo_step "Re-running checks..."
        ./scripts/quality.sh check
        ;;

    *)
        echo "Usage: $0 {format|lint|lint-fix|type|test|check|fix}"
        echo ""
        echo "Commands:"
        echo "  format    - Format code with Black and Ruff"
        echo "  lint      - Run Ruff linter (check only)"
        echo "  lint-fix  - Run Ruff linter with auto-fix"
        echo "  type      - Run mypy type checker"
        echo "  test      - Run pytest with coverage"
        echo "  check     - Run all checks (format, lint, type, test)"
        echo "  fix       - Auto-fix formatting and linting, then check"
        exit 1
        ;;
esac
