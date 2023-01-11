pkg := "jma_scraper"
test_dir := "tests"

venv := "venv"
venv_path := `pwd` / venv
vpy := venv_path / "bin" / "python"
vpip := venv_path / "bin" / "pip"
activate := venv_path / "bin" / "activate"

create_venv:
    @echo "Virtual env $(python --version)({{venv}}) is being created.."
    python -m venv {{venv}}
    @echo "Done"

#  Create dependency file from pyproject.toml, testing.in, linting.in. NOTE: Installation will NOT be executed.
depsync:
    pip-compile "pyproject.toml" -o "requirements/pyproject.txt" --resolver=backtracking && \
    cd "requirements" && pip-compile "linting.in" -o "linting.txt" --resolver=backtracking && \
    pip-compile "testing.in" -o "testing.txt" --resolver=backtracking

install:
    @echo "Using this pip ...: $(which pip)"
    pip install --upgrade pip
    pip install -r "requirements/all.txt"

uninstall:
    @echo "Uninstalling using this pip $(which pip)"
    @echo "Uninstalling following...:\n $(pip freeze)"
    -pip freeze > "tmp.txt" && pip uninstall -y -r "tmp.txt" && rm "tmp.txt"

# Clean initialization of dev enviroment
init:
    @echo "Fresh setup for this project"
    just create_venv
    source {{activate}} && \
    echo $(which pip) && \
    just uninstall && \
    just depsync && \
    just install

isort *flags:
    isort {{pkg}} {{test_dir}} {{flags}}

black *flags:
    black {{pkg}} {{test_dir}} {{flags}}

ruff *flags:
    ruff {{pkg}} {{test_dir}} {{flags}}


format: (ruff "--fix") isort black

lint: ruff (black "--diff")  (isort "--check-only --df")

mypy:
    mypy {{pkg}} {{test_dir}}

clear:
    rm -rf ".mypy_cache"
    rm -rf ".ruff_cache"
