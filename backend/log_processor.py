from elasticsearch import Elasticsearch
import logging
import json
import os
from datetime import datetime
import time

class LogProcessor:
    def __init__(self):
        host = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
        self.logger = logging.getLogger("orchestration")
        self.es = None
        time.sleep(10)
        # Wait for Elasticsearch to be ready
        for _ in range(70):  # Try for 70 seconds
            try:
                self.es = Elasticsearch(host)
                if self.es.ping():
                    self.logger.info("Connected to Elasticsearch")
                    break
            except Exception as e:
                self.logger.warning(f"Waiting for Elasticsearch: {str(e)}")
                time.sleep(2)
        if not self.es:
            self.logger.error("Failed to connect to Elasticsearch after timeout")
            self.logger = None

    def process_log(self, log_data: dict):
        """Structure and store logs in Elasticsearch"""
        if not self.es:
            self.logger.error("Elasticsearch not available, skipping log")
            return
        try:
            doc = {
                "@timestamp": datetime.now().isoformat(),
                "namespace": log_data.get("namespace"),
                "user": log_data.get("user"),
                "message": log_data.get("message"),
                "severity": log_data.get("level", "INFO")
            }
            self.es.index(index="orchestration-logs", body=doc)
        except Exception as e:
            self.logger.error(f"Log processing failed: {str(e)}")
