#!/usr/bin/env python3
"""
Generate tofu import commands for existing Cloud Run tag bindings.

This script:
1. Reads cloud_run_services from terraform.tfvars
2. Calls gcloud to check for existing tag bindings on each service
3. Generates tofu import commands for services that have bindings
"""

import subprocess
import json
import re
import sys
from pathlib import Path

# Configuration
PROJECT_ID = "viki-dev-app-wsky"
LOCATION = "us-east4"
TERRAFORM_TFVARS_PATH = "../env/dev/terraform.tfvars"

# Service name mapping for services that don't follow standard naming
SERVICE_NAME_MAPPING = {
    "paperglass_api_external": "ai-paperglass-external-api",
    "medication_extraction_api": "ai-medication-extraction",
    "medication_extraction_api_2": "ai-medication-extraction-2",
    "medication_extraction_default_api": "ai-medication-extraction-default",
    "medication_extraction_high_api": "ai-medication-extraction-high",
    "medication_extraction_quarantine_api": "ai-medication-extraction-quarantine",
    "extract_and_fill_api": "ai-extract-and-fill-api",
    "extract_and_fill_events": "ai-extract-and-fill-events",
    "extract_and_fill_events_vertexai": "ai-extract-and-fill-events-vertexai",
    "extract_and_fill_widget": "ai-extract-and-fill-widget",
    "demo_api": "ai-demo-api",
    "demo_dashboard": "ai-demo-dashboard",
    "nurse_assistant": "ai-nurse-assistant",
    # Add more mappings as needed
}

def parse_terraform_tfvars():
    """Parse the terraform.tfvars file to extract cloud_run_services."""
    tfvars_path = Path(__file__).parent / TERRAFORM_TFVARS_PATH

    if not tfvars_path.exists():
        print(f"Error: {tfvars_path} not found")
        sys.exit(1)

    services = {}

    with open(tfvars_path, 'r') as f:
        content = f.read()

    # Extract cloud_run_services block using regex
    pattern = r'cloud_run_services\s*=\s*\{(.*?)\n\}'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print("Error: Could not find cloud_run_services in terraform.tfvars")
        sys.exit(1)

    services_block = match.group(1)

    # Parse individual service blocks
    service_pattern = r'(\w+)\s*=\s*\{([^}]+)\}'
    service_matches = re.findall(service_pattern, services_block)

    for service_name, config_block in service_matches:
        # Extract allow_public_access value
        access_pattern = r'allow_public_access\s*=\s*(true|false)'
        access_match = re.search(access_pattern, config_block)

        if access_match:
            allow_public_access = access_match.group(1) == 'true'
            services[service_name] = {
                'allow_public_access': allow_public_access
            }

    return services

def get_service_name(service_key):
    """Convert service key to actual Cloud Run service name."""
    if service_key in SERVICE_NAME_MAPPING:
        return SERVICE_NAME_MAPPING[service_key]
    else:
        return f"ai-{service_key.replace('_', '-')}"

def get_module_name(service_name):
    """Convert service name back to module name."""
    # Handle special mappings first
    reverse_mapping = {
        "ai-paperglass-external-api": "paperglass_external_api",
        "ai-medication-extraction": "medication_extraction_api",
        "ai-medication-extraction-2": "medication_extraction_api_2",
        "ai-medication-extraction-default": "medication_extraction_default_api",
        "ai-medication-extraction-high": "medication_extraction_high_api",
        "ai-medication-extraction-quarantine": "medication_extraction_quarantine_api",
        "ai-extract-and-fill-api": "extract_and_fill_api",
        "ai-extract-and-fill-events": "extract_and_fill_events",
        "ai-extract-and-fill-events-vertexai": "extract_and_fill_events_vertexai",
        "ai-extract-and-fill-widget": "extract_and_fill_widget",
        "ai-demo-api": "demo_api",
        "ai-demo-dashboard": "demo_dashboard",
        "ai-nurse-assistant": "nurseassistant",
    }

    if service_name in reverse_mapping:
        return reverse_mapping[service_name]
    else:
        # Standard conversion: ai-service-name -> service_name
        if service_name.startswith("ai-"):
            return service_name[3:].replace("-", "_")
        return service_name.replace("-", "_")

def check_service_bindings(service_name):
    """Check if a service has existing tag bindings."""
    parent = f"//run.googleapis.com/projects/{PROJECT_ID}/locations/{LOCATION}/services/{service_name}"

    cmd = [
        "gcloud", "resource-manager", "tags", "bindings", "list",
        f"--parent={parent}",
        f"--location={LOCATION}",
        "--format=json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        bindings = json.loads(result.stdout)
        return bindings if bindings else None
    except subprocess.CalledProcessError as e:
        if "403" in e.stderr or "does not have permission" in e.stderr:
            print(f"  Service {service_name} does not exist (403 error)")
            return None
        else:
            print(f"  Error checking {service_name}: {e.stderr}")
            return None
    except json.JSONDecodeError:
        print(f"  Could not parse response for {service_name}")
        return None

def extract_binding_id(binding_name):
    """Extract the binding ID from the full binding name."""
    # binding name format: tagBindings/{encoded_parent}/tagValues/{tag_value}
    # We need the part after "tagBindings/"
    if binding_name.startswith("tagBindings/"):
        return binding_name[12:]  # Remove "tagBindings/" prefix
    return binding_name

def generate_import_commands():
    """Generate tofu import commands for all services with existing bindings."""
    print("Parsing terraform.tfvars...")
    services = parse_terraform_tfvars()

    print(f"Found {len(services)} services in cloud_run_services")

    # Filter for services that should be public
    public_services = {k: v for k, v in services.items() if v.get('allow_public_access', False)}

    print(f"Found {len(public_services)} services with allow_public_access = true")

    import_commands = []
    state_rm_commands = []

    for service_key in public_services:
        service_name = get_service_name(service_key)
        print(f"Checking {service_key} -> {service_name}...")

        bindings = check_service_bindings(service_name)

        if bindings:
            for binding in bindings:
                binding_name = binding.get('name', '')
                binding_id = extract_binding_id(binding_name)

                if binding_id:
                    import_cmd = f'tofu import \'module.ai.google_tags_location_tag_binding.public_services["{service_name}"]\' "{LOCATION}/tagBindings/{binding_id}";'
                    import_commands.append(import_cmd)
                    print(f"  ✓ Found binding: {binding_id}")

                    # Generate corresponding state removal command
                    module_name = get_module_name(service_name)
                    state_rm_cmd = f'tofu state rm \'module.ai.module.{module_name}.google_tags_location_tag_binding.all_users_ingress[0]\';'
                    state_rm_commands.append(state_rm_cmd)
                else:
                    print(f"  ⚠ Could not extract binding ID from: {binding_name}")
        else:
            print(f"  - No bindings found")

    return import_commands, state_rm_commands

def main():
    """Main function."""
    print("Generating tofu import commands for Cloud Run tag bindings...")
    print("=" * 60)

    try:
        import_commands, state_rm_commands = generate_import_commands()

        print("\n" + "=" * 60)
        print(f"Generated {len(import_commands)} import commands and {len(state_rm_commands)} state removal commands:")
        print("=" * 60)

        # Write commands to a shell script
        script_path = Path(__file__).parent / "import_bindings.sh"

        with open(script_path, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Generated tofu commands for Cloud Run tag bindings\n")
            f.write("# Run this script in your Spacelift task\n\n")
            f.write("set -e\n\n")

            f.write("echo \"Importing existing tag bindings to centralized management...\"\n")
            for cmd in import_commands:
                f.write(f"{cmd}\n")
                print(cmd)

            f.write("\necho \"Removing old individual module tag binding state entries...\"\n")
            for cmd in state_rm_commands:
                f.write(f"{cmd}\n")
                print(cmd)

            f.write("\necho \"Tag binding migration complete!\"\n")

        print(f"\nCommands written to: {script_path}")
        print(f"Make the script executable: chmod +x {script_path}")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()