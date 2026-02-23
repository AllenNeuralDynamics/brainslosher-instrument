# Brainslosher Launcher

Wrapper repository for launching the Brainslosher instrument control software and web UI together as a single instance. The instrument control software and web UI are included as git submodules.

## Repository Structure
```
brainslosher-launcher/
├── src/
│   ├── brainslosher-instrument/   # submodule
│   └── brainslosher-web-ui/       # submodule
├── ui/                            # populated automatically at launch
├── main.py
└── README.md
```

## Setup

Clone the repository with submodules:
```bash
git clone --recurse-submodules https://github.com/AllenNeuralDynamics/brainslosher-launcher
```

If you already cloned without `--recurse-submodules`:
```bash
git submodule update --init
```

## Launch

Run `main.py` with paths to your instrument and UI config files. On first launch the latest UI release will be downloaded automatically.
```bash
uv run brainslosher-instrument --instrument-config path/to/instrument_config.json --ui-config path/to/ui_config.json
```

Optional arguments:
```bash
uv run brainslosher-instrument --instrument-config path/to/instrument_config.json \
               --ui-config path/to/ui_config.json \
               --log-level DEBUG
```

The web UI will be available at `http://localhost:<port>` where the port is defined in your UI config file (default `8000`).

### Package/Project Management 

This project utilizes [uv](https://docs.astral.sh/uv/) to handle installing dependencies as well as setting up environments for this project. It replaces tool like pip, poetry, virtualenv, and conda. 

This project also uses [tox](https://tox.wiki/en/latest/index.html) for orchestrating multiple testing environments that mimics the github actions CI/CD so that you can test the workflows locally on your machine before pushing changes. 

### Code Quality Check

The following are tools used to ensure code quality in this project. 

- Unit Testing

```bash
uv run pytest tests
```

- Linting

```bash
uv run ruff check
```

- Type Check

```bash
uv run mypy src/brainslosher-instrument
```

## Documentation
To generate the rst files source files for documentation, run
```bash
sphinx-apidoc -o docs/source/ src
```
Then to create the documentation HTML files, run
```bash
sphinx-build -b html docs/source/ docs/_build/html
```
