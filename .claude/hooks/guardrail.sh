#!/bin/bash
# .claude/hooks/guardrail.sh

# Read the JSON input from Claude via stdin

#
# Notse: 
#   make this executable with cmod +x
#   sudo apt install jq
#   (should be already in .devcontainer.json as ghcr.io/devcontainers/features/common-utils:2)
#

INPUT=$(cat)

# Extract the tool name and input details
TOOL=$(echo "$INPUT" | jq -r '.tool_name')

# 1. Block destructive root commands
if [[ "$TOOL" == "Bash" ]]; then
    CMD=$(echo "$INPUT" | jq -r '.tool_input.command')
    if [[ "$CMD" =~ rm\ .*-rf\ / || "$CMD" =~ rm\ .*-rf\ .*--no-preserve-root ]]; then
        echo "SECURITY_VIOLATION: Destructive root commands are prohibited." >&2
        exit 2
    fi
fi

# 2. Block access to .env files (Read or Write)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')
if [[ "$FILE_PATH" == *".env"* ]]; then
    echo "SECURITY_VIOLATION: Access to .env files is restricted to the human operator." >&2
    exit 2
fi

exit 0
