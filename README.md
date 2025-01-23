# Kubernetes SRE Agent

An autonomous Kubernetes troubleshooting and healing agent powered by Google's Gemini LLM. This agent combines deep cluster observability with automated remediation capabilities to help maintain Kubernetes cluster health and stability.

## Features

- 🔍 **Automated Kubernetes Diagnostics**
  - Deployment rollout analysis
  - StatefulSet configuration verification
  - Cluster event monitoring
  - Pod lifecycle inspection

- 🚨 **Intelligent Error Detection**
  - Container crash analysis
  - Resource saturation monitoring
  - Exit code investigation
  - Configuration error detection

- 🛠️ **Autonomous Remediation**
  - Controlled rollbacks
  - Safe pod restarts
  - Auto-scaling adjustments
  - Node drainage with PDB respect

- 📊 **Observability Integration**
  - Prometheus metrics analysis
  - DuckDuckGo search capabilities
  - File system operations
  - Historical context awareness

## Prerequisites

- Python 3.x
- Access to Google Gemini API
- Running Kubernetes cluster with `kubectl` access
- Prometheus installation (default: http://localhost:9090)
- Required Python packages:
  - phi-agent
  - requests

## Installation

1. Clone the repository

2. Install dependencies

3. Configure your Gemini API key in `main.py`:



## Usage

Run the agent:

```bash
python main.py
```


The agent provides an interactive CLI interface where you can:
- Query cluster status
- Investigate issues
- Execute remediation actions
- Analyze Prometheus metrics
- Access troubleshooting documentation

## Storage and Memory

The agent utilizes SQLite databases for persistent storage:
- `leader_memory.db`: Main agent memory storage
- `file_memory.db`: File operations memory
- `search_memory.db`: Search query memory
- `agent_storage.db`: Agent session storage

## Safety Features

- Confirmation required for critical operations
- Controlled remediation with minimal blast radius
- Debug mode disabled in production
- Historical context maintained for decision making

## Monitoring Capabilities

The agent monitors the three golden signals:
- Latency
- Errors
- Saturation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.