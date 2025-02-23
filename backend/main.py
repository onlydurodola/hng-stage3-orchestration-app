import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .kubernetes_manager import KubernetesManager
from .log_processor import LogProcessor
from .middleware import WebSocketAuthMiddleware  # Import the middleware
from .deployment_pipeline import DeploymentManager

app = FastAPI()
app.add_middleware(WebSocketAuthMiddleware)  # Apply the middleware
deployment_mgr = DeploymentManager()

@app.websocket("/ws/code")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_id = payload["user_id"]
                code = payload["code"]
                result = await deployment_mgr.handle_deployment(user_id, "http://dummy-repo-url", code)
                await websocket.send_text(json.dumps(result))
            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
    except WebSocketDisconnect:
        print("Websocket disconnected")
    

class DeploymentManager:
    def __init__(self):
        self.k8s = KubernetesManager()
        self.logger = LogProcessor()

    async def handle_deployment(self, user_id: str, code: str):
        namespace = f"user-{user_id}"
        try:
            self.k8s.create_namespace(namespace)
            self.k8s.ensure_test_pod(namespace, user_id)
            self.k8s.inject_code(namespace, user_id, code)
            if await self._run_tests(namespace, user_id):
                self.k8s.create_production_environment(namespace, user_id, code)
                return {"status": "deployed", "namespace": namespace}
            return {"status": "tests_failed", "namespace": namespace}
        except Exception as e:
            self.logger.log_error(user_id, str(e))
            raise

    async def _run_tests(self, namespace: str, user_id: str):
        await asyncio.sleep(2)
        logs = self.k8s.get_test_pod_logs(namespace, user_id)
        if "Error" in logs or "Traceback" in logs:
            self.logger.process_log({
                "user": user_id,
                "namespace": namespace,
                "message": f"Test failed with logs: {logs}",
                "level": "ERROR"
            })
            return False
        return True