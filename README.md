# kubernetes-unused-reporter

A command-line tool to report unused Kubernetes secrets in all namespaces of your cluster.

## Features

- Lists all namespaces in your Kubernetes cluster
- Detects and reports secrets that are not referenced by any pod, deployment, statefulset, daemonset, or replicaset
- Excludes default and system-generated secrets from the report
- Colorful terminal output for easy reading

## Requirements

- Python 3.8+
- Access to a Kubernetes cluster (with a valid kubeconfig)

## Installation

1. Clone this repository:

   ```zsh
   git clone <your-repo-url>
   cd kubernetes-unused-reporter
   ```

2. Install dependencies:

   ```zsh
   pip install .
   ```

   Or, if you prefer, use:

   ```zsh
   pip install -r requirements.txt
   ```

## Usage

Run the tool with:

```zsh
python main.py
```

You will see a list of namespaces and any unused secrets found in each. Unused secrets are highlighted in red, and namespaces with no unused secrets are shown in yellow.

## Project Structure

- `main.py` — Entry point for the CLI tool
- `src/k8s.py` — Kubernetes API logic and helpers
- `pyproject.toml` — Project metadata and dependencies

## Development

- To add new features, edit the code in `src/k8s.py` and update `main.py` as needed.
- For dependency management, prefer `pyproject.toml`.
- Use `.gitignore` to keep your repository clean.
