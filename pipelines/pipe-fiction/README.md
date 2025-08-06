# KFP Pipeline Development & Debugging Demo

This repository demonstrates **advanced development and debugging techniques** for Kubeflow Pipelines (KFP), enabling developers to build, test, and debug ML pipelines efficiently across different environments.

**Note:** This demo uses intentionally simple examples to clearly illustrate the core concepts and debugging workflows. The techniques shown here should also apply to complex ML workloads.

## Overview

As part of our MLOps platform, we support KFP for orchestrating machine learning workflows. This demo showcases:

- **Local Development** with immediate feedback loops
- **Interactive Debugging** with full IDE integration
- **Best Practices** for pipeline development and code organization

## Why?

KFP pipelines are hard to develop and debug - here we try to tackle both challenges.

### The KFP Lightweight Component Challenge

KFP Lightweight Components are easier to use than container components. However, they are designed to be **self-contained** - meaning all code must be either:
- Defined inline within the component function
- Installed via `packages_to_install` parameter

This creates a problem: code duplication. If you need the same utility function in multiple components, you typically have to copy-paste the code into each component, leading to maintenance nightmares, which is the reason most people use container components for heavy lifting.

Alternative approaches like publishing packages to PyPI or private registries are possible, but create their own challenges - you'd need to publish and version your package for every code change during development, which is not great.

**Our Solution: Base Image with Pre-installed Package**

We solve this by **pre-installing our ML package into the base Docker image**:

```dockerfile
# In pipe-fiction-codebase/Dockerfile
FROM python:3.12-slim
WORKDIR /app

# Install our package into the base image
COPY pyproject.toml README.md ./
COPY pipe_fiction/ ./pipe_fiction/
RUN uv pip install --system -e .
```

This allows us to **import** (not copy) our code in any component:

```python
@component(base_image="<your-registry>/<your-image-name>:<your-tag>")
def any_component():
    # Clean import - no code duplication!
    from pipe_fiction.data_generator import DataGenerator
    from pipe_fiction.data_processor import DataProcessor
    
    # Use the classes normally
    generator = DataGenerator()
    processor = DataProcessor()
```

### Debugging

Why is debugging a challenge?
- In the cluster, the code runs in pods that you can't easily debug into
- When executing components locally, you must pay attention to DAG order (without the local runner)
- The local runners are not readily supported by standard debugging workflows in IDEs like VS Code or PyCharm
- This often creates a long debug loop that includes waiting for CI/CD pipelines for image builds and pipeline execution

**Our Solution**: A combination of using the new local runner features of KFP and remote debugging sessions, as detailed below.

## Quick Start

### Prerequisites

- Python 3.12+
- Docker (for Docker runner)
- VS Code (recommended) or any debugpy-compatible IDE
- Access to a Kubeflow cluster (for remote execution)

### Setup

1. **Navigate to the demo:**
   ```bash
   # After cloning the example repository
   cd pipelines/pipe-fiction
   ```

2. **Install dependencies for the pipelines environment:**
   
   **Pipeline environment (KFP-specific packages):**
   ```bash
   cd pipelines
   uv sync
   source .venv/bin/activate  # Activate when working on pipeline code
   uv pip install -e ../pipe-fiction-codebase/ # Install custom package
   ```
   
3. **(RE-)Build the base Docker image if needed:**
   ```bash
   cd pipe-fiction-codebase
   docker build -t <your-registry>/<your-image-name>:<your-tag> .
   ```
   More details on this in the `pipe-fiction-codebase` directory.

4. **Run the pipeline**
    
    Run locally using subprocesses (also works in KF-notebooks):
    ```bash
    python run_locally_in_subproc.py
    ```
    
    Run locally using Docker:
    ```bash
    python run_locally_in_docker.py
    ```
    
    Submit to the cluster:
    ```bash
    python run_in_k8s_cluster.py 
    ```

## Repository Organization

This demo is structured to demonstrate **separation** between standard Python code and KFP orchestration setup:

### Code Package (`pipe-fiction-codebase/`)

Contains the core logic as a **standalone Python package**. This Python package is not KFP-related and can be independently developed, tested, and debugged. The only thing that reminds us of K8s is the Dockerfile. The important thing is that it can be installed as a package.

```
pipe-fiction-codebase/
├── pipe_fiction/
│   ├── data_generator.py   # Generate sample data
│   └── data_processor.py   # Data transformation logic
├── Dockerfile              # Containerization with package installation
└── pyproject.toml          # Package definition
```

### Pipeline Orchestration (`pipelines/`)

Contains KFP-specific orchestration code:

```
pipelines/
├── components.py           # KFP component definitions (import from base image)
├── pipeline.py             # Pipeline assembly
├── run_locally_*.py        # Local execution scripts
├── run_in_k8s_cluster.py   # Remote execution
├── .venv/                  # Virtual environment with custom package
└── utils/                  # KFP utilities and patches
```

**Local Package Installation for IDE Support:**

The pipelines directory also contains a virtual environment where, alongside KFP-specific packages, the custom package is installed in development mode:

```bash
# Install the custom package locally for IDE support
uv pip install -e ../pipe-fiction-codebase/
```

This enables full IDE integration:
- Autocomplete and IntelliSense for imported package code
- Type checking and error detection in component definitions
- "Go to definition" works across package imports
- Refactoring support across the entire codebase

*Note: this trick only works when there are no dependency conflicts between the Python venvs in the pipelines folder and the custom packages. As soon as there are multiple packages with significantly different dependencies that should run in different KFP components, this trick no longer works.*

## Execution Environments

As indicated in the quick start section, there are (at least) three ways to execute the pipeline that uses logic from the custom package in tasks within the DAG:

### 1. Subprocess Runner (Fastest Development)

**Best for:** Quick iteration, algorithm development, initial testing

In this setup, the pipeline is run on your local machine using subprocesses.

```bash
cd pipelines
python run_locally_in_subproc.py
```

**Workflow**

A typical workflow using the subprocess runner could look like this:
1. Implement changes in component or custom package code
2. Run `python run_locally_in_subproc.py` to see if it works
3. Set breakpoints using the debugger or IDE to figure out what's wrong
4. Build and push Docker image when ready for submission to the cluster (this could also be done in a CI/CD pipeline):
   `docker build -t <your-registry>/<your-image-name>:<your-tag> . && docker push` 
5. Update image reference in pipeline components if needed
6. Submit pipeline to cluster: `python submit_to_cluster.py`

Note that this workflow also works inside Kubeflow notebooks.

**Advantages:**
- Fastest execution - no container overhead
- Live code changes - no rebuilds needed
- Local Package Access - SubprocessRunner uses the package installed in the local .venv
- No Image Rebuilds - Code changes are immediately available without Docker builds

**Limitations:**
- Environment differences - may not match production environment exactly
- Dependency conflicts - uses local Python environment
- Limited isolation - no containerization benefits
- Lightweight components only - this does not work for container components
- Remote debugging required - CLI-based debuggers (like `pdb` with `breakpoint()`) work directly, but IDE debugging requires remote debugging setup

### 2. Docker Runner (Container-based Development)

**Best for:** Pipelines with container components and multiple differing environments in the KFP tasks

This setup is similar to the local execution in subprocesses, however in this case the local Docker engine on your machine is used to run the pipeline tasks inside Docker containers.

```bash
cd pipelines
python run_locally_in_docker.py
```

**Workflow**

For changes in the pipeline directory:
1. Modify files in `pipelines/` directory (components, pipeline definitions, pipeline arguments)
2. Run `python run_locally_in_docker.py` - changes are immediately reflected
3. Submit to cluster when ready

For changes in the custom Python package:
1. Modify code in `pipe-fiction-codebase/`
2. Rebuild Docker image locally (no push needed):
   `docker build -t <your-registry>/<your-image-name>:<your-tag> .` 
3. Run `python run_locally_in_docker.py` to test with new image
4. To debug the code inside the components, you'll need to use remote debugging (see dedicated section below)
5. Rebuild the image if needed and push it to your registry:
   `docker push <your-registry>/<your-image-name>:<your-tag>`
6. Update image reference in pipeline components if needed
7. Submit pipeline to cluster: `python submit_to_cluster.py`

**Advantages:**
- Production environment - identical to cluster execution
- Debugging support over remote debugger - step into containerized code
- Dependency isolation - no local conflicts

**Limitations:**
- Port forwarding needed - to connect debugger or any other tools 
- Slower iteration - container startup overhead
- Docker dependency - requires Docker runtime
- Image builds needed - for changes in the custom Python package
- Limited resource control - basic Docker constraints only, things like `task.set_env_vars()` or the caching mechanisms are not supported

### 3. Cluster Execution (In-Cluster Debugging)

**Best for:** In-cluster issues, cluster-specific debugging, resource-intensive workloads

Here we use the KFP backend as it runs inside the Kubernetes cluster, as intended.

```bash
cd pipelines
python submit_to_cluster.py
```

**Cluster Execution Workflow**

For pipeline-only changes:
1. Modify files in `pipelines/` directory
2. Enable remote debugging for the task you want to debug (see remote debugging section for details)
3. Submit directly to cluster: `python submit_to_cluster.py`

For custom package changes:
1. Modify code in `pipe-fiction-codebase/`
2. Rebuild and push Docker image: `docker build -t <your-registry>/<your-image-name>:<your-tag> . && docker push`
3. Update image reference in pipeline components
4. Enable remote debugging for the task you want to debug (see remote debugging section for details)
5. Submit pipeline to cluster

**Advantages:**
- Real production environment - actual cluster resources
- All the KFP features - everything from caching to parallelism works here
- Scalability testing - real resource constraints
- Integration testing - with actual cluster services, without port forwards or similar

**Limitations:**
- Slowest feedback - submission and scheduling overhead
- Complex setup - requires cluster access and networking

## Remote Debugging

All debugging across environments (SubprocessRunner, DockerRunner, and cluster execution) now uses remote debugging with [debugpy](https://github.com/microsoft/debugpy) for IDE integration. For CLI-based debugging, `breakpoint()` still works directly with the SubprocessRunner.

### Debuggable Component Decorator (Recommended)

The easiest way to enable debugging is using our custom `@lightweight_debuggable_component` decorator that automatically injects debugging code:

```python
from utils.debuggable_component import lightweight_debuggable_component

@lightweight_debuggable_component(base_image="<your-registry>/<your-image-name>:<your-tag>")
def your_component_name(debug: bool = False):
    # Your component logic here - debugging code is auto-injected!
    from pipe_fiction.data_processor import DataProcessor
    processor = DataProcessor()
    return processor.process()
```

**Features:**
- Automatic debugging code injection (no boilerplate)
- Supports both `debugpy` (VS Code) and `remote-pdb` (CLI) debuggers
- Configurable debug ports
- Works with all KFP component parameters

**Usage examples:**
```python
# Default debugpy on port 5678
@lightweight_debuggable_component(base_image="my-image:latest")
def my_component(debug: bool = False): ...

# Remote pdb on custom port
@lightweight_debuggable_component(
    base_image="my-image:latest",
    debugger_type="remote-pdb",
    debug_port=4444
)
def my_component(debug: bool = False): ...
```

### Manual Component Setup (Alternative)

For manual setup or when not using the decorator, components can be configured with debugging code directly:

```python
@component(base_image="<your-registry>/<your-image-name>:<your-tag>", packages_to_install=["debugpy"])
def your_component_name(debug: bool = False):
    if debug:
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()
    
    # Your component logic here...
```

### VS Code Setup

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Pipeline: Remote SubprocessRunner",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "justMyCode": false,
            "subProcess": true
        },
        {
            "name": "Pipeline: Remote KFP/DockerRunner",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/pipe-fiction-codebase",
                    "remoteRoot": "/app"
                }
            ],
            "justMyCode": false,
            "subProcess": true
        }
    ]
}
```

### Debugging Workflow

1. **Enable debug mode:**
   
   Pass `debug=True` to your component when calling it in the pipeline:
   ```python
   # In your pipeline definition
   task = your_component_name(debug=True)
   ```

2. **Start the pipeline:**
   
   SubprocessRunner:
   ```bash
   python run_locally_in_subproc.py
   ```
   
   DockerRunner:
   ```bash
   python run_locally_in_docker.py
   ```

   Cluster:
   ```bash
   python run_in_k8s_cluster.py
   ```

3. **Connect debugger:**
   - Pipeline will pause and wait for debugger connection
   - Use the appropriate VS Code configuration to attach:
     - "Pipeline: Remote SubprocessRunner" for subprocess execution
     - "Pipeline: Remote KFP/DockerRunner" for Docker and cluster execution

4. **Debug interactively:**
   - Set breakpoints in your pipeline components or the code package that gets imported
   - Step through code execution
   - Inspect variables and data structures
   - Debug both pipeline logic and imported modules

### Cluster Debugging with Port Forwarding

For cluster execution, you'll need port forwarding:

```bash
# Find your pipeline pod
kubectl get pods | grep your-pipeline

# Forward debug port
kubectl port-forward pod/your-pod-name 5678:5678

# Connect local debugger using the "Pipeline: Remote KFP/DockerRunner" configuration
```

## Technical Implementation Notes

### KFP Version Compatibility

This demo includes monkey patches for older KFP versions (pre-2.14) to enable:
- Port forwarding for debugging
- Environment variable injection
- Volume mounting for data access

in the DockerRunner of KFP local.

These patches provide forward compatibility and will be obsolete when upgrading to KFP 2.14+.

### Debugging Architecture

The debugging setup works by:
1. **Injecting debugpy** into pipeline components via the `remote_debugging` parameter
2. **Port forwarding** from container to host (for Docker/cluster execution)
3. **Path mapping** between local IDE and remote container (for Docker/cluster execution)
4. **Unified debugging experience** across all execution environments
