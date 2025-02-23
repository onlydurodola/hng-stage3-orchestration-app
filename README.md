# Orchestration App

## Overview

The Orchestration App is a lightweight, automated CI/CD-like system designed to streamline code testing and deployment within a Kubernetes environment. It leverages a WebSocket interface to accept code submissions from users, tests them in a persistent pod, and deploys production-ready pods (application and database) if the tests pass. Built with Python, FastAPI, and MicroK8s, it integrates logging with an EFK (Elasticsearch, Fluentd, Kibana) stack for monitoring and debugging.

### Key Features
- **WebSocket Interface**: Users submit code via a WebSocket endpoint (`/ws/code`).
- **Persistent Testing**: A single test pod (`test-test`) in the `user-test` namespace runs and evaluates code submissions.
- **Automated Deployment**: Successful code triggers deployment of production pods (`test-prod-*`, `test-prod-db-*`).
- **Logging**: All actions are logged to Elasticsearch, with Fluentd aggregating logs and Kibana providing visualization (EFK stack).
- **Containerized Setup**: Uses Docker Compose for local development and MicroK8s for Kubernetes orchestration.

### Purpose
This app simulates a developer workflow where code is tested instantly and deployed seamlessly, demonstrating skills in containerization, Kubernetes, and real-time systems.

---

## Project Structure
```
/orchestration-app
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI WebSocket server
│   ├── kubernetes_manager.py # Kubernetes resource management
│   ├── deployment_pipeline.py # Test and deployment logic
│   ├── log_processor.py     # Elasticsearch logging
│   ├── middleware.py        # WebSocket authentication
│   └── Dockerfile.test      # Test pod Dockerfile
├── Scripts/
│   ├── test_backend.py      # Test script for code submissions
│   └── run.sh               # Test pod execution script
├── infrastructure/
│   ├── elasticsearch.yaml   # Elasticsearch service configuration
│   ├── fluentd.yaml         # Fluentd service configuration
│   ├── kibana.yaml          # Kibana service configuration
│   ├── rbac.yaml            # Cluster RBAC permissions
│   └── ingress.yaml         # Production ingress (optional)
├── Dockerfile               # Orchestration app Dockerfile
├── compose.yaml             # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

---

## Prerequisites

- **Docker**: For containerization (local development).
- **Docker Compose**: To manage multi-container setup.
- **MicroK8s**: Lightweight Kubernetes cluster (tested with v1.32.1).
- **Python**: Version 3.9+ (for local script execution).
- **kubectl**: Kubernetes CLI (installed in the container and on the host).

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd orchestration-app
```

### 2. Configure Environment
Create a `.env` file:
```bash
echo "ELASTICSEARCH_HOST=http://elasticsearch:9200" > .env
echo "API_KEY=ceab673e2b6794dd31be3dcf12f1db9d6f6cfe75c2c5f302747f4d94516020db" >> .env
```
Ensure your Kubernetes config is accessible:
```bash
mkdir -p ~/.kube
cp /path/to/kubeconfig ~/.kube/config
```

### 3. Build and Run with Docker Compose
```bash
docker compose up -d --build
```
This starts:
- `orchestration`: The WebSocket server on `0.0.0.0:8000`.
- `elasticsearch`: Logging service on `0.0.0.0:9200`.
- `test-base`: Base image for test pods.

### 4. Deploy EFK Stack to Kubernetes
Apply EFK configurations:
```bash
kubectl apply -f infrastructure/elasticsearch.yaml
kubectl apply -f infrastructure/fluentd.yaml
kubectl apply -f infrastructure/kibana.yaml
```
Optionally apply RBAC and ingress:
```bash
kubectl apply -f infrastructure/rbac.yaml
kubectl apply -f infrastructure/ingress.yaml
```

### 5. Verify Setup
Check containers:
```bash
docker compose ps
```
Check pods:
```bash
kubectl get pods -n user-test
```

---

## Usage

### Testing Code Submission
#### Via WebSocket Client:
```bash
wscat -c ws://localhost:8000/ws/code -H "X-API-Key: ceab673e2b6794dd31be3dcf12f1db9d6f6cfe75c2c5f302747f4d94516020db"
```
Send bad code:
```json
{"user_id": "test", "code": "print('broken'"}
```
Response:
```json
{"status": "tests_failed", "namespace": "user-test"}
```
Send good code:
```json
{"user_id": "test", "code": "print('Hello')"}
```
Response:
```json
{"status": "deployed", "namespace": "user-test"}
```

#### Via Test Script:
```bash
python Scripts/test_backend.py
```
Output:
```
Bad code response: {"status": "tests_failed", "namespace": "user-test"}
Good code response: {"status": "deployed", "namespace": "user-test"}
```

### Monitoring Logs
Access Kibana (if deployed) at `http://<kibana-host>:5601` to view logs from Elasticsearch.
Check pod logs:
```bash
kubectl logs test-test -n user-test
kubectl logs -l app=prod -n user-test
```

---

## Implementation Details

### Core Components
- **WebSocket Server (`main.py`)**: Built with FastAPI, accepts code submissions, and delegates to the deployment pipeline.
- **Kubernetes Manager (`kubernetes_manager.py`)**: Uses `kubectl exec` via subprocess to inject code into the test pod and manage deployments.
- **Deployment Pipeline (`deployment_pipeline.py`)**: Tests code in `test-test`, deploys production pods (`test-prod-*`, `test-prod-db-*`) on success.
- **Logging (`log_processor.py`)**: Sends logs to Elasticsearch with retries for reliability.
- **Test Pod Script (`run.sh`)**: Keeps `test-test` running, executes injected code, and logs output.

### Challenges Overcome
- **Persistent Test Pod**: Achieved with a `while` loop in `run.sh` and `restartPolicy: Always`.
- **Elasticsearch Integration**: Fixed HTTPS issues by disabling security in `compose.yaml`.
- **WebSocket/Kubernetes Issues**: Switched from `connect_get_namespaced_pod_exec` to `kubectl exec` to resolve `400 Bad Request` errors.

### Current State
✅ **Working**: Code submission, testing, and deployment triggering work as expected.

⏳ **In Progress**: Fixing a syntax error in the production pod’s command (`test-prod-*`) causing `CrashLoopBackOff`.

### Future Improvements
- Stabilize production pod deployment with a robust command structure.
- Add a frontend UI for real-time code submission and log viewing.
- Enhance error handling for edge cases (e.g., pod crashes, network failures).
- Scale to support multiple users with dynamic namespaces.

---

## Contributing
Feel free to fork this repository, submit issues, or send pull requests. Focus areas include production pod stability and EFK enhancements.

## License
This project is unlicensed for now—open for collaboration and feedback!
