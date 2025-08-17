import os
import json
import yaml
import subprocess
import time
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from pydantic import BaseModel, Field

class CIPipelineManager:
    """
    A tool for automating testing and deployment pipelines.
    Provides capabilities for creating CI configurations, executing tests, and managing deployment workflows.
    """
    
    def __init__(self):
        self.pipeline_templates = {
            "github_actions": {
                "python": self._get_github_actions_python_template(),
                "rust": self._get_github_actions_rust_template(),
                "go": self._get_github_actions_go_template(),
                "docker": self._get_github_actions_docker_template()
            },
            "gitlab_ci": {
                "python": self._get_gitlab_ci_python_template(),
                "rust": self._get_gitlab_ci_rust_template(),
                "go": self._get_gitlab_ci_go_template(),
                "docker": self._get_gitlab_ci_docker_template()
            },
            "jenkins": {
                "python": self._get_jenkins_python_template(),
                "rust": self._get_jenkins_rust_template(),
                "go": self._get_jenkins_go_template(),
                "docker": self._get_jenkins_docker_template()
            }
        }
        
        self.test_configurations = {
            "python": {
                "unit": self._get_python_unit_test_config(),
                "integration": self._get_python_integration_test_config(),
                "security": self._get_python_security_test_config()
            },
            "rust": {
                "unit": self._get_rust_unit_test_config(),
                "integration": self._get_rust_integration_test_config(),
                "security": self._get_rust_security_test_config()
            },
            "go": {
                "unit": self._get_go_unit_test_config(),
                "integration": self._get_go_integration_test_config(),
                "security": self._get_go_security_test_config()
            }
        }
        
        self.deployment_workflows = {
            "kubernetes": self._get_kubernetes_deployment_workflow(),
            "aws": self._get_aws_deployment_workflow(),
            "azure": self._get_azure_deployment_workflow(),
            "gcp": self._get_gcp_deployment_workflow(),
            "docker_compose": self._get_docker_compose_deployment_workflow()
        }
        
        self.workflow_history = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("CIPipelineManager")
    
    def create_pipeline_configuration(self, repo_url: str = Field(..., description="Repository URL or path"), 
                                    language: str = Field(..., description="Programming language"),
                                    ci_system: str = Field("github_actions", description="CI system to use"),
                                    config_options: Dict[str, Any] = Field({}, description="Additional configuration options")) -> Dict[str, Any]:
        """
        Generate CI pipeline configurations.
        
        Args:
            repo_url: Repository URL or path
            language: Programming language (python, rust, go, docker)
            ci_system: CI system to use (github_actions, gitlab_ci, jenkins)
            config_options: Additional configuration options
                - test_types: List of test types to include (unit, integration, security)
                - environments: List of deployment environments (development, staging, production)
                - notification_email: Email for notifications
                - custom_steps: List of custom steps to add
            
        Returns:
            Dictionary containing the generated configuration and metadata
        """
        # Validate language
        language = language.lower()
        if language not in ["python", "rust", "go", "docker"]:
            return {
                "success": False,
                "error": f"Unsupported language '{language}'. Supported languages: python, rust, go, docker"
            }
        
        # Validate CI system
        ci_system = ci_system.lower()
        if ci_system not in ["github_actions", "gitlab_ci", "jenkins"]:
            return {
                "success": False,
                "error": f"Unsupported CI system '{ci_system}'. Supported systems: github_actions, gitlab_ci, jenkins"
            }
        
        # Generate pipeline configuration
        try:
            # Get base template
            template = self.pipeline_templates[ci_system][language]
            
            # Process configuration options
            test_types = config_options.get("test_types", ["unit"])
            environments = config_options.get("environments", ["development"])
            notification_email = config_options.get("notification_email", "admin@example.com")
            custom_steps = config_options.get("custom_steps", [])
            
            # Apply configuration options to template
            config = self._process_template(template, {
                "repo_url": repo_url,
                "language": language,
                "test_types": test_types,
                "environments": environments,
                "notification_email": notification_email,
                "custom_steps": custom_steps
            })
            
            # Generate file name based on CI system
            if ci_system == "github_actions":
                filename = ".github/workflows/ci.yml"
            elif ci_system == "gitlab_ci":
                filename = ".gitlab-ci.yml"
            else:  # jenkins
                filename = "Jenkinsfile"
            
            # Log generation
            workflow_id = f"pipeline-{int(time.time())}"
            self.workflow_history[workflow_id] = {
                "type": "pipeline_creation",
                "repo_url": repo_url,
                "language": language,
                "ci_system": ci_system,
                "options": config_options,
                "filename": filename,
                "timestamp": time.time()
            }
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "filename": filename,
                "configuration": config,
                "message": f"Successfully generated {ci_system} pipeline configuration for {language}"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating pipeline configuration: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_test_suite(self, test_config: Dict[str, Any] = Field(..., description="Test configuration")) -> Dict[str, Any]:
        """
        Run automated test suites against code.
        
        Args:
            test_config: Test configuration
                Required keys:
                - language: Programming language (python, rust, go)
                - test_types: List of test types to run (unit, integration, security)
                - code_path: Path to code to test
                Optional keys:
                - timeout: Test timeout in seconds (default: 300)
                - parallel: Run tests in parallel (default: False)
                - coverage_threshold: Minimum coverage percentage (default: 80)
            
        Returns:
            Dictionary containing test results
        """
        # Validate test configuration
        required_keys = ["language", "test_types", "code_path"]
        for key in required_keys:
            if key not in test_config:
                return {
                    "success": False,
                    "error": f"Missing required key '{key}' in test configuration"
                }
        
        # Extract configuration
        language = test_config["language"].lower()
        test_types = test_config["test_types"]
        code_path = test_config["code_path"]
        timeout = test_config.get("timeout", 300)
        parallel = test_config.get("parallel", False)
        coverage_threshold = test_config.get("coverage_threshold", 80)
        
        # Validate language
        if language not in ["python", "rust", "go"]:
            return {
                "success": False,
                "error": f"Unsupported language '{language}'. Supported languages: python, rust, go"
            }
        
        # Validate test types
        for test_type in test_types:
            if test_type not in ["unit", "integration", "security"]:
                return {
                    "success": False,
                    "error": f"Unsupported test type '{test_type}'. Supported types: unit, integration, security"
                }
        
        # In a real implementation, we would execute actual test commands
        # For this implementation, we'll simulate test execution
        
        # Generate workflow ID
        workflow_id = f"test-{int(time.time())}"
        
        # Log test execution
        self.workflow_history[workflow_id] = {
            "type": "test_execution",
            "language": language,
            "test_types": test_types,
            "code_path": code_path,
            "timeout": timeout,
            "parallel": parallel,
            "coverage_threshold": coverage_threshold,
            "status": "running",
            "timestamp": time.time()
        }
        
        try:
            # Simulate test execution
            self.logger.info(f"Executing {', '.join(test_types)} tests for {language} code in {code_path}")
            
            test_results = {}
            overall_success = True
            
            for test_type in test_types:
                # Get test configuration
                test_config = self.test_configurations[language][test_type]
                
                # Simulate test execution
                test_result = self._simulate_test_execution(language, test_type, code_path, test_config)
                test_results[test_type] = test_result
                
                # Update overall success
                if not test_result["success"]:
                    overall_success = False
            
            # Calculate coverage
            coverage = self._calculate_simulated_coverage(language, test_types, code_path)
            coverage_success = coverage >= coverage_threshold
            
            if not coverage_success:
                overall_success = False
            
            # Update workflow history
            self.workflow_history[workflow_id]["status"] = "completed"
            self.workflow_history[workflow_id]["success"] = overall_success
            self.workflow_history[workflow_id]["results"] = test_results
            self.workflow_history[workflow_id]["coverage"] = coverage
            
            return {
                "success": overall_success,
                "workflow_id": workflow_id,
                "results": test_results,
                "coverage": coverage,
                "coverage_threshold": coverage_threshold,
                "coverage_met": coverage_success,
                "message": "All tests passed successfully" if overall_success else "Some tests failed"
            }
            
        except Exception as e:
            self.logger.error(f"Error executing test suite: {str(e)}")
            self.workflow_history[workflow_id]["status"] = "failed"
            self.workflow_history[workflow_id]["error"] = str(e)
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e)
            }
    
    def manage_deployment_workflow(self, workflow_id: str = Field(..., description="ID of the workflow to manage"), 
                                 environment: str = Field("development", description="Deployment environment")) -> Dict[str, Any]:
        """
        Orchestrate deployment processes.
        
        Args:
            workflow_id: ID of the workflow to manage
            environment: Deployment environment (development, staging, production)
            
        Returns:
            Dictionary containing deployment status and information
        """
        # Validate workflow ID
        if workflow_id not in self.workflow_history:
            return {
                "success": False,
                "error": f"Workflow ID '{workflow_id}' not found"
            }
        
        # Validate environment
        valid_environments = ["development", "staging", "production"]
        if environment not in valid_environments:
            return {
                "success": False,
                "error": f"Invalid environment '{environment}'. Valid environments: {', '.join(valid_environments)}"
            }
        
        # Get workflow
        workflow = self.workflow_history[workflow_id]
        
        # Check if it's a test workflow
        if workflow["type"] != "test_execution":
            return {
                "success": False,
                "error": f"Workflow '{workflow_id}' is not a test execution workflow"
            }
        
        # Check if tests passed
        if workflow.get("status") != "completed" or not workflow.get("success", False):
            return {
                "success": False,
                "error": f"Cannot deploy workflow '{workflow_id}' because tests did not complete successfully"
            }
        
        # Determine deployment strategy based on language and environment
        language = workflow["language"]
        deployment_strategy = "kubernetes"  # Default strategy
        
        if environment == "development":
            deployment_strategy = "docker_compose"
        elif environment == "staging":
            if language == "python":
                deployment_strategy = "aws"
            elif language == "rust":
                deployment_strategy = "kubernetes"
            else:  # go
                deployment_strategy = "gcp"
        else:  # production
            if language == "python":
                deployment_strategy = "aws"
            elif language == "rust":
                deployment_strategy = "kubernetes"
            else:  # go
                deployment_strategy = "gcp"
        
        # Get deployment workflow
        deployment_workflow = self.deployment_workflows[deployment_strategy]
        
        # Generate deployment ID
        deployment_id = f"deploy-{int(time.time())}"
        
        # Log deployment
        self.workflow_history[deployment_id] = {
            "type": "deployment",
            "parent_workflow": workflow_id,
            "language": language,
            "environment": environment,
            "deployment_strategy": deployment_strategy,
            "status": "deploying",
            "timestamp": time.time()
        }
        
        try:
            # Simulate deployment
            self.logger.info(f"Deploying {language} application to {environment} environment using {deployment_strategy}")
            
            # Perform deployment steps
            deployment_result = self._simulate_deployment(deployment_id, workflow, environment, deployment_strategy, deployment_workflow)
            
            # Update workflow history
            self.workflow_history[deployment_id]["status"] = "completed" if deployment_result["success"] else "failed"
            self.workflow_history[deployment_id]["result"] = deployment_result
            
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"Error managing deployment workflow: {str(e)}")
            self.workflow_history[deployment_id]["status"] = "failed"
            self.workflow_history[deployment_id]["error"] = str(e)
            
            return {
                "success": False,
                "deployment_id": deployment_id,
                "error": str(e)
            }
    
    def _process_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Process template by replacing variables"""
        result = template
        
        # Replace simple variables
        for key, value in variables.items():
            if isinstance(value, str):
                result = result.replace(f"{{{{var.{key}}}}}", value)
        
        # Process test types
        if "test_types" in variables:
            test_section = ""
            for test_type in variables["test_types"]:
                test_section += f"      - {test_type}\n"
            result = result.replace("{{var.test_section}}", test_section)
        
        # Process environments
        if "environments" in variables:
            env_section = ""
            for env in variables["environments"]:
                env_section += f"      - {env}\n"
            result = result.replace("{{var.env_section}}", env_section)
        
        # Process custom steps
        if "custom_steps" in variables and variables["custom_steps"]:
            custom_section = "\n"
            for step in variables["custom_steps"]:
                custom_section += f"    - name: {step['name']}\n"
                custom_section += f"      run: {step['command']}\n"
            result = result.replace("{{var.custom_section}}", custom_section)
        else:
            result = result.replace("{{var.custom_section}}", "")
        
        return result
    
    def _simulate_test_execution(self, language: str, test_type: str, code_path: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate test execution (for demonstration purposes)"""
        self.logger.info(f"Running {test_type} tests for {language} code in {code_path}")
        
        # Simulate test execution time
        time.sleep(0.5)
        
        # Generate random test results (90% success rate)
        import random
        success = random.random() < 0.9
        
        if success:
            self.logger.info(f"{test_type.capitalize()} tests passed successfully")
            
            # Generate simulated test details
            test_count = random.randint(10, 100)
            failed_count = 0
            skipped_count = random.randint(0, 5)
            
            return {
                "success": True,
                "test_count": test_count,
                "passed_count": test_count - failed_count - skipped_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "duration_seconds": random.randint(1, 30)
            }
        else:
            self.logger.warning(f"{test_type.capitalize()} tests failed")
            
            # Generate simulated test details
            test_count = random.randint(10, 100)
            failed_count = random.randint(1, 5)
            skipped_count = random.randint(0, 5)
            
            return {
                "success": False,
                "test_count": test_count,
                "passed_count": test_count - failed_count - skipped_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "duration_seconds": random.randint(1, 30),
                "failures": [
                    {
                        "name": f"test_function_{i}",
                        "message": f"Assertion failed: expected value not equal to actual value",
                        "file": f"{code_path}/tests/test_{i}.{language}"
                    } for i in range(1, failed_count + 1)
                ]
            }
    
    def _calculate_simulated_coverage(self, language: str, test_types: List[str], code_path: str) -> float:
        """Calculate simulated code coverage (for demonstration purposes)"""
        # Base coverage based on language
        if language == "python":
            base_coverage = 85.0
        elif language == "rust":
            base_coverage = 90.0
        else:  # go
            base_coverage = 88.0
        
        # Adjust coverage based on test types
        coverage_adjustment = 0.0
        
        if "unit" in test_types:
            coverage_adjustment += 5.0
        
        if "integration" in test_types:
            coverage_adjustment += 3.0
        
        if "security" in test_types:
            coverage_adjustment += 2.0
        
        # Apply a small random variation
        import random
        random_adjustment = random.uniform(-5.0, 5.0)
        
        # Calculate final coverage
        coverage = min(100.0, max(0.0, base_coverage + coverage_adjustment + random_adjustment))
        
        return round(coverage, 2)
    
    def _simulate_deployment(self, deployment_id: str, workflow: Dict[str, Any], environment: str, strategy: str, deployment_workflow: str) -> Dict[str, Any]:
        """Simulate deployment process (for demonstration purposes)"""
        language = workflow["language"]
        code_path = workflow["code_path"]
        
        self.logger.info(f"Deploying {language} application from {code_path} to {environment} environment using {strategy}")
        
        # Simulate deployment steps
        self.logger.info(f"Step 1: Preparing deployment...")
        time.sleep(0.5)
        
        self.logger.info(f"Step 2: Building artifacts...")
        time.sleep(1.0)
        
        self.logger.info(f"Step 3: Running pre-deployment checks...")
        time.sleep(0.5)
        
        self.logger.info(f"Step 4: Deploying to {environment}...")
        time.sleep(1.0)
        
        self.logger.info(f"Step 5: Running post-deployment tests...")
        time.sleep(0.5)
        
        # Simulate deployment success (95% success rate)
        import random
        success = random.random() < 0.95
        
        if success:
            self.logger.info(f"Deployment to {environment} completed successfully")
            
            # Generate deployment URL based on environment
            if environment == "development":
                url = "http://localhost:8080"
            elif environment == "staging":
                url = f"https://staging.example.com/{language}-app"
            else:  # production
                url = f"https://example.com/{language}-app"
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "environment": environment,
                "strategy": strategy,
                "url": url,
                "timestamp": time.time()
            }
        else:
            self.logger.warning(f"Deployment to {environment} failed")
            
            return {
                "success": False,
                "deployment_id": deployment_id,
                "environment": environment,
                "strategy": strategy,
                "error": "Deployment failed due to infrastructure issues",
                "timestamp": time.time()
            }
    
    # Template methods
    def _get_github_actions_python_template(self) -> str:
        return """name: CI/CD Pipeline

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10"]
        test-type: {{var.test_section}}

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 pytest pytest-cov
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        if [ -f dev-requirements.txt ]; then pip install -r dev-requirements.txt; fi
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Test with pytest
      run: |
        pytest --cov=./ --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3{{var.custom_section}}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    strategy:
      matrix:
        environment: {{var.env_section}}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Deploy to ${{ matrix.environment }}
      run: |
        echo "Deploying to ${{ matrix.environment }}"
        # Add deployment commands here
    
    - name: Notify deployment
      run: |
        echo "Notifying deployment to {{var.notification_email}}"
"""
    
    def _get_github_actions_rust_template(self) -> str:
        return """name: CI/CD Pipeline

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        rust-version: [stable, beta]
        test-type: {{var.test_section}}

    steps:
    - uses: actions/checkout@v3
    - name: Set up Rust ${{ matrix.rust-version }}
      uses: actions-rs/toolchain@v1
      with:
        profile: minimal
        toolchain: ${{ matrix.rust-version }}
        override: true
        components: rustfmt, clippy
    
    - name: Check formatting
      uses: actions-rs/cargo@v1
      with:
        command: fmt
        args: --all -- --check
    
    - name: Lint with clippy
      uses: actions-rs/cargo@v1
      with:
        command: clippy
        args: -- -D warnings
    
    - name: Build
      uses: actions-rs/cargo@v1
      with:
        command: build
    
    - name: Test
      uses: actions-rs/cargo@v1
      with:
        command: test
        args: --all-features{{var.custom_section}}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    strategy:
      matrix:
        environment: {{var.env_section}}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Rust
      uses: actions-rs/toolchain@v1
      with:
        profile: minimal
        toolchain: stable
        override: true
    
    - name: Build release binary
      uses: actions-rs/cargo@v1
      with:
        command: build
        args: --release
    
    - name: Deploy to ${{ matrix.environment }}
      run: |
        echo "Deploying to ${{ matrix.environment }}"
        # Add deployment commands here
    
    - name: Notify deployment
      run: |
        echo "Notifying deployment to {{var.notification_email}}"
"""
    
    def _get_github_actions_go_template(self) -> str:
        return """name: CI/CD Pipeline

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        go-version: [1.18, 1.19]
        test-type: {{var.test_section}}

    steps:
    - uses: actions/checkout@v3
    - name: Set up Go ${{ matrix.go-version }}
      uses: actions/setup-go@v3
      with:
        go-version: ${{ matrix.go-version }}
    
    - name: Install dependencies
      run: |
        go mod download
        go install honnef.co/go/tools/cmd/staticcheck@latest
    
    - name: Verify dependencies
      run: go mod verify
    
    - name: Build
      run: go build -v ./...
    
    - name: Run staticcheck
      run: staticcheck ./...
    
    - name: Run tests
      run: go test -race -coverprofile=coverage.txt -covermode=atomic ./...
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3{{var.custom_section}}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    strategy:
      matrix:
        environment: {{var.env_section}}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Go
      uses: actions/setup-go@v3
      with:
        go-version: 1.19
    
    - name: Build release binary
      run: |
        GOOS=linux GOARCH=amd64 go build -o app-linux-amd64
    
    - name: Deploy to ${{ matrix.environment }}
      run: |
        echo "Deploying to ${{ matrix.environment }}"
        # Add deployment commands here
    
    - name: Notify deployment
      run: |
        echo "Notifying deployment to {{var.notification_email}}"
"""
    
    def _get_github_actions_docker_template(self) -> str:
        return """name: CI/CD Pipeline

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Cache Docker layers
      uses: actions/cache@v3
      with:
        path: /tmp/.buildx-cache
        key: ${{ runner.os }}-buildx-${{ github.sha }}
        restore-keys: |
          ${{ runner.os }}-buildx-
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v3
      with:
        context: .
        push: ${{ github.event_name != 'pull_request' }}
        tags: user/app:latest
        cache-from: type=local,src=/tmp/.buildx-cache
        cache-to: type=local,dest=/tmp/.buildx-cache-new{{var.custom_section}}
    
    # Temp fix for https://github.com/docker/build-push-action/issues/252
    - name: Move cache
      run: |
        rm -rf /tmp/.buildx-cache
        mv /tmp/.buildx-cache-new /tmp/.buildx-cache

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    strategy:
      matrix:
        environment: {{var.env_section}}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to ${{ matrix.environment }}
      run: |
        echo "Deploying to ${{ matrix.environment }}"
        # Add deployment commands here
    
    - name: Notify deployment
      run: |
        echo "Notifying deployment to {{var.notification_email}}"
"""
    
    def _get_gitlab_ci_python_template(self) -> str:
        return """stages:
  - test
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/

test:
  stage: test
  image: python:3.9
  script:
    - pip install --upgrade pip
    - pip install -r requirements.txt
    - pip install pytest pytest-cov flake8
    - flake8 .
    - pytest --cov=./
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

deploy:
  stage: deploy
  image: python:3.9
  script:
    - echo "Deploying application"
    - pip install -r requirements.txt
    # Add deployment commands here
  only:
    - main
    - master
  environment:
    name: {{var.environment}}
    url: https://{{var.environment}}.example.com
"""

    def _get_gitlab_ci_rust_template(self) -> str:
        return """stages:
  - test
  - deploy

test:
  stage: test
  image: rust:latest
  script:
    - cargo fmt --all -- --check
    - cargo clippy -- -D warnings
    - cargo build
    - cargo test --all-features

deploy:
  stage: deploy
  image: rust:latest
  script:
    - cargo build --release
    - echo "Deploying Rust application"
  only:
    - main
    - master
"""

    def _get_gitlab_ci_go_template(self) -> str:
        return """stages:
  - test
  - deploy

test:
  stage: test
  image: golang:1.19
  script:
    - go mod download
    - go vet ./...
    - go test -race -coverprofile=coverage.txt ./...

deploy:
  stage: deploy
  image: golang:1.19
  script:
    - go build -o app
    - echo "Deploying Go application"
  only:
    - main
    - master
"""

    def _get_gitlab_ci_docker_template(self) -> str:
        return """stages:
  - build
  - deploy

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_PROJECT_NAME:$CI_COMMIT_SHA .
    - docker tag $CI_PROJECT_NAME:$CI_COMMIT_SHA $CI_PROJECT_NAME:latest

deploy:
  stage: deploy
  image: docker:latest
  script:
    - docker push $CI_PROJECT_NAME:latest
    - echo "Deploying Docker application"
  only:
    - main
    - master
"""

    def _get_jenkins_python_template(self) -> str:
        return """pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
                sh 'pip install pytest pytest-cov flake8'
                sh 'flake8 .'
                sh 'pytest --cov=./ --cov-report=xml'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'echo "Deploying Python application"'
            }
        }
    }
}"""

    def _get_jenkins_rust_template(self) -> str:
        return """pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'cargo fmt --all -- --check'
                sh 'cargo clippy -- -D warnings'
                sh 'cargo build'
                sh 'cargo test --all-features'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'cargo build --release'
                sh 'echo "Deploying Rust application"'
            }
        }
    }
}"""

    def _get_jenkins_go_template(self) -> str:
        return """pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'go mod download'
                sh 'go vet ./...'
                sh 'go test -race -coverprofile=coverage.txt ./...'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'go build -o app'
                sh 'echo "Deploying Go application"'
            }
        }
    }
}"""

    def _get_jenkins_docker_template(self) -> str:
        return """pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t app:${BUILD_NUMBER} .'
                sh 'docker tag app:${BUILD_NUMBER} app:latest'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker push app:latest'
                sh 'echo "Deploying Docker application"'
            }
        }
    }
}"""

    # Test configuration methods
    def _get_python_unit_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "pytest",
            "command": "pytest tests/unit/",
            "coverage": True,
            "parallel": False
        }

    def _get_python_integration_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "pytest",
            "command": "pytest tests/integration/",
            "coverage": True,
            "parallel": True
        }

    def _get_python_security_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "bandit",
            "command": "bandit -r ./",
            "coverage": False,
            "parallel": False
        }

    def _get_rust_unit_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "cargo",
            "command": "cargo test --lib",
            "coverage": True,
            "parallel": True
        }

    def _get_rust_integration_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "cargo",
            "command": "cargo test --test '*'",
            "coverage": True,
            "parallel": True
        }

    def _get_rust_security_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "cargo-audit",
            "command": "cargo audit",
            "coverage": False,
            "parallel": False
        }

    def _get_go_unit_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "go test",
            "command": "go test ./...",
            "coverage": True,
            "parallel": True
        }

    def _get_go_integration_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "go test",
            "command": "go test -tags=integration ./...",
            "coverage": True,
            "parallel": True
        }

    def _get_go_security_test_config(self) -> Dict[str, Any]:
        return {
            "framework": "gosec",
            "command": "gosec ./...",
            "coverage": False,
            "parallel": False
        }

    # Deployment workflow methods
    def _get_kubernetes_deployment_workflow(self) -> str:
        return "kubectl apply -f k8s/"

    def _get_aws_deployment_workflow(self) -> str:
        return "aws deploy push --application-name app"

    def _get_azure_deployment_workflow(self) -> str:
        return "az webapp deployment source config"

    def _get_gcp_deployment_workflow(self) -> str:
        return "gcloud app deploy"

    def _get_docker_compose_deployment_workflow(self) -> str:
        return "docker-compose up -d"
