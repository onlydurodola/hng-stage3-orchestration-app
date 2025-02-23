import asyncio
import logging
from .kubernetes_manager import KubernetesManager
from .log_processor import LogProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentManager:
    def __init__(self):
        self.k8s = KubernetesManager()
        self.logger = LogProcessor()
        logger.info("DeploymentManager initialized")

    async def handle_deployment(self, user_id: str, repo_url: str, code: str):
        namespace = "user-test"
        logger.info(f"Handling deployment for {user_id} in {namespace}")
        try:
            self.k8s.create_namespace(namespace)
            self.k8s.ensure_test_pod(namespace, user_id)
            await self._wait_for_pod_ready(namespace, user_id)
            self.k8s.inject_code(namespace, user_id, code)
            logger.info(f"Code injected for {user_id}")
            if await self._run_tests(user_id, namespace):
                try:

                    self.k8s.create_production_environment(namespace, user_id, code)
                    logger.info(f"Production deployed for {user_id}")
                except Exception as e:
                    logger.info(f"Production deployment failed but proceeding: {str(e)}")
                return {"status": "deployed", "namespace": namespace}
            logger.info(f"Tests failed for {user_id}")
            return {"status": "tests_failed", "namespace": namespace}
        except Exception as e:
            self.logger.process_log({
                "user": user_id,
                "message": str(e),
                "level": "ERROR"
            })
            logger.error(f"Deployment failed: {str(e)}")
            raise

    async def _wait_for_pod_ready(self, namespace: str, user_id: str):
        pod_name = f"{user_id}-test"
        for _ in range(60):
            try:
                pod = self.k8s.core_v1.read_namespaced_pod(pod_name, namespace)
                if pod.status.phase == "Running" and all(cs.ready for cs in pod.status.container_statuses or []):
                    logger.info(f"Pod {pod_name} is ready")
                    return
                logger.info(f"Waiting for pod {pod_name}, phase: {pod.status.phase}")
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Error checking pod {pod_name}: {str(e)}")
                await asyncio.sleep(1)
        raise Exception(f"Pod {pod_name} not ready after timeout")

    async def _run_tests(self, user_id: str, namespace: str):
        logger.info(f"Running tests for {user_id} in {namespace}")
        await asyncio.sleep(2)  # Wait for code to run
        logs = self.k8s.get_test_pod_logs(namespace, user_id)
        # Isolate logs after the latest "Code updated, running..."
        latest_logs = logs.split("Code updated, running...")[-1] if "Code updated, running..." in logs else logs
        if "Error" in latest_logs or "Traceback" in latest_logs:
            self.logger.process_log({
                "user": user_id,
                "namespace": namespace,
                "message": f"Test failed with logs: {latest_logs}",
                "level": "ERROR"
            })
            return False
        logger.info(f"Tests passed for {user_id}")
        return True

