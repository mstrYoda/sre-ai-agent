from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.file import FileTools
from phi.memory.db.sqlite import SqliteMemoryDb
from phi.storage.agent.sqlite import SqlAgentStorage
import requests

gemini_model = Gemini(api_key="")

leader_memory = SqliteMemoryDb(db_file="leader_memory.db")
file_memory = SqliteMemoryDb(db_file="file_memory.db")
search_memory = SqliteMemoryDb(db_file="search_memory.db")

leader_storage = SqlAgentStorage(table_name="agent_sessions", db_file="agent_storage.db")

def run_shell_command(args: str, tail: int = 100) -> str:
    """Runs a shell command and returns the output or error.

    Args:
        args (str): The command to run as a list of strings.
        tail (int): The number of lines to return from the output.
    Returns:
        str: The output of the command.
    """
    import subprocess

    try:
        result = subprocess.run(args.split(" "), capture_output=True, text=True)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        # return only the last n lines of the output
        return "\n".join(result.stdout.split("\n")[-tail:])
    except Exception as e:
        return f"Error: {e}"

def query_prometheus(query: str, prometheus_url: str = "http://localhost:9090") -> str:
    """Sends a PromQL query to Prometheus and returns the result.

    Args:
        query (str): The PromQL query to execute
        prometheus_url (str): The base URL of the Prometheus server (default: http://localhost:9090)

    Returns:
        str: The query results as a formatted string, or error message if the query fails
    """
    try:
        # Construct the query URL
        url = f"{prometheus_url}/api/v1/query"
        params = {'query': query}
        
        # Send the request
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == 'success':
            result = data['data']['result']
            
            # Format the results as a string
            if not result:
                return "Query returned no data"
            
            output = []
            for item in result:
                metric = item.get('metric', {})
                value = item.get('value', [None, 'N/A'])
                
                # Format metric labels
                labels = ', '.join(f"{k}={v}" for k, v in metric.items())
                # Format timestamp and value
                timestamp, metric_value = value
                
                output.append(f"[{labels}] Value: {metric_value}")
            
            return '\n'.join(output)
        else:
            return f"Query failed: {data.get('error', 'Unknown error')}"
            
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Prometheus: {str(e)}"
    except Exception as e:
        return f"Error processing query: {str(e)}"

k8s_agent = Agent(
    model=gemini_model,
    description="""
    Senior SRE Kubernetes Troubleshooting Agent - Autonomous Cluster Healing System
    
    A self-healing Kubernetes operations specialist combining deep cluster observability with 
    autonomous remediation capabilities. Expert in distributed systems failure modes,
    performance optimization, and incident post-mortem automation. Maintains 3 golden signals:
    latency, errors, and saturation. Prioritizes cluster stability while minimizing blast radius.
    """,
    role="Senior Site Reliability Engineer - Kubernetes Platform",
    instructions=[
        "0. Confirmation for critical operations",
        "Ask for the user's confirmation for critical operations like kubectl apply, patch, delete, etc.",
        "PHASED OPERATIONS:",
        "1. INITIAL ASSESSMENT, USE SHELL COMMAND TOOL TO RUN KUBECTL COMMANDS:",
        "   - Check Deployment rollout history: `kubectl rollout history deployment/{name}`",
        "   - Verify StatefulSet update strategy: `kubectl get sts/{name} -o jsonpath='{.spec.updateStrategy}'`",
        "   - Inspect ClusterEvents chronologically: `kubectl get events --sort-by=.metadata.creationTimestamp`",
        "   - Check Pod lifecycle phases: `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{\"\\t\"}{.status.phase}{\"\\t\"}{.status.message}{\"\\n\"}{end}'`",
        
        "2. ERROR IDENTIFICATION:",
        "   - Perform triage: Check CrashLoopBackOff, ImagePullBackOff, CreateContainerConfigError",
        "   - Analyze container exit codes: `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{\"\\t\"}{.status.containerStatuses[*].lastState.terminated.exitCode}{\"\\n\"}{end}'`",
        "   - Check resource saturation: `kubectl top pods --containers | sort -k3 -nr`",
        
        "3. REMEDIATION PROTOCOLS:",
        "   - Rollback strategy: `kubectl rollout undo deployment/{name} --to-revision={stable_rev}`",
        "   - Controlled pod restart: `kubectl rollout restart deployment/{name} --grace-period=30`",
        "   - Auto-scale adjustment: `kubectl scale deploy/{name} --replicas={safe_count}`",
        "   - Drain node with pod disruption budget: `kubectl drain {node} --ignore-daemonsets --delete-emptydir-data`",
        
        "4. POST-INCIDENT ANALYSIS:",
        "   - Generate forensic bundle: `kubectl get all,events,metrics --all-namespaces -o yaml > cluster_snapshot_$(date +%s).yaml`",
        "   - Create timeline of events with UTC timestamps",
                
        "OBSERVABILITY INTEGRATION:",
        "- Cross-correlate with Prometheus metrics (apiserver_request_duration_seconds, KubeletPodStartDuration)",
        "- Check Grafana dashboards for node memory pressure and IO wait",
        "- Analyze distributed tracing data for microservice dependencies"
    ],
    tools=[run_shell_command, FileTools(), query_prometheus, DuckDuckGo()],
    add_history_to_messages=True,
    num_history_responses=10,
    markdown=True,
    monitoring=True,
    debug_mode=False,  # Disabled in production per security policy
)

k8s_agent.cli_app(markdown=True)