Orchestration App

/backend.im-orchestration
├── app/
│   ├── __init__.py
│   ├── main.py             # WebSocket server
│   ├── kubernetes_manager.py
│   ├── deployment_pipeline.py
│   └── schemas.py          # Pydantic models
├── infrastructure/
│   ├── rbac.yaml           # Cluster permissions
│   ├── efk-stack.yaml      # Logging resources
│   └── ingress.yaml        # Production ingress
├── scripts/
│   └── test_runner.py      # Test validation logic
├── Dockerfile
├── requirements.txt
└── .env.example
