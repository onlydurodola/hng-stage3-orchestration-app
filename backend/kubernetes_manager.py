from kubernetes import client, config
import os
import logging
import subprocess

logger = logging.getLogger(__name__)

class KubernetesManager:
    def __init__(self):
        kubeconfig = os.getenv("KUBECONFIG", "/root/.kube/config")
        try:
            config.load_kube_config(kubeconfig)
        except Exception as e:
            logger.error(f"Failed to load kubeconfig from {kubeconfig}: {str(e)}")
            raise
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    def create_namespace(self, namespace: str):
        try:
            self.core_v1.read_namespace(name=namespace)
        except client.ApiException as e:
            if e.status == 404:
                self.core_v1.create_namespace(
                    body=client.V1Namespace(
                        metadata=client.V1ObjectMeta(name=namespace)
                    )
                )
            else:
                raise

    def ensure_test_pod(self, namespace: str, user_id: str):
        pod_name = f"{user_id}-test"
        try:
            self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        except client.ApiException as e:
            if e.status == 404:
                self.core_v1.create_namespaced_pod(
                    namespace=namespace,
                    body=client.V1Pod(
                        metadata=client.V1ObjectMeta(name=pod_name, labels={"app": "test"}),
                        spec=client.V1PodSpec(
                            containers=[client.V1Container(
                                name="test",
                                image="nowdurodola/test-base:latest",
                                image_pull_policy="IfNotPresent"
                            )],
                            restart_policy="Always"
                        )
                    )
                )
            else:
                raise

    def inject_code(self, namespace: str, user_id: str, code: str):
        pod_name = f"{user_id}-test"
        code = code.replace("'", "'\\''")  # Escape single quotes
        command = f"echo '{code}' > /app/code.py"
        try:
            # Use kubectl exec instead of client API
            result = subprocess.run(
                ["kubectl", "exec", pod_name, "-n", namespace, "--", "/bin/sh", "-c", command],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stderr:
                raise Exception(f"Failed to inject code: {result.stderr}")
            logger.info(f"Code injected into {pod_name}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to inject code: {e.stderr}")

    def get_test_pod_logs(self, namespace: str, user_id: str):
        pod_name = f"{user_id}-test"
        return self.core_v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)

    def create_production_environment(self, namespace: str, user_id: str, code: str):

        # Delete existing deployments if they exist
        try:
            self.apps_v1.delete_namespaced_deployment(name=f"{user_id}-prod", namespace=namespace)
            logger.info(f"Deleted existing deployment {user_id}-prod")
        except client.ApiException as e:
            if e.status != 404:  # Ignore if it doesn't exist
                logger.error(f"Failed to delete existing deployment {user_id}-prod: {str(e)}")
        try:
            self.apps_v1.delete_namespaced_deployment(name=f"{user_id}-prod-db", namespace=namespace)
            logger.info(f"Deleted existing deployment {user_id}-prod-db")
        except client.ApiException as e:
            if e.status != 404:
                logger.error(f"Failed to delete existing deployment {user_id}-prod-db: {str(e)}")

        #create new deployment
        self.apps_v1.create_namespaced_deployment(
            namespace=namespace,
            body=client.V1Deployment(
                metadata=client.V1ObjectMeta(name=f"{user_id}-prod"),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(match_labels={"app": "prod"}),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(labels={"app": "prod"}),
                        spec=client.V1PodSpec(
                            containers=[client.V1Container(
                                name="prod",
                                image="python:3.9-slim",
                                command=["python", "-c", f"{code}; while True: time.sleep(60)"]
                            )]
                        )
                    )
                )
            )
        )
        self.apps_v1.create_namespaced_deployment(
            namespace=namespace,
            body=client.V1Deployment(
                metadata=client.V1ObjectMeta(name=f"{user_id}-prod-db"),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(match_labels={"app": "prod-db"}),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(labels={"app": "prod-db"}),
                        spec=client.V1PodSpec(
                            containers=[client.V1Container(
                                name="prod-db",
                                image="postgres:13",
                                env=[client.V1EnvVar(name="POSTGRES_PASSWORD", value="password")]
                            )]
                        )
                    )
                )
            )
        )

