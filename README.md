/orchestration-app

├── backend/

│   ├── _init_.py          # Empty file to mark as Python package

│   ├── main.py             # FastAPI WebSocket server

│   ├── kubernetes_manager.py # Kubernetes interaction logic (e.g., pod creation, code injection)
│   ├── deployment_pipeline.py # Deployment workflow (testing and production deployment)
│   ├── log_processor.py    # Elasticsearch logging integration
│   ├── middleware.py       # WebSocket authentication middleware
│   └── Dockerfile.test     # Dockerfile for test-base image
├── Scripts/
│   ├── test_backend.py     # Test script simulating bad and good code submissions
│   └── run.sh              # Shell script for test pod persistence and code execution
├── Dockerfile              # Dockerfile for orchestration app (includes kubectl)
├── compose.yaml            # Docker Compose configuration (orchestration, Elasticsearch, test-base)
├── requirements.txt        # Python dependencies (e.g., fastapi, kubernetes, elasticsearch)
└── .env                    # Environment variables (e.g., API key, Elasticsearch host)
