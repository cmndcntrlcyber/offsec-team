import os
import json
import re
import time
import logging
import subprocess
from typing import Dict, List, Optional, Tuple, Union, Any
from pydantic import BaseModel, Field

class FrameworkSecurityAnalyzer:
    """
    A tool for analyzing web framework security configurations.
    Provides capabilities for evaluating framework settings, finding security misconfigurations, and suggesting improvements.
    """
    
    def __init__(self):
        self.supported_frameworks = {
            "django": {
                "description": "Django web framework",
                "file_patterns": ["settings.py", "urls.py", "middleware.py"],
                "dependency_patterns": ["django==", "django>=", "Django==", "Django>="],
                "settings_analyzer": self._analyze_django_settings,
                "security_checklist": self._get_django_security_checklist()
            },
            "flask": {
                "description": "Flask web framework",
                "file_patterns": ["app.py", "config.py", "__init__.py"],
                "dependency_patterns": ["flask==", "flask>=", "Flask==", "Flask>="],
                "settings_analyzer": self._analyze_flask_settings,
                "security_checklist": self._get_flask_security_checklist()
            },
            "express": {
                "description": "Express.js web framework",
                "file_patterns": ["app.js", "server.js", "index.js"],
                "dependency_patterns": ["express", "express:"],
                "settings_analyzer": self._analyze_express_settings,
                "security_checklist": self._get_express_security_checklist
            },
            "rails": {
                "description": "Ruby on Rails web framework",
                "file_patterns": ["config/application.rb", "config/environments/", "Gemfile"],
                "dependency_patterns": ["rails", "Rails"],
                "settings_analyzer": self._analyze_rails_settings,
                "security_checklist": self._get_rails_security_checklist()
            },
            "laravel": {
                "description": "Laravel PHP framework",
                "file_patterns": ["config/app.php", ".env", "composer.json"],
                "dependency_patterns": ["laravel/framework", "Laravel"],
                "settings_analyzer": self._analyze_laravel_settings,
                "security_checklist": self._get_laravel_security_checklist()
            }
        }
        
        self.analysis_history = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("FrameworkSecurityAnalyzer")
    
    def detect_framework(self, project_path: str = Field(..., description="Path to the project to analyze")) -> Dict[str, Any]:
        """
        Detect which web framework a project is using.
        
        Args:
            project_path: Path to the project to analyze
            
        Returns:
            Dictionary containing detection results
        """
        # Validate parameters
        if not project_path:
            return {
                "success": False,
                "error": "Project path is required"
            }
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path '{project_path}' does not exist"
            }
        
        # Initialize results
        frameworks_detected = []
        evidence = []
        
        try:
            self.logger.info(f"Detecting framework for project at {project_path}")
            
            # Check for dependency files
            dependency_files = {
                "requirements.txt": self._check_python_requirements,
                "Pipfile": self._check_pipfile,
                "package.json": self._check_package_json,
                "Gemfile": self._check_gemfile,
                "composer.json": self._check_composer_json
            }
            
            for filename, checker in dependency_files.items():
                filepath = os.path.join(project_path, filename)
                if os.path.exists(filepath):
                    # Found a dependency file, check for framework dependencies
                    dep_results = checker(filepath)
                    if dep_results["frameworks"]:
                        frameworks_detected.extend(dep_results["frameworks"])
                        evidence.append({
                            "type": "dependency_file",
                            "file": filename,
                            "frameworks": dep_results["frameworks"],
                            "details": dep_results["details"]
                        })
            
            # Check for framework-specific files
            for framework, config in self.supported_frameworks.items():
                file_patterns = config["file_patterns"]
                
                for pattern in file_patterns:
                    # Search for files matching the pattern
                    matching_files = self._find_files_matching_pattern(project_path, pattern)
                    
                    if matching_files:
                        if framework not in frameworks_detected:
                            frameworks_detected.append(framework)
                        
                        evidence.append({
                            "type": "file_pattern",
                            "framework": framework,
                            "pattern": pattern,
                            "matching_files": matching_files
                        })
            
            # If no frameworks detected, try content-based detection
            if not frameworks_detected:
                content_detection = self._detect_framework_from_content(project_path)
                if content_detection["frameworks"]:
                    frameworks_detected.extend(content_detection["frameworks"])
                    evidence.append({
                        "type": "code_content",
                        "details": content_detection["details"]
                    })
            
            # Remove duplicates while preserving order
            unique_frameworks = []
            for framework in frameworks_detected:
                if framework not in unique_frameworks:
                    unique_frameworks.append(framework)
            
            # Generate detection ID
            detection_id = f"framework-detection-{int(time.time())}"
            
            # Store detection results
            self.analysis_history[detection_id] = {
                "type": "framework_detection",
                "project_path": project_path,
                "frameworks_detected": unique_frameworks,
                "evidence": evidence,
                "timestamp": time.time()
            }
            
            return {
                "success": True,
                "detection_id": detection_id,
                "frameworks_detected": unique_frameworks,
                "evidence": evidence
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting framework: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_security_settings(self, project_path: str = Field(..., description="Path to the project to analyze"), 
                                framework: str = Field(..., description="Framework to analyze")) -> Dict[str, Any]:
        """
        Analyze framework security settings and identify misconfigurations.
        
        Args:
            project_path: Path to the project to analyze
            framework: Framework to analyze (django, flask, express, rails, laravel)
            
        Returns:
            Dictionary containing analysis results
        """
        # Validate parameters
        if not project_path:
            return {
                "success": False,
                "error": "Project path is required"
            }
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path '{project_path}' does not exist"
            }
        
        framework = framework.lower()
        if framework not in self.supported_frameworks:
            return {
                "success": False,
                "error": f"Unsupported framework '{framework}'. Supported frameworks: {', '.join(self.supported_frameworks.keys())}"
            }
        
        try:
            self.logger.info(f"Analyzing security settings for {framework} project at {project_path}")
            
            # Get the settings analyzer for the framework
            analyzer = self.supported_frameworks[framework]["settings_analyzer"]
            
            # Analyze the settings
            analysis_results = analyzer(project_path)
            
            # Generate analysis ID
            analysis_id = f"{framework}-analysis-{int(time.time())}"
            
            # Store analysis results
            self.analysis_history[analysis_id] = {
                "type": "security_analysis",
                "project_path": project_path,
                "framework": framework,
                "results": analysis_results,
                "timestamp": time.time()
            }
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "framework": framework,
                "security_score": analysis_results["security_score"],
                "issues_found": len(analysis_results["issues"]),
                "critical_issues": analysis_results["issue_counts"]["critical"],
                "high_issues": analysis_results["issue_counts"]["high"],
                "medium_issues": analysis_results["issue_counts"]["medium"],
                "low_issues": analysis_results["issue_counts"]["low"],
                "results": analysis_results
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing security settings: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_security_recommendations(self, analysis_id: str = Field(..., description="ID of the analysis to use")) -> Dict[str, Any]:
        """
        Generate security recommendations based on analysis results.
        
        Args:
            analysis_id: ID of the analysis to use
            
        Returns:
            Dictionary containing recommendations
        """
        # Validate parameters
        if not analysis_id:
            return {
                "success": False,
                "error": "Analysis ID is required"
            }
        
        if analysis_id not in self.analysis_history:
            return {
                "success": False,
                "error": f"Analysis ID '{analysis_id}' not found"
            }
        
        analysis = self.analysis_history[analysis_id]
        if analysis["type"] != "security_analysis":
            return {
                "success": False,
                "error": f"Analysis ID '{analysis_id}' is not a security analysis"
            }
        
        try:
            self.logger.info(f"Generating recommendations for analysis {analysis_id}")
            
            framework = analysis["framework"]
            results = analysis["results"]
            
            # Generate recommendations based on issues
            recommendations = []
            code_examples = {}
            
            for issue in results["issues"]:
                recommendation = {
                    "issue_id": issue["id"],
                    "title": issue["title"],
                    "severity": issue["severity"],
                    "description": issue["description"],
                    "recommendation": issue["recommendation"],
                    "affected_files": issue.get("affected_files", []),
                    "references": issue.get("references", [])
                }
                
                # Add code example if available
                if "code_example" in issue:
                    code_key = f"{issue['id']}_code"
                    code_examples[code_key] = issue["code_example"]
                    recommendation["code_example_key"] = code_key
                
                recommendations.append(recommendation)
            
            # Sort recommendations by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            recommendations.sort(key=lambda x: severity_order.get(x["severity"], 4))
            
            # Generate a summary
            summary = {
                "framework": framework,
                "security_score": results["security_score"],
                "issues_count": len(results["issues"]),
                "issue_counts": results["issue_counts"],
                "top_issues": [rec["title"] for rec in recommendations[:3]] if recommendations else []
            }
            
            # Generate an action plan
            action_plan = []
            
            # Add critical and high issues to immediate action
            immediate_actions = [rec for rec in recommendations if rec["severity"] in ["critical", "high"]]
            if immediate_actions:
                action_plan.append({
                    "phase": "immediate",
                    "title": "Critical and High Priority Fixes",
                    "description": "These issues should be addressed immediately to protect against serious vulnerabilities",
                    "items": [{"title": item["title"], "issue_id": item["issue_id"]} for item in immediate_actions]
                })
            
            # Add medium issues to short-term action
            short_term_actions = [rec for rec in recommendations if rec["severity"] == "medium"]
            if short_term_actions:
                action_plan.append({
                    "phase": "short-term",
                    "title": "Medium Priority Fixes",
                    "description": "These issues should be addressed in the short term to improve security posture",
                    "items": [{"title": item["title"], "issue_id": item["issue_id"]} for item in short_term_actions]
                })
            
            # Add low issues to long-term action
            long_term_actions = [rec for rec in recommendations if rec["severity"] == "low"]
            if long_term_actions:
                action_plan.append({
                    "phase": "long-term",
                    "title": "Low Priority Fixes",
                    "description": "These issues should be addressed in the long term to enhance security",
                    "items": [{"title": item["title"], "issue_id": item["issue_id"]} for item in long_term_actions]
                })
            
            # Generate a unique ID for the recommendations
            recommendations_id = f"recommendations-{int(time.time())}"
            
            # Store recommendations
            self.analysis_history[recommendations_id] = {
                "type": "security_recommendations",
                "analysis_id": analysis_id,
                "framework": framework,
                "summary": summary,
                "recommendations": recommendations,
                "action_plan": action_plan,
                "code_examples": code_examples,
                "timestamp": time.time()
            }
            
            return {
                "success": True,
                "recommendations_id": recommendations_id,
                "framework": framework,
                "summary": summary,
                "recommendations": recommendations,
                "action_plan": action_plan,
                "code_examples": code_examples
            }
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_python_requirements(self, filepath: str) -> Dict[str, Any]:
        """Check requirements.txt for framework dependencies"""
        frameworks = []
        details = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
                for framework, config in self.supported_frameworks.items():
                    if framework in ["django", "flask"]:  # Python frameworks
                        for pattern in config["dependency_patterns"]:
                            if pattern in content:
                                frameworks.append(framework)
                                details.append({
                                    "framework": framework,
                                    "pattern": pattern,
                                    "file": filepath
                                })
                                break
        except Exception as e:
            self.logger.error(f"Error checking requirements.txt: {str(e)}")
        
        return {
            "frameworks": frameworks,
            "details": details
        }
    
    def _check_pipfile(self, filepath: str) -> Dict[str, Any]:
        """Check Pipfile for framework dependencies"""
        frameworks = []
        details = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
                for framework, config in self.supported_frameworks.items():
                    if framework in ["django", "flask"]:  # Python frameworks
                        for pattern in config["dependency_patterns"]:
                            if pattern.lower() in content.lower():
                                frameworks.append(framework)
                                details.append({
                                    "framework": framework,
                                    "pattern": pattern,
                                    "file": filepath
                                })
                                break
        except Exception as e:
            self.logger.error(f"Error checking Pipfile: {str(e)}")
        
        return {
            "frameworks": frameworks,
            "details": details
        }
    
    def _check_package_json(self, filepath: str) -> Dict[str, Any]:
        """Check package.json for framework dependencies"""
        frameworks = []
        details = []
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
                # Check dependencies and devDependencies
                dependencies = data.get("dependencies", {})
                devDependencies = data.get("devDependencies", {})
                all_dependencies = {**dependencies, **devDependencies}
                
                for framework, config in self.supported_frameworks.items():
                    if framework in ["express"]:  # JavaScript frameworks
                        for pattern in config["dependency_patterns"]:
                            pattern = pattern.replace(":", "")  # Remove colon for comparison
                            if pattern in all_dependencies:
                                frameworks.append(framework)
                                details.append({
                                    "framework": framework,
                                    "pattern": pattern,
                                    "version": all_dependencies[pattern],
                                    "file": filepath
                                })
                                break
        except Exception as e:
            self.logger.error(f"Error checking package.json: {str(e)}")
        
        return {
            "frameworks": frameworks,
            "details": details
        }
    
    def _check_gemfile(self, filepath: str) -> Dict[str, Any]:
        """Check Gemfile for framework dependencies"""
        frameworks = []
        details = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
                for framework, config in self.supported_frameworks.items():
                    if framework in ["rails"]:  # Ruby frameworks
                        for pattern in config["dependency_patterns"]:
                            if f"gem '{pattern}'" in content or f'gem "{pattern}"' in content:
                                frameworks.append(framework)
                                details.append({
                                    "framework": framework,
                                    "pattern": pattern,
                                    "file": filepath
                                })
                                break
        except Exception as e:
            self.logger.error(f"Error checking Gemfile: {str(e)}")
        
        return {
            "frameworks": frameworks,
            "details": details
        }
    
    def _check_composer_json(self, filepath: str) -> Dict[str, Any]:
        """Check composer.json for framework dependencies"""
        frameworks = []
        details = []
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
                # Check require and require-dev
                require = data.get("require", {})
                require_dev = data.get("require-dev", {})
                all_require = {**require, **require_dev}
                
                for framework, config in self.supported_frameworks.items():
                    if framework in ["laravel"]:  # PHP frameworks
                        for pattern in config["dependency_patterns"]:
                            if pattern in all_require:
                                frameworks.append(framework)
                                details.append({
                                    "framework": framework,
                                    "pattern": pattern,
                                    "version": all_require[pattern],
                                    "file": filepath
                                })
                                break
        except Exception as e:
            self.logger.error(f"Error checking composer.json: {str(e)}")
        
        return {
            "frameworks": frameworks,
            "details": details
        }
    
    def _find_files_matching_pattern(self, project_path: str, pattern: str) -> List[str]:
        """Find files matching a pattern"""
        matching_files = []
        
        # Check if pattern contains a directory separator
        if '/' in pattern:
            # Pattern contains directory, check exact path
            full_path = os.path.join(project_path, pattern)
            if os.path.exists(full_path):
                matching_files.append(full_path)
        else:
            # Pattern is a filename, search recursively
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file == pattern:
                        matching_files.append(os.path.join(root, file))
        
        return matching_files
    
    def _detect_framework_from_content(self, project_path: str) -> Dict[str, Any]:
        """Detect framework from file content"""
        frameworks = []
        details = []
        
        # Define content patterns for each framework
        content_patterns = {
            "django": [
                r"from\s+django\.",
                r"import\s+django",
                r"INSTALLED_APPS\s*=",
                r"MIDDLEWARE\s*="
            ],
            "flask": [
                r"from\s+flask\s+import",
                r"import\s+flask",
                r"Flask\(__name__\)"
            ],
            "express": [
                r"express\(\)",
                r"require\(['\"]express['\"]\)",
                r"app\.use\(",
                r"app\.get\("
            ],
            "rails": [
                r"Rails\.application",
                r"class\s+[A-Za-z0-9]+Controller\s*<\s*ApplicationController",
                r"ActiveRecord::Base"
            ],
            "laravel": [
                r"use\s+Illuminate\\",
                r"extends\s+Controller",
                r"Artisan::command"
            ]
        }
        
        # Maximum files to check per framework to avoid excessive scanning
        max_files_per_framework = 20
        
        # Check files for content patterns
        for framework, patterns in content_patterns.items():
            files_checked = 0
            framework_found = False
            
            # Get file extensions to check
            extensions = self._get_framework_file_extensions(framework)
            
            # Find files with matching extensions
            for root, dirs, files in os.walk(project_path):
                if files_checked >= max_files_per_framework or framework_found:
                    break
                
                for file in files:
                    if files_checked >= max_files_per_framework or framework_found:
                        break
                    
                    # Check if file has a relevant extension
                    if any(file.endswith(ext) for ext in extensions):
                        filepath = os.path.join(root, file)
                        files_checked += 1
                        
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                                # Check for patterns
                                for pattern in patterns:
                                    if re.search(pattern, content):
                                        frameworks.append(framework)
                                        details.append({
                                            "framework": framework,
                                            "pattern": pattern,
                                            "file": filepath
                                        })
                                        framework_found = True
                                        break
                        except Exception as e:
                            # Skip files that can't be read
                            pass
        
        return {
            "frameworks": frameworks,
            "details": details
        }
    
    def _get_framework_file_extensions(self, framework: str) -> List[str]:
        """Get file extensions for a framework"""
        if framework in ["django", "flask"]:
            return [".py"]
        elif framework == "express":
            return [".js", ".ts"]
        elif framework == "rails":
            return [".rb"]
        elif framework == "laravel":
            return [".php"]
        else:
            return []
    
    def _analyze_django_settings(self, project_path: str) -> Dict[str, Any]:
        """Analyze Django security settings"""
        self.logger.info(f"Analyzing Django security settings in {project_path}")
        
        # Initialize results
        results = {
            "security_score": 0,
            "issues": [],
            "issue_counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "checked_files": []
        }
        
        # Get Django security checklist
        checklist = self._get_django_security_checklist()
        
        # Find settings.py files
        settings_files = self._find_files_matching_pattern(project_path, "settings.py")
        results["checked_files"].extend(settings_files)
        
        # If no settings file found, try to find settings module
        if not settings_files:
            for root, dirs, files in os.walk(project_path):
                for dirname in dirs:
                    if dirname == "settings":
                        module_path = os.path.join(root, dirname)
                        for file in os.listdir(module_path):
                            if file.endswith(".py"):
                                settings_files.append(os.path.join(module_path, file))
        
        # If still no settings found, return empty results
        if not settings_files:
            results["issues"].append({
                "id": "django-no-settings",
                "title": "Django settings file not found",
                "severity": "medium",
                "description": "Could not find Django settings.py file to analyze",
                "recommendation": "Ensure your Django project has a proper settings file"
            })
            results["issue_counts"]["medium"] += 1
            results["security_score"] = 50  # Default middle score when can't analyze
            return results
        
        # Parse settings files
        settings = {}
        for filepath in settings_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Extract settings
                    for item in checklist:
                        setting_name = item["setting_name"]
                        pattern = rf"{setting_name}\s*=\s*(.+?)($|\n)"
                        matches = re.findall(pattern, content)
                        
                        if matches:
                            # Use the last match (in case of multiple definitions)
                            value_str = matches[-1][0].strip()
                            settings[setting_name] = self._parse_setting_value(value_str)
            except Exception as e:
                self.logger.error(f"Error parsing settings file {filepath}: {str(e)}")
                results["issues"].append({
                    "id": "django-settings-parse-error",
                    "title": f"Error parsing settings file: {os.path.basename(filepath)}",
                    "severity": "medium",
                    "description": f"Could not parse Django settings file: {str(e)}",
                    "recommendation": "Ensure your settings file is properly formatted",
                    "affected_files": [filepath]
                })
                results["issue_counts"]["medium"] += 1
        
        # Check settings against checklist
        for item in checklist:
            setting_name = item["setting_name"]
            secure_value = item["secure_value"]
            severity = item["severity"]
            
            # Check if setting exists
            if setting_name in settings:
                current_value = settings[setting_name]
                
                # Check if value is secure
                is_secure = self._compare_settings_values(current_value, secure_value, item.get("comparison", "equals"))
                
                if not is_secure:
                    # Add issue
                    results["issues"].append({
                        "id": f"django-{setting_name.lower().replace('_', '-')}",
                        "title": item["title"],
                        "severity": severity,
                        "description": item["description"],
                        "recommendation": item["recommendation"],
                        "current_value": str(current_value),
                        "secure_value": str(secure_value),
                        "affected_files": settings_files,
                        "references": item.get("references", []),
                        "code_example": item.get("code_example", "")
                    })
                    results["issue_counts"][severity] += 1
            elif item.get("required", False):
                # Required setting is missing
                results["issues"].append({
                    "id": f"django-missing-{setting_name.lower().replace('_', '-')}",
                    "title": f"Missing required security setting: {setting_name}",
                    "severity": severity,
                    "description": item["description"],
                    "recommendation": item["recommendation"],
                    "current_value": "Not set",
                    "secure_value": str(secure_value),
                    "affected_files": settings_files,
                    "references": item.get("references", []),
                    "code_example": item.get("code_example", "")
                })
                results["issue_counts"][severity] += 1
        
        # Calculate security score
        total_weight = sum(self._get_severity_weight(item["severity"]) for item in checklist if item.get("required", False))
        current_weight = total_weight
        
        for issue in results["issues"]:
            current_weight -= self._get_severity_weight(issue["severity"])
        
        if total_weight > 0:
            results["security_score"] = int((current_weight / total_weight) * 100)
        else:
            results["security_score"] = 100
        
        return results
    
    def _analyze_flask_settings(self, project_path: str) -> Dict[str, Any]:
        """Analyze Flask security settings"""
        self.logger.info(f"Analyzing Flask security settings in {project_path}")
        
        # Initialize results
        results = {
            "security_score": 0,
            "issues": [],
            "issue_counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "checked_files": []
        }
        
        # Get Flask security checklist
        checklist = self._get_flask_security_checklist()
        
        # Find Flask app files
        app_files = []
        for pattern in ["app.py", "__init__.py", "config.py"]:
            app_files.extend(self._find_files_matching_pattern(project_path, pattern))
        
        results["checked_files"].extend(app_files)
        
        # If no app files found, return empty results
        if not app_files:
            results["issues"].append({
                "id": "flask-no-app",
                "title": "Flask app file not found",
                "severity": "medium",
                "description": "Could not find Flask app file to analyze",
                "recommendation": "Ensure your Flask project has a proper app file"
            })
            results["issue_counts"]["medium"] += 1
            results["security_score"] = 50  # Default middle score when can't analyze
            return results
        
        # Parse app files
        settings = {}
        for filepath in app_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Extract settings
                    for item in checklist:
                        setting_name = item["setting_name"]
                        # Flask settings can be set in multiple ways
                        patterns = [
                            rf"app\.config\[\s*['\"]({setting_name})['\"]?\s*\]\s*=\s*(.+?)($|\n)",
                            rf"app\.config\.update\(.*?{setting_name}\s*:\s*(.+?)[,\}}]",
                            rf"{setting_name}\s*=\s*(.+?)($|\n)"
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            if matches:
                                # Use the last match (in case of multiple definitions)
                                value_str = matches[-1][0].strip() if len(matches[0]) > 1 else matches[-1][0].strip()
                                settings[setting_name] = self._parse_setting_value(value_str)
            except Exception as e:
                self.logger.error(f"Error parsing app file {filepath}: {str(e)}")
                results["issues"].append({
                    "id": "flask-settings-parse-error",
                    "title": f"Error parsing Flask app file: {os.path.basename(filepath)}",
                    "severity": "medium",
                    "description": f"Could not parse Flask app file: {str(e)}",
                    "recommendation": "Ensure your Flask app file is properly formatted",
                    "affected_files": [filepath]
                })
                results["issue_counts"]["medium"] += 1
        
        # Check settings against checklist
        for item in checklist:
            setting_name = item["setting_name"]
            secure_value = item["secure_value"]
            severity = item["severity"]
            
            # Check if setting exists
            if setting_name in settings:
                current_value = settings[setting_name]
                
                # Check if value is secure
                is_secure = self._compare_settings_values(current_value, secure_value, item.get("comparison", "equals"))
                
                if not is_secure:
                    # Add issue
                    results["issues"].append({
                        "id": f"flask-{setting_name.lower().replace('_', '-')}",
                        "title": item["title"],
                        "severity": severity,
                        "description": item["description"],
                        "recommendation": item["recommendation"],
                        "current_value": str(current_value),
                        "secure_value": str(secure_value),
                        "affected_files": app_files,
                        "references": item.get("references", []),
                        "code_example": item.get("code_example", "")
                    })
                    results["issue_counts"][severity] += 1
            elif item.get("required", False):
                # Required setting is missing
                results["issues"].append({
                    "id": f"flask-missing-{setting_name.lower().replace('_', '-')}",
                    "title": f"Missing required security setting: {setting_name}",
                    "severity": severity,
                    "description": item["description"],
                    "recommendation": item["recommendation"],
                    "current_value": "Not set",
                    "secure_value": str(secure_value),
                    "affected_files": app_files,
                    "references": item.get("references", []),
                    "code_example": item.get("code_example", "")
                })
                results["issue_counts"][severity] += 1
        
        # Calculate security score
        total_weight = sum(self._get_severity_weight(item["severity"]) for item in checklist if item.get("required", False))
        current_weight = total_weight
        
        for issue in results["issues"]:
            current_weight -= self._get_severity_weight(issue["severity"])
        
        if total_weight > 0:
            results["security_score"] = int((current_weight / total_weight) * 100)
        else:
            results["security_score"] = 100
        
        return results
    
    def _analyze_express_settings(self, project_path: str) -> Dict[str, Any]:
        """Analyze Express.js security settings"""
        self.logger.info(f"Analyzing Express.js security settings in {project_path}")
        
        # Initialize results
        results = {
            "security_score": 0,
            "issues": [],
            "issue_counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "checked_files": []
        }
        
        # Get Express security checklist
        checklist = self._get_express_security_checklist()
        
        # Find Express app files
        app_files = []
        for pattern in ["app.js", "server.js", "index.js"]:
            app_files.extend(self._find_files_matching_pattern(project_path, pattern))
        
        # Look for security-related files
        security_files = []
        for pattern in ["helmet.js", "cors.js", "security.js"]:
            security_files.extend(self._find_files_matching_pattern(project_path, pattern))
        
        all_files = app_files + security_files
        results["checked_files"].extend(all_files)
        
        # If no app files found, return empty results
        if not app_files:
            results["issues"].append({
                "id": "express-no-app",
                "title": "Express app file not found",
                "severity": "medium",
                "description": "Could not find Express app file to analyze",
                "recommendation": "Ensure your Express project has a proper app file"
            })
            results["issue_counts"]["medium"] += 1
            results["security_score"] = 50  # Default middle score when can't analyze
            return results
        
        # Check for security middleware
        middleware_found = {
            "helmet": False,
            "cors": False,
            "csrf": False,
            "rate_limit": False,
            "content_security_policy": False,
            "xss_protection": False
        }
        
        # Parse app files
        for filepath in all_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for middleware imports and usage
                    if re.search(r"require\(['\"]helmet['\"]\)", content) or re.search(r"import\s+helmet", content):
                        middleware_found["helmet"] = True
                    
                    if re.search(r"require\(['\"]cors['\"]\)", content) or re.search(r"import\s+cors", content):
                        middleware_found["cors"] = True
                    
                    if re.search(r"require\(['\"]csurf['\"]\)", content) or re.search(r"import\s+csurf", content):
                        middleware_found["csrf"] = True
                    
                    if re.search(r"require\(['\"]express-rate-limit['\"]\)", content) or re.search(r"import\s+rateLimit", content):
                        middleware_found["rate_limit"] = True
                    
                    # Check for content security policy
                    if "Content-Security-Policy" in content or "contentSecurityPolicy" in content:
                        middleware_found["content_security_policy"] = True
                    
                    # Check for XSS protection
                    if "X-XSS-Protection" in content or "xssFilter" in content:
                        middleware_found["xss_protection"] = True
            except Exception as e:
                self.logger.error(f"Error analyzing Express file {filepath}: {str(e)}")
                results["issues"].append({
                    "id": "express-file-parse-error",
                    "title": f"Error parsing Express file: {os.path.basename(filepath)}",
                    "severity": "medium",
                    "description": f"Could not parse Express file: {str(e)}",
                    "recommendation": "Ensure your Express app file is properly formatted",
                    "affected_files": [filepath]
                })
                results["issue_counts"]["medium"] += 1
        
        # Check middleware against checklist
        for item in checklist:
            middleware_name = item["middleware_name"]
            severity = item["severity"]
            
            if not middleware_found.get(middleware_name, False):
                # Middleware is missing
                results["issues"].append({
                    "id": f"express-missing-{middleware_name.lower().replace('_', '-')}",
                    "title": item["title"],
                    "severity": severity,
                    "description": item["description"],
                    "recommendation": item["recommendation"],
                    "affected_files": app_files,
                    "references": item.get("references", []),
                    "code_example": item.get("code_example", "")
                })
                results["issue_counts"][severity] += 1
        
        # Calculate security score
        total_weight = sum(self._get_severity_weight(item["severity"]) for item in checklist)
        current_weight = total_weight
        
        for issue in results["issues"]:
            current_weight -= self._get_severity_weight(issue["severity"])
        
        if total_weight > 0:
            results["security_score"] = int((current_weight / total_weight) * 100)
        else:
            results["security_score"] = 100
        
        return results
    
    def _analyze_rails_settings(self, project_path: str) -> Dict[str, Any]:
        """Analyze Ruby on Rails security settings"""
        self.logger.info(f"Analyzing Rails security settings in {project_path}")
        
        # Initialize results
        results = {
            "security_score": 0,
            "issues": [],
            "issue_counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "checked_files": []
        }
        
        # Get Rails security checklist
        checklist = self._get_rails_security_checklist()
        
        # Find Rails configuration files
        config_files = []
        config_patterns = ["config/application.rb", "config/environments/production.rb", "config/initializers/security.rb"]
        
        for pattern in config_patterns:
            found_files = self._find_files_matching_pattern(project_path, pattern)
            config_files.extend(found_files)
            results["checked_files"].extend(found_files)
        
        # If no config files found, return empty results
        if not config_files:
            results["issues"].append({
                "id": "rails-no-config",
                "title": "Rails configuration files not found",
                "severity": "medium",
                "description": "Could not find Rails configuration files to analyze",
                "recommendation": "Ensure your Rails project has proper configuration files"
            })
            results["issue_counts"]["medium"] += 1
            results["security_score"] = 50  # Default middle score when can't analyze
            return results
        
        # Check for security settings
        settings_found = {
            "force_ssl": False,
            "filter_parameters": False,
            "session_store": False,
            "protect_from_forgery": False,
            "content_security_policy": False,
            "secure_headers": False
        }
        
        # Parse config files
        for filepath in config_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for security settings
                    if re.search(r"config\.force_ssl\s*=\s*true", content):
                        settings_found["force_ssl"] = True
                    
                    if re.search(r"config\.filter_parameters", content):
                        settings_found["filter_parameters"] = True
                    
                    if re.search(r"config\.session_store", content) or "ActionDispatch::Session::CookieStore" in content:
                        settings_found["session_store"] = True
                    
                    if "protect_from_forgery" in content:
                        settings_found["protect_from_forgery"] = True
                    
                    if "content_security_policy" in content:
                        settings_found["content_security_policy"] = True
                    
                    if "secure_headers" in content:
                        settings_found["secure_headers"] = True
            except Exception as e:
                self.logger.error(f"Error analyzing Rails file {filepath}: {str(e)}")
                results["issues"].append({
                    "id": "rails-file-parse-error",
                    "title": f"Error parsing Rails file: {os.path.basename(filepath)}",
                    "severity": "medium",
                    "description": f"Could not parse Rails file: {str(e)}",
                    "recommendation": "Ensure your Rails configuration file is properly formatted",
                    "affected_files": [filepath]
                })
                results["issue_counts"]["medium"] += 1
        
        # Check settings against checklist
        for item in checklist:
            setting_name = item["setting_name"]
            severity = item["severity"]
            
            if not settings_found.get(setting_name, False):
                # Setting is missing
                results["issues"].append({
                    "id": f"rails-missing-{setting_name.lower().replace('_', '-')}",
                    "title": item["title"],
                    "severity": severity,
                    "description": item["description"],
                    "recommendation": item["recommendation"],
                    "affected_files": config_files,
                    "references": item.get("references", []),
                    "code_example": item.get("code_example", "")
                })
                results["issue_counts"][severity] += 1
        
        # Calculate security score
        total_weight = sum(self._get_severity_weight(item["severity"]) for item in checklist)
        current_weight = total_weight
        
        for issue in results["issues"]:
            current_weight -= self._get_severity_weight(issue["severity"])
        
        if total_weight > 0:
            results["security_score"] = int((current_weight / total_weight) * 100)
        else:
            results["security_score"] = 100
        
        return results
    
    def _analyze_laravel_settings(self, project_path: str) -> Dict[str, Any]:
        """Analyze Laravel security settings"""
        self.logger.info(f"Analyzing Laravel security settings in {project_path}")
        
        # Initialize results
        results = {
            "security_score": 0,
            "issues": [],
            "issue_counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "checked_files": []
        }
        
        # Get Laravel security checklist
        checklist = self._get_laravel_security_checklist()
        
        # Find Laravel configuration files
        config_files = []
        config_patterns = ["config/app.php", "config/session.php", "config/auth.php", ".env"]
        
        for pattern in config_patterns:
            found_files = self._find_files_matching_pattern(project_path, pattern)
            config_files.extend(found_files)
            results["checked_files"].extend(found_files)
        
        # If no config files found, return empty results
        if not config_files:
            results["issues"].append({
                "id": "laravel-no-config",
                "title": "Laravel configuration files not found",
                "severity": "medium",
                "description": "Could not find Laravel configuration files to analyze",
                "recommendation": "Ensure your Laravel project has proper configuration files"
            })
            results["issue_counts"]["medium"] += 1
            results["security_score"] = 50  # Default middle score when can't analyze
            return results
        
        # Check for security settings
        settings_found = {
            "app_key": False,
            "debug_production": True,  # Default to True (secure: debug is not enabled in production)
            "https_only": False,
            "secure_cookies": False,
            "csrf_protection": False,
            "hashed_passwords": True   # Default to True (Laravel uses bcrypt by default)
        }
        
        # Parse config files
        for filepath in config_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for security settings
                    if ".env" in filepath:
                        # Check .env file
                        if re.search(r"APP_KEY\s*=\s*.+", content) and not re.search(r"APP_KEY\s*=\s*$", content):
                            settings_found["app_key"] = True
                        
                        if re.search(r"APP_DEBUG\s*=\s*true", content):
                            settings_found["debug_production"] = False
                        
                        if re.search(r"SESSION_SECURE_COOKIE\s*=\s*true", content):
                            settings_found["secure_cookies"] = True
                    else:
                        # Check PHP config files
                        if "'key'" in content and "'base64:" in content:
                            settings_found["app_key"] = True
                        
                        if "'debug'" in content and "true" in content:
                            settings_found["debug_production"] = False
                        
                        if "'secure'" in content and "true" in content:
                            settings_found["secure_cookies"] = True
                        
                        if "'url'" in content and "https://" in content:
                            settings_found["https_only"] = True
                        
                        if "'driver'" in content and "'bcrypt'" in content:
                            settings_found["hashed_passwords"] = True
                        
                        if "'csrf'" in content and re.search(r"VerifyCsrfToken", content):
                            settings_found["csrf_protection"] = True
            except Exception as e:
                self.logger.error(f"Error analyzing Laravel file {filepath}: {str(e)}")
                results["issues"].append({
                    "id": "laravel-file-parse-error",
                    "title": f"Error parsing Laravel file: {os.path.basename(filepath)}",
                    "severity": "medium",
                    "description": f"Could not parse Laravel file: {str(e)}",
                    "recommendation": "Ensure your Laravel configuration file is properly formatted",
                    "affected_files": [filepath]
                })
                results["issue_counts"]["medium"] += 1
        
        # Check settings against checklist
        for item in checklist:
            setting_name = item["setting_name"]
            severity = item["severity"]
            
            # For some settings, the secure value is False (e.g., debug_production should be False)
            if item.get("inverse", False):
                if settings_found.get(setting_name, False):
                    # Setting is insecure
                    results["issues"].append({
                        "id": f"laravel-insecure-{setting_name.lower().replace('_', '-')}",
                        "title": item["title"],
                        "severity": severity,
                        "description": item["description"],
                        "recommendation": item["recommendation"],
                        "affected_files": config_files,
                        "references": item.get("references", []),
                        "code_example": item.get("code_example", "")
                    })
                    results["issue_counts"][severity] += 1
            else:
                if not settings_found.get(setting_name, False):
                    # Setting is missing
                    results["issues"].append({
                        "id": f"laravel-missing-{setting_name.lower().replace('_', '-')}",
                        "title": item["title"],
                        "severity": severity,
                        "description": item["description"],
                        "recommendation": item["recommendation"],
                        "affected_files": config_files,
                        "references": item.get("references", []),
                        "code_example": item.get("code_example", "")
                    })
                    results["issue_counts"][severity] += 1
        
        # Calculate security score
        total_weight = sum(self._get_severity_weight(item["severity"]) for item in checklist)
        current_weight = total_weight
        
        for issue in results["issues"]:
            current_weight -= self._get_severity_weight(issue["severity"])
        
        if total_weight > 0:
            results["security_score"] = int((current_weight / total_weight) * 100)
        else:
            results["security_score"] = 100
        
        return results
    
    def _parse_setting_value(self, value_str: str) -> Any:
        """Parse a setting value from a string"""
        value_str = value_str.strip()
        
        # Try to parse as JSON
        try:
            return json.loads(value_str)
        except:
            pass
        
        # Try to parse as Python literal
        try:
            # For Python literals, we need to handle some common cases
            if value_str == "True":
                return True
            elif value_str == "False":
                return False
            elif value_str == "None":
                return None
            elif value_str.isdigit():
                return int(value_str)
            elif value_str.startswith("'") and value_str.endswith("'"):
                return value_str[1:-1]
            elif value_str.startswith('"') and value_str.endswith('"'):
                return value_str[1:-1]
            elif value_str.startswith("[") and value_str.endswith("]"):
                # Try to parse as a list
                items = value_str[1:-1].split(",")
                return [self._parse_setting_value(item) for item in items]
            elif value_str.startswith("{") and value_str.endswith("}"):
                # This is likely a dict, but it's hard to parse safely
                # Just return it as a string
                return value_str
            else:
                return value_str
        except:
            # If all else fails, return as string
            return value_str
    
    def _compare_settings_values(self, current_value: Any, secure_value: Any, comparison: str = "equals") -> bool:
        """Compare a setting value against a secure value"""
        if comparison == "equals":
            return current_value == secure_value
        elif comparison == "not_equals":
            return current_value != secure_value
        elif comparison == "contains":
            if isinstance(current_value, list):
                return secure_value in current_value
            elif isinstance(current_value, str):
                return secure_value in current_value
            else:
                return False
        elif comparison == "not_contains":
            if isinstance(current_value, list):
                return secure_value not in current_value
            elif isinstance(current_value, str):
                return secure_value not in current_value
            else:
                return True
        elif comparison == "greater_than":
            if isinstance(current_value, (int, float)) and isinstance(secure_value, (int, float)):
                return current_value > secure_value
            else:
                return False
        elif comparison == "less_than":
            if isinstance(current_value, (int, float)) and isinstance(secure_value, (int, float)):
                return current_value < secure_value
            else:
                return False
        else:
            # Default to equals
            return current_value == secure_value
    
    def _get_severity_weight(self, severity: str) -> int:
        """Get the weight of a severity level for scoring purposes"""
        weights = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 1
        }
        return weights.get(severity, 0)
    
    def _get_django_security_checklist(self) -> List[Dict[str, Any]]:
        """Get security checklist for Django"""
        return [
            {
                "setting_name": "DEBUG",
                "secure_value": False,
                "comparison": "equals",
                "severity": "critical",
                "required": True,
                "title": "Debug mode enabled in production",
                "description": "DEBUG mode should be disabled in production as it exposes sensitive information",
                "recommendation": "Set DEBUG = False in production settings",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#debug"],
                "code_example": "# settings.py\nDEBUG = False"
            },
            {
                "setting_name": "SECRET_KEY",
                "secure_value": "",
                "comparison": "not_equals",
                "severity": "critical",
                "required": True,
                "title": "Weak or missing SECRET_KEY",
                "description": "SECRET_KEY should be a strong, unique value used for cryptographic signing",
                "recommendation": "Set a strong, unique SECRET_KEY and keep it secret",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#secret-key"],
                "code_example": "# settings.py\nSECRET_KEY = '...long random string...'"
            },
            {
                "setting_name": "ALLOWED_HOSTS",
                "secure_value": [],
                "comparison": "not_equals",
                "severity": "high",
                "required": True,
                "title": "ALLOWED_HOSTS not properly configured",
                "description": "ALLOWED_HOSTS should be set to the domains your site is served from",
                "recommendation": "Set ALLOWED_HOSTS to a list of your site's domains",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts"],
                "code_example": "# settings.py\nALLOWED_HOSTS = ['example.com', 'www.example.com']"
            },
            {
                "setting_name": "SECURE_SSL_REDIRECT",
                "secure_value": True,
                "comparison": "equals",
                "severity": "high",
                "required": False,
                "title": "SSL redirect not enabled",
                "description": "SECURE_SSL_REDIRECT should be enabled to redirect HTTP to HTTPS",
                "recommendation": "Set SECURE_SSL_REDIRECT = True in production settings",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#secure-ssl-redirect"],
                "code_example": "# settings.py\nSECURE_SSL_REDIRECT = True"
            },
            {
                "setting_name": "SESSION_COOKIE_SECURE",
                "secure_value": True,
                "comparison": "equals",
                "severity": "high",
                "required": False,
                "title": "Insecure session cookies",
                "description": "SESSION_COOKIE_SECURE should be enabled to only send session cookies over HTTPS",
                "recommendation": "Set SESSION_COOKIE_SECURE = True in production settings",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-secure"],
                "code_example": "# settings.py\nSESSION_COOKIE_SECURE = True"
            },
            {
                "setting_name": "CSRF_COOKIE_SECURE",
                "secure_value": True,
                "comparison": "equals",
                "severity": "high",
                "required": False,
                "title": "Insecure CSRF cookies",
                "description": "CSRF_COOKIE_SECURE should be enabled to only send CSRF cookies over HTTPS",
                "recommendation": "Set CSRF_COOKIE_SECURE = True in production settings",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-secure"],
                "code_example": "# settings.py\nCSRF_COOKIE_SECURE = True"
            },
            {
                "setting_name": "SECURE_HSTS_SECONDS",
                "secure_value": 0,
                "comparison": "greater_than",
                "severity": "medium",
                "required": False,
                "title": "HSTS not enabled",
                "description": "SECURE_HSTS_SECONDS should be set to enable HTTP Strict Transport Security",
                "recommendation": "Set SECURE_HSTS_SECONDS to at least 31536000 (1 year)",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#secure-hsts-seconds"],
                "code_example": "# settings.py\nSECURE_HSTS_SECONDS = 31536000  # 1 year"
            },
            {
                "setting_name": "SECURE_CONTENT_TYPE_NOSNIFF",
                "secure_value": True,
                "comparison": "equals",
                "severity": "medium",
                "required": False,
                "title": "Content type sniffing not prevented",
                "description": "SECURE_CONTENT_TYPE_NOSNIFF should be enabled to prevent MIME type sniffing",
                "recommendation": "Set SECURE_CONTENT_TYPE_NOSNIFF = True",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#secure-content-type-nosniff"],
                "code_example": "# settings.py\nSECURE_CONTENT_TYPE_NOSNIFF = True"
            },
            {
                "setting_name": "SECURE_BROWSER_XSS_FILTER",
                "secure_value": True,
                "comparison": "equals",
                "severity": "medium",
                "required": False,
                "title": "XSS filter not enabled",
                "description": "SECURE_BROWSER_XSS_FILTER should be enabled to activate browser XSS filtering",
                "recommendation": "Set SECURE_BROWSER_XSS_FILTER = True",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#secure-browser-xss-filter"],
                "code_example": "# settings.py\nSECURE_BROWSER_XSS_FILTER = True"
            },
            {
                "setting_name": "X_FRAME_OPTIONS",
                "secure_value": "DENY",
                "comparison": "equals",
                "severity": "medium",
                "required": False,
                "title": "Clickjacking protection not optimal",
                "description": "X_FRAME_OPTIONS should be set to 'DENY' to prevent clickjacking",
                "recommendation": "Set X_FRAME_OPTIONS = 'DENY'",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#x-frame-options"],
                "code_example": "# settings.py\nX_FRAME_OPTIONS = 'DENY'"
            },
            {
                "setting_name": "SECURE_REFERRER_POLICY",
                "secure_value": "same-origin",
                "comparison": "equals",
                "severity": "low",
                "required": False,
                "title": "Referrer policy not set",
                "description": "SECURE_REFERRER_POLICY should be set to control the Referrer header",
                "recommendation": "Set SECURE_REFERRER_POLICY = 'same-origin' or stricter",
                "references": ["https://docs.djangoproject.com/en/stable/ref/settings/#secure-referrer-policy"],
                "code_example": "# settings.py\nSECURE_REFERRER_POLICY = 'same-origin'"
            }
        ]
    
    def _get_flask_security_checklist(self) -> List[Dict[str, Any]]:
        """Get Flask-specific security checklist."""
        return [
            {
                "category": "Authentication",
                "checks": [
                    {"name": "Session management", "critical": True},
                    {"name": "Password hashing", "critical": True},
                    {"name": "CSRF protection", "critical": True}
                ]
            },
            {
                "category": "Input Validation", 
                "checks": [
                    {"name": "SQL injection prevention", "critical": True},
                    {"name": "XSS prevention", "critical": True},
                    {"name": "File upload validation", "critical": False}
                ]
            },
            {
                "category": "Configuration",
                "checks": [
                    {"name": "Debug mode disabled", "critical": True},
                    {"name": "Secret key security", "critical": True},
                    {"name": "Security headers", "critical": False}
                ]
            }
        ]

    def _get_express_security_checklist(self) -> List[Dict[str, Any]]:
        """Get Express.js-specific security checklist."""
        return [
            {
                "middleware_name": "helmet",
                "severity": "high",
                "title": "Helmet middleware not configured",
                "description": "Helmet helps secure Express apps by setting various HTTP headers",
                "recommendation": "Install and configure helmet middleware for security headers",
                "references": ["https://www.npmjs.com/package/helmet"],
                "code_example": "const helmet = require('helmet');\napp.use(helmet());"
            },
            {
                "middleware_name": "cors",
                "severity": "medium",
                "title": "CORS not properly configured",
                "description": "Cross-Origin Resource Sharing should be properly configured",
                "recommendation": "Configure CORS middleware with appropriate origins",
                "references": ["https://www.npmjs.com/package/cors"],
                "code_example": "const cors = require('cors');\napp.use(cors({origin: 'https://yourdomain.com'}));"
            },
            {
                "middleware_name": "csrf",
                "severity": "high",
                "title": "CSRF protection not enabled",
                "description": "Cross-Site Request Forgery protection should be enabled",
                "recommendation": "Implement CSRF protection using csurf middleware",
                "references": ["https://www.npmjs.com/package/csurf"],
                "code_example": "const csrf = require('csurf');\napp.use(csrf());"
            },
            {
                "middleware_name": "rate_limit",
                "severity": "medium",
                "title": "Rate limiting not configured",
                "description": "Rate limiting helps prevent abuse and DoS attacks",
                "recommendation": "Configure express-rate-limit middleware",
                "references": ["https://www.npmjs.com/package/express-rate-limit"],
                "code_example": "const rateLimit = require('express-rate-limit');\napp.use(rateLimit({windowMs: 15 * 60 * 1000, max: 100}));"
            }
        ]

    def _get_rails_security_checklist(self) -> List[Dict[str, Any]]:
        """Get Rails-specific security checklist."""
        return [
            {
                "setting_name": "force_ssl",
                "severity": "high",
                "title": "Force SSL not enabled",
                "description": "Rails should force HTTPS connections in production",
                "recommendation": "Enable config.force_ssl = true in production.rb",
                "references": ["https://guides.rubyonrails.org/security.html#ssl"],
                "code_example": "# config/environments/production.rb\nconfig.force_ssl = true"
            },
            {
                "setting_name": "filter_parameters",
                "severity": "medium",
                "title": "Sensitive parameters not filtered",
                "description": "Sensitive parameters should be filtered from logs",
                "recommendation": "Configure filter_parameters to hide sensitive data",
                "references": ["https://guides.rubyonrails.org/security.html#logging"],
                "code_example": "# config/application.rb\nconfig.filter_parameters += [:password, :email]"
            },
            {
                "setting_name": "protect_from_forgery",
                "severity": "high",
                "title": "CSRF protection not enabled",
                "description": "Controllers should use protect_from_forgery",
                "recommendation": "Add protect_from_forgery to ApplicationController",
                "references": ["https://guides.rubyonrails.org/security.html#csrf"],
                "code_example": "# app/controllers/application_controller.rb\nprotect_from_forgery with: :exception"
            }
        ]

    def _get_laravel_security_checklist(self) -> List[Dict[str, Any]]:
        """Get Laravel-specific security checklist."""
        return [
            {
                "setting_name": "app_key",
                "severity": "critical",
                "title": "Application key not set",
                "description": "Laravel APP_KEY should be set for encryption",
                "recommendation": "Generate and set a strong APP_KEY in .env file",
                "references": ["https://laravel.com/docs/encryption"],
                "code_example": "# .env\nAPP_KEY=base64:your-generated-key-here"
            },
            {
                "setting_name": "debug_production",
                "severity": "high",
                "inverse": True,
                "title": "Debug mode enabled in production",
                "description": "APP_DEBUG should be false in production",
                "recommendation": "Set APP_DEBUG=false in production .env",
                "references": ["https://laravel.com/docs/configuration#debug-mode"],
                "code_example": "# .env\nAPP_DEBUG=false"
            },
            {
                "setting_name": "secure_cookies",
                "severity": "high",
                "title": "Secure cookies not enabled",
                "description": "Cookies should be marked as secure in production",
                "recommendation": "Set SESSION_SECURE_COOKIE=true in .env",
                "references": ["https://laravel.com/docs/session"],
                "code_example": "# .env\nSESSION_SECURE_COOKIE=true"
            }
        ]
