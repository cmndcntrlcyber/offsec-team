FROM python:3.11-slim

LABEL maintainer="C3S-ATTCK Team"
LABEL description="Service Health Monitoring"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for monitoring
RUN pip install --no-cache-dir \
    requests \
    psutil \
    prometheus-client \
    schedule

# Copy monitoring scripts
COPY health-check.sh /app/
COPY . /app/

# Make scripts executable
RUN chmod +x /app/health-check.sh

# Create data directory
RUN mkdir -p /app/data

# Create monitoring script
RUN echo '#!/usr/bin/env python3' > /app/monitoring.py && \
    echo 'import time' >> /app/monitoring.py && \
    echo 'import requests' >> /app/monitoring.py && \
    echo 'import os' >> /app/monitoring.py && \
    echo 'import json' >> /app/monitoring.py && \
    echo 'import logging' >> /app/monitoring.py && \
    echo 'from datetime import datetime' >> /app/monitoring.py && \
    echo 'from prometheus_client import start_http_server, Gauge, Counter' >> /app/monitoring.py && \
    echo '' >> /app/monitoring.py && \
    echo '# Setup logging' >> /app/monitoring.py && \
    echo 'logging.basicConfig(level=logging.INFO)' >> /app/monitoring.py && \
    echo 'logger = logging.getLogger(__name__)' >> /app/monitoring.py && \
    echo '' >> /app/monitoring.py && \
    echo '# Prometheus metrics' >> /app/monitoring.py && \
    echo 'service_health = Gauge("service_health", "Service health status", ["service"])' >> /app/monitoring.py && \
    echo 'service_response_time = Gauge("service_response_time_seconds", "Service response time", ["service"])' >> /app/monitoring.py && \
    echo 'health_check_counter = Counter("health_checks_total", "Total health checks", ["service", "status"])' >> /app/monitoring.py && \
    echo '' >> /app/monitoring.py && \
    echo 'class ServiceMonitor:' >> /app/monitoring.py && \
    echo '    def __init__(self):' >> /app/monitoring.py && \
    echo '        self.services = os.getenv("SERVICES", "").split(",")' >> /app/monitoring.py && \
    echo '        self.gateway_url = os.getenv("GATEWAY_URL", "http://gateway:8005")' >> /app/monitoring.py && \
    echo '        self.check_interval = int(os.getenv("CHECK_INTERVAL", "30"))' >> /app/monitoring.py && \
    echo '        ' >> /app/monitoring.py && \
    echo '    def check_service_health(self, service_name: str, url: str) -> dict:' >> /app/monitoring.py && \
    echo '        """Check health of a specific service"""' >> /app/monitoring.py && \
    echo '        try:' >> /app/monitoring.py && \
    echo '            start_time = time.time()' >> /app/monitoring.py && \
    echo '            response = requests.get(f"{url}/health", timeout=10)' >> /app/monitoring.py && \
    echo '            response_time = time.time() - start_time' >> /app/monitoring.py && \
    echo '            ' >> /app/monitoring.py && \
    echo '            is_healthy = response.status_code == 200' >> /app/monitoring.py && \
    echo '            ' >> /app/monitoring.py && \
    echo '            # Update Prometheus metrics' >> /app/monitoring.py && \
    echo '            service_health.labels(service=service_name).set(1 if is_healthy else 0)' >> /app/monitoring.py && \
    echo '            service_response_time.labels(service=service_name).set(response_time)' >> /app/monitoring.py && \
    echo '            health_check_counter.labels(service=service_name, status="success" if is_healthy else "failure").inc()' >> /app/monitoring.py && \
    echo '            ' >> /app/monitoring.py && \
    echo '            return {' >> /app/monitoring.py && \
    echo '                "service": service_name,' >> /app/monitoring.py && \
    echo '                "healthy": is_healthy,' >> /app/monitoring.py && \
    echo '                "response_time": response_time,' >> /app/monitoring.py && \
    echo '                "status_code": response.status_code,' >> /app/monitoring.py && \
    echo '                "timestamp": datetime.now().isoformat()' >> /app/monitoring.py && \
    echo '            }' >> /app/monitoring.py && \
    echo '            ' >> /app/monitoring.py && \
    echo '        except Exception as e:' >> /app/monitoring.py && \
    echo '            logger.error(f"Health check failed for {service_name}: {e}")' >> /app/monitoring.py && \
    echo '            service_health.labels(service=service_name).set(0)' >> /app/monitoring.py && \
    echo '            health_check_counter.labels(service=service_name, status="error").inc()' >> /app/monitoring.py && \
    echo '            ' >> /app/monitoring.py && \
    echo '            return {' >> /app/monitoring.py && \
    echo '                "service": service_name,' >> /app/monitoring.py && \
    echo '                "healthy": False,' >> /app/monitoring.py && \
    echo '                "error": str(e),' >> /app/monitoring.py && \
    echo '                "timestamp": datetime.now().isoformat()' >> /app/monitoring.py && \
    echo '            }' >> /app/monitoring.py && \
    echo '    ' >> /app/monitoring.py && \
    echo '    def run_monitoring(self):' >> /app/monitoring.py && \
    echo '        """Main monitoring loop"""' >> /app/monitoring.py && \
    echo '        logger.info("Starting service monitoring...")' >> /app/monitoring.py && \
    echo '        ' >> /app/monitoring.py && \
    echo '        service_urls = {' >> /app/monitoring.py && \
    echo '            "gateway": self.gateway_url,' >> /app/monitoring.py && \
    echo '            "chat-service": "http://chat-service:8080",' >> /app/monitoring.py && \
    echo '            "tools-service": "http://tools-service:8001",' >> /app/monitoring.py && \
    echo '            "research-service": "http://research-service:8002",' >> /app/monitoring.py && \
    echo '            "mcp-service": "http://mcp-service:8003",' >> /app/monitoring.py && \
    echo '            "rtpi-pen": "http://rtpi-pen:8080"' >> /app/monitoring.py && \
    echo '        }' >> /app/monitoring.py && \
    echo '        ' >> /app/monitoring.py && \
    echo '        while True:' >> /app/monitoring.py && \
    echo '            try:' >> /app/monitoring.py && \
    echo '                results = []' >> /app/monitoring.py && \
    echo '                ' >> /app/monitoring.py && \
    echo '                for service_name in self.services:' >> /app/monitoring.py && \
    echo '                    if service_name in service_urls:' >> /app/monitoring.py && \
    echo '                        result = self.check_service_health(service_name, service_urls[service_name])' >> /app/monitoring.py && \
    echo '                        results.append(result)' >> /app/monitoring.py && \
    echo '                        ' >> /app/monitoring.py && \
    echo '                        status = "✅" if result["healthy"] else "❌"' >> /app/monitoring.py && \
    echo '                        logger.info(f"{status} {service_name}: {result.get(\"response_time\", \"N/A\")}s")' >> /app/monitoring.py && \
    echo '                ' >> /app/monitoring.py && \
    echo '                # Save results' >> /app/monitoring.py && \
    echo '                with open("/app/data/health_results.json", "w") as f:' >> /app/monitoring.py && \
    echo '                    json.dump(results, f, indent=2)' >> /app/monitoring.py && \
    echo '                ' >> /app/monitoring.py && \
    echo '                time.sleep(self.check_interval)' >> /app/monitoring.py && \
    echo '                ' >> /app/monitoring.py && \
    echo '            except KeyboardInterrupt:' >> /app/monitoring.py && \
    echo '                logger.info("Monitoring stopped")' >> /app/monitoring.py && \
    echo '                break' >> /app/monitoring.py && \
    echo '            except Exception as e:' >> /app/monitoring.py && \
    echo '                logger.error(f"Monitoring error: {e}")' >> /app/monitoring.py && \
    echo '                time.sleep(self.check_interval)' >> /app/monitoring.py && \
    echo '' >> /app/monitoring.py && \
    echo 'if __name__ == "__main__":' >> /app/monitoring.py && \
    echo '    # Start Prometheus metrics server' >> /app/monitoring.py && \
    echo '    start_http_server(9090)' >> /app/monitoring.py && \
    echo '    ' >> /app/monitoring.py && \
    echo '    # Start monitoring' >> /app/monitoring.py && \
    echo '    monitor = ServiceMonitor()' >> /app/monitoring.py && \
    echo '    monitor.run_monitoring()' >> /app/monitoring.py && \
    chmod +x /app/monitoring.py

# Health check for the monitor itself
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:9090/metrics || exit 1

# Expose metrics port
EXPOSE 9090

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run monitoring
CMD ["python", "/app/monitoring.py"]
