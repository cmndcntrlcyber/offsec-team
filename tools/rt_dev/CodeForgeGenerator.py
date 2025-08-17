import os
import subprocess
import re
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

class CodeForgeGenerator:
    """
    A tool for generating template code for various programming languages and project types.
    Provides capabilities for creating, customizing, and validating code templates.
    """
    
    def __init__(self):
        self.template_paths = {
            "python": {
                "basic": "templates/python/basic",
                "api": "templates/python/api",
                "cli": "templates/python/cli",
                "data_science": "templates/python/data_science"
            },
            "rust": {
                "basic": "templates/rust/basic",
                "cli": "templates/rust/cli",
                "web": "templates/rust/web",
                "system": "templates/rust/system"
            },
            "go": {
                "basic": "templates/go/basic",
                "api": "templates/go/api",
                "cli": "templates/go/cli",
                "microservice": "templates/go/microservice"
            },
            "docker": {
                "basic": "templates/docker/basic",
                "multi_stage": "templates/docker/multi_stage",
                "compose": "templates/docker/compose"
            },
            "terraform": {
                "aws": "templates/terraform/aws",
                "azure": "templates/terraform/azure",
                "gcp": "templates/terraform/gcp",
                "modules": "templates/terraform/modules"
            }
        }
        
        # Sample templates for immediate use when actual template files aren't available
        self.sample_templates = {
            "python": {
                "basic": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
{{project_name}}

{{project_description}}
\"\"\"

import sys
import os
import argparse

def main():
    \"\"\"Main entry point for the application\"\"\"
    parser = argparse.ArgumentParser(description='{{project_description}}')
    # Add arguments here
    args = parser.parse_args()
    
    # Your code here
    print("Hello, World!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
"""
            },
            "rust": {
                "basic": """//! {{project_name}}
//! 
//! {{project_description}}

fn main() {
    println!("Hello, World!");
}
"""
            },
            "go": {
                "basic": """// {{project_name}}
// {{project_description}}

package main

import (
	"fmt"
)

func main() {
	fmt.Println("Hello, World!")
}
"""
            },
            "docker": {
                "basic": """FROM {{base_image}}:{{tag}}

WORKDIR /app

COPY . .

RUN {{build_command}}

EXPOSE {{port}}

CMD ["{{command}}"]
"""
            },
            "terraform": {
                "basic": """# {{project_name}}
# {{project_description}}

provider "{{provider}}" {
  {{provider_config}}
}

resource "{{resource_type}}" "{{resource_name}}" {
  {{resource_config}}
}

output "{{output_name}}" {
  value = {{output_value}}
}
"""
            }
        }
    
    def generate_language_template(self, language: str = Field(..., description="Programming language (python, rust, go, docker, terraform)"), 
                                  project_type: str = Field(..., description="Type of project (basic, api, cli, etc.)"),
                                  variables: Dict[str, str] = Field({}, description="Template variables to replace")) -> str:
        """
        Generate boilerplate code in Python, Rust, Go, Docker, or Terraform.
        
        Args:
            language: Programming language to generate code for
            project_type: Type of project to generate
            variables: Dictionary of variables to replace in the template
            
        Returns:
            Generated code as a string
        """
        # Validate inputs
        language = language.lower()
        project_type = project_type.lower()
        
        if language not in self.template_paths:
            return f"Error: Unsupported language '{language}'. Supported languages: {', '.join(self.template_paths.keys())}"
        
        if project_type not in self.template_paths[language]:
            available_types = ', '.join(self.template_paths[language].keys())
            return f"Error: Unsupported project type '{project_type}' for {language}. Available types: {available_types}"
        
        # Get template content (from file or fallback to sample)
        template_path = self.template_paths[language][project_type]
        template = ""
        
        # Attempt to read from file if it exists
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r') as file:
                    template = file.read()
            except Exception as e:
                # Fallback to sample template
                template = self.sample_templates.get(language, {}).get(project_type, "")
                if not template:
                    return f"Error: Could not load template for {language}/{project_type}: {str(e)}"
        else:
            # Use sample template
            template = self.sample_templates.get(language, {}).get(project_type, "")
            if not template:
                return f"Error: No sample template available for {language}/{project_type}"
        
        # Replace template variables
        for key, value in variables.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        
        return template
    
    def inject_custom_code_blocks(self, template: str = Field(..., description="Template code to modify"), 
                                custom_blocks: Dict[str, str] = Field(..., description="Dictionary of block markers and their replacements")) -> str:
        """
        Insert custom code blocks into templates by replacing markers.
        
        Args:
            template: The template code with markers for custom blocks
            custom_blocks: Dictionary where keys are marker names and values are replacement code
            
        Returns:
            Modified template with custom blocks inserted
        """
        modified_template = template
        
        for marker, code in custom_blocks.items():
            # Replace markers in the format {{block:marker_name}}
            marker_pattern = f"{{{{block:{marker}}}}}"
            modified_template = modified_template.replace(marker_pattern, code)
        
        return modified_template
    
    def validate_code_syntax(self, code: str = Field(..., description="Code to validate"), 
                           language: str = Field(..., description="Programming language of the code")) -> Tuple[bool, str]:
        """
        Verify syntax of generated code before output.
        
        Args:
            code: The code to validate
            language: The programming language of the code
            
        Returns:
            Tuple containing (is_valid, error_message)
        """
        language = language.lower()
        
        # Different validation approaches based on language
        if language == "python":
            return self._validate_python_syntax(code)
        elif language == "rust":
            return self._validate_rust_syntax(code)
        elif language == "go":
            return self._validate_go_syntax(code)
        elif language == "docker":
            return self._validate_dockerfile_syntax(code)
        elif language == "terraform":
            return self._validate_terraform_syntax(code)
        else:
            return False, f"Error: Syntax validation not supported for language '{language}'"
    
    def _validate_python_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Python code syntax using ast.parse"""
        try:
            # Use Python's built-in parser to check syntax
            import ast
            ast.parse(code)
            return True, "Code syntax is valid"
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}"
        except Exception as e:
            return False, f"Error validating Python code: {str(e)}"
    
    def _validate_rust_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Rust code syntax using rustc"""
        # Check if rustc is available
        try:
            # Write code to temporary file
            temp_file = "temp_rust_code.rs"
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Run rustc with --check flag (syntax only)
            result = subprocess.run(["rustc", "--check", temp_file], 
                                   capture_output=True, text=True)
            
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode == 0:
                return True, "Code syntax is valid"
            else:
                return False, f"Rust syntax error: {result.stderr}"
        except FileNotFoundError:
            # Fallback to basic validation if rustc not available
            return self._basic_rust_validation(code)
        except Exception as e:
            return False, f"Error validating Rust code: {str(e)}"
    
    def _basic_rust_validation(self, code: str) -> Tuple[bool, str]:
        """Basic Rust syntax validation for when rustc is not available"""
        # Check for basic syntax errors
        errors = []
        
        # Check for unmatched brackets
        brackets = {'(': ')', '{': '}', '[': ']'}
        stack = []
        
        for i, char in enumerate(code):
            if char in brackets.keys():
                stack.append((char, i))
            elif char in brackets.values():
                if not stack:
                    errors.append(f"Unmatched closing bracket '{char}' at position {i}")
                    continue
                
                opening, pos = stack.pop()
                if char != brackets[opening]:
                    errors.append(f"Mismatched brackets: '{opening}' at position {pos} and '{char}' at position {i}")
        
        for bracket, pos in stack:
            errors.append(f"Unmatched opening bracket '{bracket}' at position {pos}")
        
        # Check for string termination
        in_string = False
        string_start = 0
        
        for i, char in enumerate(code):
            if char == '"' and (i == 0 or code[i-1] != '\\'):
                if in_string:
                    in_string = False
                else:
                    in_string = True
                    string_start = i
        
        if in_string:
            errors.append(f"Unterminated string starting at position {string_start}")
        
        if errors:
            return False, "\n".join(errors)
        else:
            return True, "Basic syntax check passed (Note: full validation requires rustc)"
    
    def _validate_go_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Go code syntax using go vet"""
        try:
            # Write code to temporary file
            temp_file = "temp_go_code.go"
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Run go vet
            result = subprocess.run(["go", "vet", temp_file], 
                                   capture_output=True, text=True)
            
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode == 0:
                return True, "Code syntax is valid"
            else:
                return False, f"Go syntax error: {result.stderr}"
        except FileNotFoundError:
            # Basic validation if go is not available
            return True, "Go syntax validation skipped (go command not available)"
        except Exception as e:
            return False, f"Error validating Go code: {str(e)}"
    
    def _validate_dockerfile_syntax(self, code: str) -> Tuple[bool, str]:
        """Basic Dockerfile syntax validation"""
        # Check for common Dockerfile syntax errors
        errors = []
        
        # Each line should start with a valid Dockerfile instruction
        valid_instructions = ['FROM', 'RUN', 'CMD', 'LABEL', 'EXPOSE', 'ENV', 
                             'ADD', 'COPY', 'ENTRYPOINT', 'VOLUME', 'USER', 
                             'WORKDIR', 'ARG', 'ONBUILD', 'STOPSIGNAL', 'HEALTHCHECK', 'SHELL']
        
        lines = code.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            instruction = parts[0].upper()
            if instruction not in valid_instructions:
                errors.append(f"Line {i+1}: Invalid Dockerfile instruction '{instruction}'")
            
            # FROM must be followed by an image name
            if instruction == 'FROM' and len(parts) < 2:
                errors.append(f"Line {i+1}: FROM instruction requires an image name")
            
            # CMD and ENTRYPOINT need arguments
            if instruction in ['CMD', 'ENTRYPOINT'] and len(parts) < 2:
                errors.append(f"Line {i+1}: {instruction} requires at least one argument")
        
        if errors:
            return False, "\n".join(errors)
        else:
            return True, "Dockerfile syntax appears valid"
    
    def _validate_terraform_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Terraform syntax using terraform fmt"""
        try:
            # Write code to temporary file
            temp_file = "temp_terraform_code.tf"
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Run terraform fmt to check syntax
            result = subprocess.run(["terraform", "fmt", "-check", temp_file], 
                                   capture_output=True, text=True)
            
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode == 0:
                return True, "Terraform syntax is valid"
            else:
                return False, f"Terraform syntax error: {result.stderr}"
        except FileNotFoundError:
            # Basic validation if terraform is not available
            return True, "Terraform syntax validation skipped (terraform command not available)"
        except Exception as e:
            return False, f"Error validating Terraform code: {str(e)}"
