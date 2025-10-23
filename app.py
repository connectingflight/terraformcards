from flask import Flask, render_template_string, url_for
import webbrowser
import threading
import json

"""
python3 -m pip install -r requirements.txt

Enhanced Flask web app that renders Command Cards for Terraform Associate topics.
- Run: pip install flask
- Then: python TerraformHeatMap.py
- Opens a local web page with interactive cards linking to Terraform docs.

This file intentionally summarizes topics and provides concise examples; it does not copy content from external articles.
Terraform docs: https://developer.hashicorp.com/terraform
"""

app = Flask(__name__)

# Topic data: include core Terraform commands and short examples.
# Each entry follows the format requested: COMMAND / DESCRIPTION OR NOTES / EXAMPLE
TOPICS = [
    # Basic Terraform Commands
    {"id": "init", "title": "terraform init",
     "desc": "Initialize a new or existing Terraform working directory: downloads providers, initializes backends and modules.",
     "cmd": "terraform init",
     "example": "terraform init\n# Reconfigure backend\nterraform init -reconfigure -backend-config=\"bucket=my-bucket\"",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/init",
     "category": "Basic Terraform Commands"},
    {"id": "plan", "title": "terraform plan",
     "desc": "Generate and show an execution plan (what Terraform will change).",
     "cmd": "terraform plan -out=plan.tfplan",
     "example": "terraform plan -out=plan.tfplan\nterraform plan -detailed-exitcode",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Basic Terraform Commands"},
    {"id": "apply", "title": "terraform apply",
     "desc": "Build or change infrastructure as described by the plan or configuration.",
     "cmd": "terraform apply plan.tfplan",
     "example": "terraform apply plan.tfplan\n# non-interactive\nterraform apply -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Basic Terraform Commands"},
    {"id": "destroy", "title": "terraform destroy",
     "desc": "Destroy Terraform-managed infrastructure for the current configuration.",
     "cmd": "terraform destroy",
     "example": "terraform destroy -auto-approve\n# target a single resource\nterraform destroy -target=aws_instance.example",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/destroy",
     "category": "Basic Terraform Commands"},
    {"id": "fmt", "title": "terraform fmt",
     "desc": "Format Terraform configuration files to canonical HCL style.",
     "cmd": "terraform fmt -recursive",
     "example": "terraform fmt -check -recursive",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/fmt",
     "category": "Basic Terraform Commands"},
    {"id": "validate", "title": "terraform validate",
     "desc": "Validate configuration syntax and basic semantic rules without contacting remote systems.",
     "cmd": "terraform validate",
     "example": "terraform validate\nterraform validate -json > validate.json",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/validate",
     "category": "Basic Terraform Commands"},
    {"id": "output", "title": "terraform output",
     "desc": "Read outputs from the state or a saved plan; supports machine-readable JSON.",
     "cmd": "terraform output instance_ip",
     "example": "terraform output -json > outputs.json",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/output",
     "category": "Basic Terraform Commands"},
    {"id": "show", "title": "terraform show",
     "desc": "Produce human-readable or JSON representation of state or plan files.",
     "cmd": "terraform show plan.tfplan",
     "example": "terraform show -json plan.tfplan > plan.json",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/show",
     "category": "Basic Terraform Commands"},
    {"id": "version", "title": "terraform version",
     "desc": "Display the Terraform and plugin versions in use.",
     "cmd": "terraform version",
     "example": "terraform version",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/version",
     "category": "Basic Terraform Commands"},
    {"id": "providers", "title": "terraform providers",
     "desc": "List providers required by the configuration and show provider dependency graph.",
     "cmd": "terraform providers",
     "example": "terraform providers\nterraform providers | sed -n '1,50p'",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/providers",
     "category": "Basic Terraform Commands"},

    # Terraform State Management
    {"id": "state_list", "title": "terraform state list",
     "desc": "List all resources recorded in the Terraform state.",
     "cmd": "terraform state list",
     "example": "terraform state list",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Terraform State Management"},
    {"id": "state_show", "title": "terraform state show",
     "desc": "Show attributes for a single resource from the state.",
     "cmd": "terraform state show aws_instance.example",
     "example": "terraform state show module.db.aws_db_instance.example",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Terraform State Management"},
    {"id": "state_pull", "title": "terraform state pull",
     "desc": "Download current state from the backend as JSON to stdout.",
     "cmd": "terraform state pull",
     "example": "terraform state pull > terraform.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Terraform State Management"},
    {"id": "state_push", "title": "terraform state push",
     "desc": "Upload a local state file to the remote backend (advanced/rare; use with caution).",
     "cmd": "terraform state push terraform.tfstate",
     "example": "terraform state push terraform.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Terraform State Management"},
    {"id": "state_rm", "title": "terraform state rm",
     "desc": "Remove a resource from the state without modifying real infrastructure.",
     "cmd": "terraform state rm aws_instance.example",
     "example": "terraform state rm module.old.aws_instance.example",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Terraform State Management"},
    {"id": "state_mv", "title": "terraform state mv",
     "desc": "Move resources within the state (rename or move between modules).",
     "cmd": "terraform state mv 'aws_instance.old[0]' 'aws_instance.new[0]'",
     "example": "terraform state mv module.old.aws_instance.example module.new.aws_instance.example",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Terraform State Management"},
    {"id": "state_replace_provider", "title": "terraform state replace-provider",
     "desc": "Replace provider references in the state when changing provider addresses.",
     "cmd": "terraform state replace-provider registry.terraform.io/hashicorp/aws registry.terraform.io/custom/myaws",
     "example": "terraform state replace-provider old_provider new_provider",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Terraform State Management"},
    {"id": "refresh", "title": "terraform refresh",
     "desc": "Update local state to match real-world infrastructure (deprecated; plan/refresh flags preferred).",
     "cmd": "terraform refresh",
     "example": "terraform refresh\n# or use plan with -refresh=true/false",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Terraform State Management"},

    # Terraform Workspaces
    {"id": "workspace_list", "title": "terraform workspace list",
     "desc": "List all named workspaces for the current configuration.",
     "cmd": "terraform workspace list",
     "example": "terraform workspace list",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/workspace",
     "category": "Terraform Workspaces"},
    {"id": "workspace_new", "title": "terraform workspace new",
     "desc": "Create a new named workspace (separate state instance).",
     "cmd": "terraform workspace new dev",
     "example": "terraform workspace new staging",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/workspace",
     "category": "Terraform Workspaces"},
    {"id": "workspace_select", "title": "terraform workspace select",
     "desc": "Switch to an existing workspace to use its state.",
     "cmd": "terraform workspace select prod",
     "example": "terraform workspace select staging",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/workspace",
     "category": "Terraform Workspaces"},
    {"id": "workspace_delete", "title": "terraform workspace delete",
     "desc": "Delete a workspace and its state (use with caution).",
     "cmd": "terraform workspace delete old-env",
     "example": "terraform workspace delete staging",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/workspace",
     "category": "Terraform Workspaces"},
    {"id": "workspace_show", "title": "terraform workspace show",
     "desc": "Display the current workspace name.",
     "cmd": "terraform workspace show",
     "example": "terraform workspace show",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/workspace",
     "category": "Terraform Workspaces"},

    # Terraform Import
    {"id": "import_resource", "title": "terraform import",
     "desc": "Import existing infrastructure into Terraform state; update configuration afterwards to match resource attributes.",
     "cmd": "terraform import aws_instance.web i-0123456789abcdef0",
     "example": "terraform import module.db.aws_db_instance.example rds-123456",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/import",
     "category": "Terraform Import"},

    # Graph & Visualization
    {"id": "graph", "title": "terraform graph",
     "desc": "Output dependency graph in DOT format; pipe to Graphviz to render images.",
     "cmd": "terraform graph | dot -Tpng > graph.png",
     "example": "terraform graph | dot -Tsvg > graph.svg",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/graph",
     "category": "Graph & Visualization"},

    # Plan & Apply Options
    {"id": "apply_auto_approve", "title": "terraform apply -auto-approve",
     "desc": "Apply without interactive confirmation (use with caution in automation).",
     "cmd": "terraform apply -auto-approve",
     "example": "terraform apply -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Plan & Apply Options"},
    {"id": "apply_var", "title": "terraform apply -var",
     "desc": "Pass a single variable override on the CLI during apply.",
     "cmd": "terraform apply -var='key=value'",
     "example": "terraform apply -var='region=eu-west-1' -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/language/values/variables#passing-values-on-the-command-line",
     "category": "Plan & Apply Options"},
    {"id": "apply_target", "title": "terraform apply -target",
     "desc": "Apply changes targeting a specific resource (advanced; use carefully).",
     "cmd": "terraform apply -target=aws_instance.example",
     "example": "terraform apply -target=module.db.aws_db_instance.example",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Plan & Apply Options"},
    {"id": "apply_planfile", "title": "terraform apply <plan_file>",
     "desc": "Apply a previously saved plan file to perform the planned changes.",
     "cmd": "terraform apply plan.tfplan",
     "example": "terraform plan -out=plan.tfplan\nterraform apply plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Plan & Apply Options"},
    {"id": "plan_out", "title": "terraform plan -out",
     "desc": "Save the execution plan to a file for later application or inspection.",
     "cmd": "terraform plan -out=plan.tfplan",
     "example": "terraform plan -out=ci.plan\nterraform show -json ci.plan > ci-plan.json",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Plan & Apply Options"},
    {"id": "plan_var", "title": "terraform plan -var",
     "desc": "Provide a one-off variable override on the CLI when generating a plan.",
     "cmd": "terraform plan -var='key=value'",
     "example": "terraform plan -var='env=staging' -out=plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/language/values/variables#passing-values-on-the-command-line",
     "category": "Plan & Apply Options"},
    {"id": "plan_target", "title": "terraform plan -target",
     "desc": "Generate a plan targeting specific resources to limit change scope.",
     "cmd": "terraform plan -target=aws_instance.example",
     "example": "terraform plan -target=module.db -out=target-plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Plan & Apply Options"},
    {"id": "plan_destroy", "title": "terraform plan -destroy",
     "desc": "Show a plan that would destroy all resources managed by the configuration.",
     "cmd": "terraform plan -destroy",
     "example": "terraform plan -destroy -out=destroy.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Plan & Apply Options"},
    {"id": "plan_refresh_false", "title": "terraform plan -refresh=false",
     "desc": "Skip refreshing the state from real infrastructure when generating the plan (faster but may be stale).",
     "cmd": "terraform plan -refresh=false",
     "example": "terraform plan -refresh=false -out=plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Plan & Apply Options"},
    {"id": "apply_refresh_only", "title": "terraform apply -refresh-only",
     "desc": "Update the state to match real infrastructure without changing any resources.",
     "cmd": "terraform apply -refresh-only",
     "example": "terraform apply -refresh-only -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Plan & Apply Options"},

    # Variable Management (explicit cards per request)
    {"id": "apply_var_file", "title": "terraform apply -var-file=<file.tfvars>",
     "desc": "Load variables from a .tfvars file during apply to provide consistent input values.",
     "cmd": "terraform apply -var-file=prod.tfvars",
     "example": "terraform apply -var-file=prod.tfvars -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/language/values/variables#variable-definitions-tfvars-files",
     "category": "Variable Management (explicit cards per request)"},
    {"id": "plan_var_file", "title": "terraform plan -var-file=<file.tfvars>",
     "desc": "Create a plan using variables sourced from a .tfvars file.",
     "cmd": "terraform plan -var-file=prod.tfvars -out=plan.tfplan",
     "example": "terraform plan -var-file=staging.tfvars -out=plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Variable Management (explicit cards per request)"},
    {"id": "apply_var_cli", "title": "terraform apply -var=\"key=value\"",
     "desc": "Apply with an immediate single variable override from the CLI.",
     "cmd": "terraform apply -var='image=ami-12345' -auto-approve",
     "example": "terraform apply -var='region=eu-west-1' -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/language/values/variables#passing-values-on-the-command-line",
     "category": "Variable Management (explicit cards per request)"},
    {"id": "plan_var_cli", "title": "terraform plan -var=\"key=value\"",
     "desc": "Plan using a single CLI-provided variable override.",
     "cmd": "terraform plan -var='image=ami-12345' -out=plan.tfplan",
     "example": "terraform plan -var='env=dev' -out=plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/language/values/variables#passing-values-on-the-command-line",
     "category": "Variable Management (explicit cards per request)"},
    {"id": "apply_lock_false", "title": "terraform apply -lock=false",
     "desc": "Disable state locking for this apply (dangerous for remote backends; use cautiously).",
     "cmd": "terraform apply -lock=false -auto-approve",
     "example": "terraform apply -lock=false -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Variable Management (explicit cards per request)"},
    {"id": "plan_input_false", "title": "terraform plan -input=false",
     "desc": "Run plan non-interactively by disabling prompts for missing input; useful in CI.",
     "cmd": "terraform plan -input=false -var-file=ci.tfvars",
     "example": "terraform plan -input=false -var-file=secrets.tfvars -out=plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Variable Management (explicit cards per request)"},

    # Resource Taint & Untaint
    {"id": "taint_cmd", "title": "terraform taint <resource>",
     "desc": "Mark a resource in the state to be recreated on the next apply.",
     "cmd": "terraform taint aws_instance.example",
     "example": "terraform taint aws_instance.old",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/taint",
     "category": "Resource Taint & Untaint"},
    {"id": "untaint_cmd", "title": "terraform untaint <resource>",
     "desc": "Remove a taint mark so the resource will not be recreated.",
     "cmd": "terraform untaint aws_instance.example",
     "example": "terraform untaint aws_instance.old",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/taint",
     "category": "Resource Taint & Untaint"},

    # Remote State Management
    {"id": "remote_config", "title": "terraform remote config",
     "desc": "Configure remote state storage (legacy command in older versions; use backend blocks with init).",
     "cmd": "terraform remote config",
     "example": "# Prefer backend block + terraform init\nterraform init -backend-config=\"bucket=my-bucket\"",
     "tf_link": "https://developer.hashicorp.com/terraform/language/state/overview",
     "category": "Remote State Management"},
    {"id": "backend_config", "title": "terraform init -backend-config",
     "desc": "Specify backend configuration values at init time or reconfigure existing backend.",
     "cmd": "terraform init -backend-config=backend.tf",
     "example": "terraform init -backend-config=\"bucket=my-bucket\" -reconfigure",
     "tf_link": "https://developer.hashicorp.com/terraform/language/state/overview",
     "category": "Remote State Management"},
    {"id": "state_push_remote", "title": "terraform state push (remote)",
     "desc": "Upload a local state file to the configured backend (advanced; be cautious).",
     "cmd": "terraform state push terraform.tfstate",
     "example": "terraform state push terraform.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Remote State Management"},
    {"id": "state_pull_remote", "title": "terraform state pull (remote)",
     "desc": "Download current remote state from the backend.",
     "cmd": "terraform state pull > current.tfstate",
     "example": "terraform state pull > backup-2025-10-22.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Remote State Management"},

    # Provider Management
    {"id": "providers_schema", "title": "terraform providers schema",
     "desc": "Show provider schema to inspect resource and data source attributes (JSON output available).",
     "cmd": "terraform providers schema -json",
     "example": "terraform providers schema -json > providers-schema.json",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/providers",
     "category": "Provider Management"},
    {"id": "providers_lock", "title": "terraform providers lock",
     "desc": "Generate a dependency lock file for providers to ensure reproducible installs.",
     "cmd": "terraform providers lock -platform=linux_amd64",
     "example": "terraform providers lock -platform=linux_amd64",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/providers",
     "category": "Provider Management"},
    {"id": "providers_mirror", "title": "terraform providers mirror",
     "desc": "Mirror provider plugins to a directory for air-gapped installs.",
     "cmd": "terraform providers mirror ./vendor",
     "example": "terraform providers mirror ./vendor",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/providers",
     "category": "Provider Management"},
    {"id": "providers_install", "title": "terraform providers install",
     "desc": "Install providers locally (used by some workflows).",
     "cmd": "terraform providers install",
     "example": "terraform init && terraform providers install",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/providers",
     "category": "Provider Management"},
    {"id": "init_upgrade", "title": "terraform init -upgrade",
     "desc": "Upgrade provider plugins to the newest allowed versions during init.",
     "cmd": "terraform init -upgrade",
     "example": "terraform init -upgrade",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/init",
     "category": "Provider Management"},

    # Locking and Unlocking
    {"id": "force_unlock", "title": "terraform force-unlock <lock-id>",
     "desc": "Manually remove a stale lock on the state using the lock ID (use carefully).",
     "cmd": "terraform force-unlock LOCK_ID",
     "example": "terraform force-unlock 1234-abcd-5678",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/force-unlock",
     "category": "Locking and Unlocking"},
    {"id": "apply_lock_timeout", "title": "terraform apply -lock-timeout",
     "desc": "Specify how long to wait when acquiring a state lock before failing.",
     "cmd": "terraform apply -lock-timeout=5m -auto-approve",
     "example": "terraform apply -lock-timeout=2m -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Locking and Unlocking"},

    # State Manipulation & Backups
    {"id": "state_push_file", "title": "terraform state push <file>",
     "desc": "Push a local state file to the remote backend (advanced restore or migration step).",
     "cmd": "terraform state push backup.tfstate",
     "example": "terraform state push backup.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "State Manipulation & Backups"},
    {"id": "state_pull_file", "title": "terraform state pull > file.tfstate",
     "desc": "Pull the current state and save it locally for backup or inspection.",
     "cmd": "terraform state pull > backup.tfstate",
     "example": "terraform state pull > backup-2025-10-22.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "State Manipulation & Backups"},
    {"id": "state_backup_restore", "title": "State snapshot & restore",
     "desc": "Create snapshots of state and restore from backups when needed.",
     "cmd": "terraform state pull > snapshot.tfstate",
     "example": "terraform state pull > snapshot.tfstate\n# restore: terraform state push snapshot.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "State Manipulation & Backups"},

    # Debugging & Logging
    {"id": "tf_log_debug", "title": "TF_LOG=DEBUG",
     "desc": "Enable debug-level logging to troubleshoot provider or plugin behavior.",
     "cmd": "TF_LOG=DEBUG TF_LOG_PATH=./tf.log terraform plan",
     "example": "TF_LOG=DEBUG TF_LOG_PATH=./tf.log terraform apply",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/log",
     "category": "Debugging & Logging"},
    {"id": "tf_log_info", "title": "TF_LOG=INFO",
     "desc": "Enable info-level logging for less verbose runtime logs.",
     "cmd": "TF_LOG=INFO terraform plan",
     "example": "TF_LOG=INFO terraform plan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/log",
     "category": "Debugging & Logging"},
    {"id": "tf_log_path", "title": "TF_LOG_PATH",
     "desc": "Redirect Terraform logs to a file with TF_LOG_PATH.",
     "cmd": "TF_LOG_PATH=./tf.log terraform apply",
     "example": "TF_LOG=DEBUG TF_LOG_PATH=./tf.log terraform plan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/log",
     "category": "Debugging & Logging"},
    {"id": "validate_json", "title": "terraform validate -json",
     "desc": "Produce machine-readable JSON validation output for tooling and CI.",
     "cmd": "terraform validate -json",
     "example": "terraform validate -json > validate.json",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/validate",
     "category": "Debugging & Logging"},
    {"id": "console", "title": "terraform console",
     "desc": "Interactive REPL to evaluate expressions against configuration and state.",
     "cmd": "terraform console",
     "example": "terraform console\n> var.count\n> module.vpc.subnet_ids",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/console",
     "category": "Debugging & Logging"},
    {"id": "providers_schema_json", "title": "terraform providers schema -json",
     "desc": "Output provider schema in JSON to inspect resource/data attributes programmatically.",
     "cmd": "terraform providers schema -json > schema.json",
     "example": "terraform providers schema -json > providers-schema.json",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/providers",
     "category": "Debugging & Logging"},

    # Experimental Commands
    {"id": "apply_replace", "title": "terraform apply -replace",
     "desc": "Force replacement of a specific resource during apply (selective recreate).",
     "cmd": "terraform apply -replace='aws_instance.example' -auto-approve",
     "example": "terraform apply -replace=aws_instance.example -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Experimental Commands"},
    {"id": "plan_refresh_false_exp", "title": "terraform plan -refresh=false (experimental)",
     "desc": "Skip refresh before planning to speed up CI; may operate on stale data.",
     "cmd": "terraform plan -refresh=false",
     "example": "terraform plan -refresh=false -out=plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Experimental Commands"},
    {"id": "destroy_target", "title": "terraform destroy -target",
     "desc": "Destroy a specific resource by targeting it (advanced; use with caution).",
     "cmd": "terraform destroy -target=aws_instance.example -auto-approve",
     "example": "terraform destroy -target=module.db.aws_db_instance.example -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/destroy",
     "category": "Experimental Commands"},

    # Modules
    {"id": "get", "title": "terraform get",
     "desc": "Download and update modules required by the configuration.",
     "cmd": "terraform get -update",
     "example": "terraform get && terraform get -update",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/get",
     "category": "Modules"},
    {"id": "init_get_plugins", "title": "terraform init -get-plugins",
     "desc": "Download necessary provider plugins; modern init handles this automatically.",
     "cmd": "terraform init -get-plugins",
     "example": "terraform init -get-plugins",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/init",
     "category": "Modules"},

    # Backups & Rollbacks
    {"id": "state_snapshot", "title": "terraform state snapshot",
     "desc": "Create a snapshot/backup of the current state for recovery purposes.",
     "cmd": "terraform state pull > snapshot.tfstate",
     "example": "terraform state pull > snapshot-2025-10-22.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Backups & Rollbacks"},
    {"id": "state_restore", "title": "terraform state restore",
     "desc": "Restore state from a backup file by pushing it back to the backend (advanced).",
     "cmd": "terraform state push snapshot.tfstate",
     "example": "terraform state push snapshot.tfstate",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/state",
     "category": "Backups & Rollbacks"},
    {"id": "apply_backup_flag", "title": "terraform apply -backup",
     "desc": "Specify a backup file to write current state before applying changes (provider-specific workflows).",
     "cmd": "terraform apply -backup=backup.tfstate",
     "example": "terraform apply -backup=backup-2025-10-22.tfstate -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Backups & Rollbacks"},

    # Automation & Scripting
    {"id": "apply_auto_approve_repeat", "title": "terraform apply -auto-approve",
     "desc": "Run apply automatically without confirmation; commonly used in automation pipelines.",
     "cmd": "terraform apply -auto-approve",
     "example": "terraform apply -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Automation & Scripting"},
    {"id": "plan_detailed_exitcode", "title": "terraform plan -detailed-exitcode",
     "desc": "Return exit codes that indicate whether a plan has changes (useful in CI to detect drift).",
     "cmd": "terraform plan -detailed-exitcode",
     "example": "terraform plan -detailed-exitcode || echo 'changes or error'",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Automation & Scripting"},
    {"id": "apply_parallelism", "title": "terraform apply -parallelism",
     "desc": "Limit concurrency of resource operations during apply to control API load.",
     "cmd": "terraform apply -parallelism=10 -auto-approve",
     "example": "terraform apply -parallelism=5 -auto-approve",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/apply",
     "category": "Automation & Scripting"},

    # Remote backend & collaboration
    {"id": "login_logout", "title": "terraform login / logout",
     "desc": "Authenticate to Terraform Cloud/Enterprise and remove local credentials.",
     "cmd": "terraform login",
     "example": "terraform login\nterraform logout",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/login",
     "category": "Remote backend & collaboration"},
    {"id": "init_backend_config", "title": "terraform init -backend-config",
     "desc": "Initialize backend with specific configuration values for remote state.",
     "cmd": "terraform init -backend-config=backend.tf",
     "example": "terraform init -backend-config=\"bucket=my-bucket\" -reconfigure",
     "tf_link": "https://developer.hashicorp.com/terraform/language/state/overview",
     "category": "Remote backend & collaboration"},

    # Miscellaneous & tips
    {"id": "init_force_copy", "title": "terraform init -force-copy",
     "desc": "Force copying of state data when reinitializing a backend (use carefully).",
     "cmd": "terraform init -force-copy",
     "example": "terraform init -force-copy -reconfigure -backend-config=\"bucket=my-bucket\"",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/init",
     "category": "Miscellaneous & tips"},
    {"id": "plan_compact_warnings", "title": "terraform plan -compact-warnings",
     "desc": "Reduce verbosity of warnings in plan output for cleaner logs.",
     "cmd": "terraform plan -compact-warnings -out=plan.tfplan",
     "example": "terraform plan -compact-warnings -out=plan.tfplan",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/plan",
     "category": "Miscellaneous & tips"},
    {"id": "fmt_recursive", "title": "terraform fmt -recursive",
     "desc": "Recursively format all .tf files under a directory.",
     "cmd": "terraform fmt -recursive",
     "example": "terraform fmt -recursive",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/fmt",
     "category": "Miscellaneous & tips"},
    {"id": "force_unlock_misc", "title": "terraform force-unlock",
     "desc": "Manually unlock the state using the lock ID to recover from stuck locks.",
     "cmd": "terraform force-unlock LOCK_ID",
     "example": "terraform force-unlock 1234-abcd-5678",
     "tf_link": "https://developer.hashicorp.com/terraform/cli/commands/force-unlock",
     "category": "Miscellaneous & tips"}
]

TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Terraform Arena </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      :root { --card-radius: 12px; --ocean-1: #e6f7ff; --ocean-2: #dff6ff; --ocean-3: #cfeef8; --accent: #0b57a4; }
      /* Ocean-like pleasant background that blends with section headers */
      body {
        background:
          radial-gradient(800px 350px at 10% 10%, rgba(11,87,164,0.06), transparent 8%),
          radial-gradient(700px 300px at 85% 80%, rgba(15,155,215,0.04), transparent 6%),
          linear-gradient(180deg, var(--ocean-1) 0%, var(--ocean-2) 45%, var(--ocean-3) 100%);
        color: #071236;
        -webkit-font-smoothing:antialiased;
        -moz-osx-font-smoothing:grayscale;
        min-height:100vh;
      }
      .app-shell { padding: 2.5rem; }
      .card-desc { font-size: .90rem; color: rgba(7,18,54,.8); margin-top:8px; font-weight:500 }
      .left-panel { max-width: 360px; margin-right: 20px; }
      .search { background: rgba(7,18,54,0.06); border: none; color: #071236; }
      a.topic-link { text-decoration:none; color: inherit; }
      .source { opacity: .9; font-size:.88rem; color: rgba(7,18,54,.85); }
      .chip { font-size:.78rem; padding: .22rem .5rem; border-radius: 999px; background: rgba(7,18,54,0.06); color: #071236; }
      pre.code-block { background: rgba(2,6,23,0.06); color: #071236; padding:12px; border-radius:8px; overflow:auto; font-family: Menlo, Monaco, monospace; font-size: .85rem; margin-top:8px; }
      .example-toggle { cursor:pointer; color: #0b57a4; text-decoration: underline; }
      footer { margin-top: 28px; color: rgba(7,18,54,.65); opacity:.95; font-size:.9rem;}
      .btn-copy { font-size:.75rem; padding:.25rem .5rem; }

      /* Author styling */
      .author { font-size: .85rem; color: rgba(7,18,54,0.7); margin-top:4px; font-style:italic; }

      /* Small top-right author avatar (compact, non-intrusive) */
      .author-card {
        position: fixed;
        top: 14px;
        right: 14px;
        z-index: 1200;
        display: flex;
        gap: 10px;
        align-items: center;
        padding: 8px 12px;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(3,37,76,0.95), rgba(9,78,121,0.92));
        color: #ffffff;
        box-shadow: 0 12px 30px rgba(2,6,23,0.18);
        backdrop-filter: blur(6px);
        transition: transform .12s ease, box-shadow .12s ease;
        cursor: default;
        min-width: 180px;
      }
      .author-card:hover { transform: translateY(-3px); box-shadow: 0 18px 36px rgba(2,6,23,0.22); }
      .author-card .avatar {
        width: 42px;
        height: 42px;
        min-width:42px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 20%, #ffd166 0%, #ef476f 35%, #d65f9d 100%);
        color: #071236;
        display:flex;
        align-items:center;
        justify-content:center;
        font-weight:800;
        font-size: .95rem;
        box-shadow: 0 6px 18px rgba(2,6,23,0.12);
      }
      .author-card .meta {
        display:flex;
        flex-direction:column;
        gap:2px;
        margin-left: 4px;
      }
      .author-card .name {
        font-weight:700;
        font-size: .95rem;
        color: #f1fbff;
      }
      .author-card .sub {
        font-size: .78rem;
        color: rgba(241,251,255,0.85);
        opacity: .95;
      }
      .author-card .badge {
        margin-left: auto;
        background: rgba(255,255,255,0.10);
        padding: 4px 8px;
        border-radius: 999px;
        font-size: .75rem;
        color: #fff;
      }

      /* Command cards panel styling */
      .cards-panel {
        border-radius:14px;
        padding:18px;
        background: linear-gradient(90deg, rgba(11,87,164,0.92) 0%, rgba(15,155,215,0.88) 50%, rgba(122,213,255,0.9) 100%);
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(11,87,164,0.12);
      }

      /* section header for grouped categories inside cards panel (rich, visible colors) */
      .section-header {
        width: 100%;
        padding: 10px 12px;
        margin-bottom: 6px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
        background: linear-gradient(90deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
        box-shadow: 0 6px 18px rgba(2,6,23,0.04);
        border-left: 6px solid rgba(255,255,255,0.06);
      }
      .category-pill {
        display:inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        color: #fff;
        font-weight:700;
        font-size: .92rem;
        box-shadow: 0 6px 18px rgba(2,6,23,0.08);
        white-space: nowrap;
      }
      .section-desc {
        color: rgba(255,255,255,0.92);
        font-weight:700;
        font-size: .95rem;
      }

      .command-card {
        background: #ffffff;
        color: #071236;
        border-radius: 10px;
        padding: 14px;
        box-shadow: 0 6px 18px rgba(2,6,23,0.06);
        height: 100%;
      }
      .command-card .score-badge {
        font-weight: 800;
        font-size: 1.05rem;
      }

      /* Make pills and headers blend slightly into page background */
      .category-pill.fade {
        background-image: linear-gradient(90deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
        color: rgba(7,18,54,0.9);
      }

      @media (max-width: 600px) {
        .author-card { top:8px; right:8px; padding:4px 6px; font-size:.78rem; }
        .author-card .name { display:none; }
        .author-card .avatar { width:26px; height:26px; font-size:.78rem; }
      }
    </style>
  </head>
  <body>
    <!-- Top-right rich author card -->
    <div class="author-card" title="© Prasanth K P">
      <div class="avatar">PK</div>
      <div class="meta">
        <div class="name">Prasanth K P</div>
      </div>
      <div class="badge">©</div>
    </div>

    <div class="container app-shell">
      <div class="d-flex align-items-start mb-4 gap-3 flex-column flex-md-row">
        <div class="left-panel bg-transparent">
          <h2 class="mb-1">Terraform — Cards & Examples</h2>
          <p class="author">Author: Prasanth K P</p>
          <p class="source">Expanded map of core commands and short examples. Use cards to reveal runnable snippets and links to docs.</p>
          <div class="mt-3">
            <input id="search" class="form-control search" placeholder="Search here..." />
          </div>
          <div class="mt-3 d-flex flex-column gap-2">
            <button id="reset" class="btn btn-sm btn-outline-primary w-100">Reset Filter</button>
            <a class="btn btn-sm btn-primary w-100" href="https://developer.hashicorp.com/terraform" target="_blank">Terraform Docs</a>
          </div>

          <div class="mt-4">
            <h6 class="mb-2">Legend</h6>
            <div class="d-flex gap-2 flex-wrap">
              <div class="chip">Common</div>
              <div class="chip">Advanced</div>
              <div class="chip">Best practice</div>
            </div>
          </div>
          <footer>
            Generated concise examples — always verify in official docs and your Terraform version.
          </footer>
        </div>

        <div class="flex-fill">
          <!-- Colored Command Cards panel -->
          <div class="cards-panel mb-3">
            <h4 style="color: #ffffff; margin-bottom:12px">Command Cards</h4>
            <div id="cards" class="row g-3 mt-2"></div>
          </div>
        </div>
      </div>
    </div>

    <script>
      const topics = {{ topics_json | safe }};

      // Hash a string to a hue 0-360 deterministically
      function hueForString(s) {
        let h = 0;
        for (let i = 0; i < s.length; i++) {
          h = (h * 31 + s.charCodeAt(i)) % 360;
        }
        return h;
      }
      // Build a pleasant gradient for a given category name
      function categoryGradient(name) {
        const h = hueForString(name);
        const h2 = (h + 40) % 360;
        const c1 = `hsl(${h}, 75%, 45%)`;
        const c2 = `hsl(${h2}, 65%, 55%)`;
        return `linear-gradient(90deg, ${c1}, ${c2})`;
      }

      // Utility: map score 0-100 to a color scale (green -> yellow -> red) used for score badge color
      function colorForScore(s) {
        let hue;
        if (s >= 50) {
          hue = 120 - ((s - 50) * (60 / 50));
        } else {
          hue = 60 - ((50 - s) * (60 / 50));
        }
        hue = Math.max(0, Math.min(120, hue));
        const lightness = 45 - (s / 8);
        return `hsl(${hue}, 78%, ${lightness}%)`;
      }

      function createCodeBlock(code) {
        const pre = document.createElement('pre');
        pre.className = 'code-block';
        pre.textContent = code;
        return pre;
      }

      function copyToClipboard(text, btn) {
        navigator.clipboard.writeText(text).then(() => {
          const prev = btn.innerText;
          btn.innerText = 'Copied';
          setTimeout(()=> btn.innerText = prev, 1200);
        }).catch(()=> {
          btn.innerText = 'Copy failed';
          setTimeout(()=> btn.innerText = 'Copy', 1200);
        });
      }

      function buildCards(filtered) {
        const container = document.getElementById('cards');
        container.innerHTML = '';
        const seenCategories = new Set();
        filtered.forEach((t, idx) => {
          // if item has a category, render a section header once before first item of that category
          if (t.category && !seenCategories.has(t.category)) {
            seenCategories.add(t.category);
            const hdrCol = document.createElement('div');
            hdrCol.className = 'col-12';
            const headerDiv = document.createElement('div');
            headerDiv.className = 'section-header';
            const pill = document.createElement('span');
            pill.className = 'category-pill';
            pill.innerText = `# ${t.category}`;
            // style pill with a generated gradient that's clearly visible
            pill.style.background = categoryGradient(t.category);
            headerDiv.appendChild(pill);
            // optional subtitle (keeps header readable)
            const desc = document.createElement('div');
            desc.className = 'section-desc';
            desc.style.marginLeft = '8px';
            desc.innerText = '';
            headerDiv.appendChild(desc);
            hdrCol.appendChild(headerDiv);
            container.appendChild(hdrCol);
          }

          const col = document.createElement('div');
          col.className = 'col-12 col-md-6 col-xl-4';
          const card = document.createElement('div');
          card.className = 'command-card p-3';

          const header = document.createElement('div');
          header.style.display = 'flex';
          header.style.justifyContent = 'space-between';
          header.style.alignItems = 'flex-start';

          const left = document.createElement('div');
          left.innerHTML = `<h6 style="margin-bottom:.25rem">${t.title}</h6><p style="margin:0; opacity:.85">${t.desc}</p>`;

          const right = document.createElement('div');
          right.style.textAlign = 'right';
          // Use score if present, otherwise hide
          const scoreHtml = t.score ? `<div class="score-badge" style="color:${colorForScore(t.score)}">${t.score}</div><div style="font-size:.75rem; opacity:.65">importance</div>` : '';
          right.innerHTML = scoreHtml;

          header.appendChild(left);
          header.appendChild(right);

          const actions = document.createElement('div');
          actions.style.marginTop = '12px';
          actions.style.display = 'flex';
          actions.style.gap = '8px';

          const docsBtn = document.createElement('a');
          // match the "Show example" button color (bootstrap secondary)
          docsBtn.className = 'btn btn-sm btn-secondary';
          docsBtn.href = t.tf_link || '#';
          docsBtn.target = '_blank';
          docsBtn.innerText = 'Official docs';

          const toggle = document.createElement('button');
          toggle.className = 'btn btn-sm btn-secondary';
          toggle.type = 'button';
          toggle.innerText = 'Show example';
          toggle.style.marginLeft = 'auto';

          actions.appendChild(docsBtn);
          actions.appendChild(toggle);

          const exampleWrapper = document.createElement('div');
          exampleWrapper.style.display = 'none';
          exampleWrapper.style.marginTop = '10px';

          if (t.cmd || t.example) {
            const cmdBlock = createCodeBlock((t.cmd ? t.cmd + '\\n' : '') + (t.example ? t.example : ''));
            exampleWrapper.appendChild(cmdBlock);

            const controls = document.createElement('div');
            controls.style.marginTop = '6px';
            controls.style.display = 'flex';
            controls.style.gap = '6px';

            const copyBtn = document.createElement('button');
            copyBtn.className = 'btn btn-sm btn-light btn-copy';
            copyBtn.innerText = 'Copy';
            copyBtn.onclick = () => copyToClipboard(cmdBlock.textContent, copyBtn);

            controls.appendChild(copyBtn);
            exampleWrapper.appendChild(controls);
          }

          toggle.addEventListener('click', () => {
            if (exampleWrapper.style.display === 'none') {
              exampleWrapper.style.display = 'block';
              toggle.innerText = 'Hide example';
            } else {
              exampleWrapper.style.display = 'none';
              toggle.innerText = 'Show example';
            }
          });

          card.appendChild(header);
          card.appendChild(actions);
          card.appendChild(exampleWrapper);
          col.appendChild(card);
          container.appendChild(col);
        });
      }

      function refresh(filterText='') {
        const ft = filterText.trim().toLowerCase();
        const filtered = topics.filter(t => {
          if (!ft) return true;
          const combined = (t.title + ' ' + (t.desc || '') + ' ' + (t.cmd || '') + ' ' + (t.example || '')).toLowerCase();
          return combined.includes(ft);
        });
        filtered.sort((a,b)=> (b.score||0)-(a.score||0));
        buildCards(filtered);
      }

      document.getElementById('search').addEventListener('input', (e)=> refresh(e.target.value));
      document.getElementById('reset').addEventListener('click', ()=> {
        document.getElementById('search').value = '';
        refresh('');
      });

      // initial render
      refresh('');
    </script>
  </body>
</html>
"""

@app.route("/")
def index():
    # Pass topics as JSON to template to ensure proper JS consumption
    topics_json = json.dumps(TOPICS)
    return render_template_string(TEMPLATE, topics_json=topics_json)

def open_browser():
    webbrowser.open("http://127.0.0.1:5000", new=2)

if __name__ == "__main__":
    threading.Timer(1.2, open_browser).start()
    print("Starting TerraformHeatMap web app on http://127.0.0.1:5000")
    app.run(debug=False, port=5000)
