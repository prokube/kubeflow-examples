# KFP Pipeline Development & Debugging Demo

This repository demonstrates **advanced development and debugging techniques** for Kubeflow Pipelines (KFP), enabling developers to build, test, and debug ML pipelines efficiently across different environments.

**Note:** This demo uses intentionally simple examples to clearly illustrate the core concepts and debugging workflows. The techniques shown here should also apply to complex ML workloads.

## Overview

As part of our MLOps platform, we support KFP for orchestrating machine learning workflows. This demo showcases:

- **Local Development** with immediate feedback loops
- **Interactive Debugging** with full IDE integration
- **Multi-environment Support** (subprocess, Docker, cluster)
- **Best Practices** for pipeline development and code organization

## Quick Start

### Prerequisites

- Python 3.12+
- Docker (for Docker runner)
- VS Code (recommended) or any debugpy-compatible IDE
- Access to a Kubeflow cluster (for remote execution)

### Setup

1. **Navigate to the demo:**
   ```bash
   # After cloning the larger example repository
   cd pipelines/pipe-fiction
   ```

2. **Install dependencies for both virtual environments:**
   
   **Pipeline environment (KFP-specific packages):**
   ```bash
   cd pipelines
   uv sync
   source .venv/bin/activate  # Activate when working on pipeline code
   ```
   
3. **Build the base Docker image:**
   ```bash
   cd pipe-fiction-codebase
   docker build -t <your-registry>/<your-image-name>:<your-tag> .
   ```
   More details on this in the `pipe-fiction-codebase` directory.

## Repository Organization

This demo is structured to demonstrate **separation** between standard Python code and KFP orchestration setup, while solving a key challenge with KFP Lightweight Components:

### The KFP Lightweight Component Challenge

KFP Lightweight Components are designed to be **self-contained** - meaning all code must be either:
- Defined inline within the component function
- Installed via `packages_to_install` parameter

This creates a problem: code duplication. If you need the same utility function in multiple components, you typically have to copy-paste the code into each component, leading to maintenance nightmares, which is the reason most people use container components for heavy lifting.

Alternative approaches like publishing packages to PyPI or private registries are possible, but create their own challenges - you'd need to publish and version your package for every code change during development, which significantly slows down the iteration cycle.

### Our Solution: Base Image with Pre-installed Package

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

### Code Package (`pipe-fiction-codebase/`)

Contains the core ML logic as a **standalone Python package**:

```
pipe-fiction-codebase/
├── pipe_fiction/
│   ├── data_generator.py   # Generate sample data
│   └── data_processor.py   # Data transformation logic
├── Dockerfile              # Containerization with package installation
└── pyproject.toml          # Package definition
```

**Key Benefits of This Approach:**

- **No Code Duplication** - Import the same classes/functions across multiple components without copying code
- **Independent Development** - The `pipe_fiction` package can be developed, tested, and debugged completely independently of KFP
- **Data Scientists in Their Home Turf** - Familiar Python development environment without KFP complexity
- **Reusability** - The same code can be used in notebooks, scripts, web services, or other orchestration frameworks
- **Standard Testing** - Use pytest, unittest, or any testing framework without KFP complexity
- **IDE Support** - Full autocomplete, refactoring, and debugging support for your core logic
- **Version Management** - Package versioning independent of pipeline versions
- **Clean Components** - Pipeline components focus on orchestration, not business logic implementation

### Pipeline Orchestration (`pipelines/`)

Contains KFP-specific orchestration code:

```
pipelines/
├── components.py           # KFP component definitions (import from base image)
├── pipeline.py             # Pipeline assembly
├── run_locally_*.py        # Local execution scripts
├── submit_to_cluster.py    # Remote execution
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

**This separation allows you to:**

1. **Develop core logic** using standard Python development practices
2. **Test business logic** without spinning up KFP environments  
3. **Debug algorithms** using familiar tools and workflows
4. **Reuse code** across multiple components without duplication
5. **Maintain clean abstractions** between ML code and infrastructure
6. **Scale development** - multiple developers can work on the package independently

## Execution Environments

There are (at least) three ways to execute the pipeline that uses logic from the custom package in tasks within the DAG:

### 1. Subprocess Runner (Fastest Development)

**Best for:** Quick iteration, algorithm development, initial testing

```bash
cd pipelines
python run_locally_in_subproc.py
```

**Advantages:**
- Fastest execution - no container overhead
- Direct debugging - breakpoints work immediately
- Live code changes - no rebuilds needed
- Full IDE integration - all debugging features available
- Local Package Access - SubprocessRunner uses the package installed in the local .venv
- No Image Rebuilds - Code changes are immediately available without Docker builds
- Immediate Debugging - Set breakpoints in both pipeline and package code instantly
- Fast iteration - Modify algorithms and test immediately

**Limitations:**
- Environment differences - may not match production environment exactly
- Dependency conflicts - uses local Python environment
- Limited isolation - no containerization benefits

### 2. Docker Runner (Container-based Development)

**Best for:** Pipelines with container components and multiple differing environments in the KFP tasks

```bash
cd pipelines
python run_locally_in_docker.py
```

**Advantages:**
- Production environment - identical to cluster execution
- Full debugging support - step into containerized code
- Dependency isolation - no local conflicts
- Volume mounting - access local data files
- Port forwarding - debug server accessible from IDE

**Limitations:**
- Slower iteration - container startup overhead
- Docker dependency - requires Docker runtime
- Limited resource control - basic Docker constraints only

### 3. Cluster Execution (In-Cluster Debugging)

**Best for:** In-cluster issues, cluster-specific debugging, resource-intensive workloads

```bash
cd pipelines
python submit_to_cluster.py
```

**Advantages:**
- Real production environment - actual cluster resources
- Remote debugging - debug running pods via port-forwarding
- Scalability testing - real resource constraints
- Integration testing - with actual cluster services

**Limitations:**
- Slowest feedback - submission and scheduling overhead
- Resource constraints - limited by cluster quotas
- Complex setup - requires cluster access and networking

## Development Workflows

### Subprocess Runner Workflow
For rapid pipeline development and testing:
1. Implement changes in component or custom package code
2. Run `python run_locally_in_subproc.py` to validate immediately
3. Build and push Docker image when ready for cluster: `docker build -t <your-registry>/<your-image-name>:<your-tag> . && docker push`
4. Update image reference in pipeline components if needed
5. Submit pipeline to cluster: `python submit_to_cluster.py`

### Docker Runner Workflow

**For pipeline-only changes:**
1. Modify files in `pipelines/` directory (components, pipeline definitions)
2. Run `python run_locally_in_docker.py` - changes are immediately reflected
3. Submit to cluster when ready

**For custom package changes:**
1. Modify code in `pipe-fiction-codebase/`
2. Rebuild Docker image locally: `docker build -t <your-registry>/<your-image-name>:<your-tag> .`
3. Run `python run_locally_in_docker.py` to test with new image
4. Push image to registry: `docker push <your-registry>/<your-image-name>:<your-tag>`
5. Update image reference in pipeline components if needed
6. Submit pipeline to cluster

### Cluster Execution Workflow

**For pipeline-only changes:**
1. Modify files in `pipelines/` directory
2. Submit directly to cluster: `python submit_to_cluster.py`

**For custom package changes:**
1. Modify code in `pipe-fiction-codebase/`
2. Rebuild and push Docker image: `docker build -t <your-registry>/<your-image-name>:<your-tag> . && docker push`
3. Update image reference in pipeline components
4. Submit pipeline to cluster

## Debugging Setup

### VS Code Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Remote Attach",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/../pipe-fiction-codebase",
                    "remoteRoot": "/app"
                }
            ],
            "justMyCode": false,
            "subProcess": true
        }
    ]
}
```

### Other IDE Support

**PyCharm:**
- Run → Edit Configurations → Python Remote Debug
- Host: `localhost`, Port: `5678`
- Path mappings: Local: `pipe-fiction-codebase` → Remote: `/app`

**Any debugpy-compatible editor:**
- Connect to `localhost:5678`
- Configure path mappings as needed

### Debugging Workflow

1. **Enable debug mode:**
   ```python
   # In run_locally_in_docker.py
   environment={'KFP_DEBUG': 'true'}
   ```

2. **Start the pipeline:**
   ```bash
   python run_locally_in_docker.py
   ```

3. **Connect debugger:**
   - Pipeline will pause and wait for debugger connection
   - Attach your IDE debugger to `localhost:5678`

4. **Debug interactively:**
   - Set breakpoints in your pipeline components
   - Step through code execution
   - Inspect variables and data structures
   - Debug both pipeline logic and imported modules

## Example: Debugging a Data Processing Pipeline

This demo includes a simple data processing pipeline that demonstrates common debugging scenarios:

### Components

1. **DataGenerator Component** (`generate_data_comp`)
   - Generates sample text data for processing
   - Demonstrates data creation debugging
   - Logs operations with structured logging

2. **DataProcessor Component** (`process_data_comp`)
   - Processes text data and extracts information
   - Counts words and generates statistics
   - Demonstrates data transformation debugging

### Debugging Scenarios

**Data Generation Logic:**
```python
generator = DataGenerator()
lines = generator.create_sample_data()  # Set breakpoint here
```

**Data Processing Logic:**
```python
processor = DataProcessor()
processed_data = processor.process_lines(lines)  # Debug transformations
summary = processor.get_summary(processed_data)  # Inspect results
```

**Cross-Component Data Flow:**
- Debug how data flows between pipeline components
- Inspect intermediate outputs and transformations
- Validate data contracts between components

## Advanced Features

### Volume Mounting for Data Access

```python
# Mount local data directory into container
local.init(runner=local.DockerRunner(
    volumes={
        os.path.abspath('../data'): {'bind': '/app/data', 'mode': 'ro'}
    }
))

# Access files in container
result = example_pipeline(file_path='/app/data/local-data-file.txt')
```

### Environment-Controlled Debugging

```python
# Enable/disable debugging via environment variables
environment={
    'KFP_DEBUG': 'true',           # Enable debugging
    'KFP_DEBUG_PORT': '5678',      # Custom debug port
}
```

### Cluster Debugging with Port Forwarding

```bash
# Find your pipeline pod
kubectl get pods | grep your-pipeline

# Forward debug port
kubectl port-forward pod/your-pod-name 5678:5678

# Connect local debugger to remote pod
# Use the same VS Code configuration
```

## Technical Implementation Notes

### KFP Version Compatibility

This demo includes monkey patches for older KFP versions (pre-2.14) to enable:
- Port forwarding for debugging
- Environment variable injection
- Volume mounting for data access

These patches provide forward compatibility and will be obsolete when upgrading to KFP 2.14+.

### Debugging Architecture

The debugging setup works by:
1. **Injecting debugpy** into pipeline components
2. **Port forwarding** from container to host
3. **Path mapping** between local IDE and remote container
4. **Environment control** for enabling/disabling debug mode

## Contributing

This demo represents best practices we've developed for KFP pipeline development. Contributions and improvements are welcome!

### Future Enhancements

- Support for KFP 2.14+ native features
- Additional debugging tools integration
- Performance profiling examples
- Multi-language component support

## Additional Resources

- [Kubeflow Pipelines Documentation](https://kubeflow-pipelines.readthedocs.io/)
- [debugpy Documentation](https://github.com/microsoft/debugpy)
- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)

---

For questions or support with KFP development on our MLOps platform, please reach out to our team.
