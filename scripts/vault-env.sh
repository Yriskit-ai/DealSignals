#!/bin/bash
# Fetch API keys from Vault using OIDC login
# Usage: source scripts/vault-env.sh
#        OR: eval "$(scripts/vault-env.sh --export)"

set -e

export VAULT_ADDR="https://butter.tail985add.ts.net:8200"
export VAULT_SKIP_VERIFY=1

# Check if already logged in
if ! vault token lookup &>/dev/null; then
    echo "Logging in to Vault via OIDC..." >&2
    vault login -method=oidc >&2
fi

# Fetch API keys from Vault
# Adjust paths as needed based on your Vault structure
echo "Fetching API keys from Vault..." >&2

# Try to get Claude/Anthropic key
if ANTHROPIC_KEY=$(vault kv get -field=api_key secret/api-keys/claude 2>/dev/null || vault kv get -field=key secret/api-keys/claude 2>/dev/null || vault kv get -field=ANTHROPIC_API_KEY secret/api-keys/claude 2>/dev/null); then
    export ANTHROPIC_API_KEY="$ANTHROPIC_KEY"
    echo "ANTHROPIC_API_KEY loaded" >&2
fi

# Try to get OpenAI key
if OPENAI_KEY=$(vault kv get -field=api_key secret/api-keys/openai 2>/dev/null || vault kv get -field=key secret/api-keys/openai 2>/dev/null || vault kv get -field=OPENAI_API_KEY secret/api-keys/openai 2>/dev/null); then
    export OPENAI_API_KEY="$OPENAI_KEY"
    echo "OPENAI_API_KEY loaded" >&2
fi

# Try to get Google/Gemini key
if GOOGLE_KEY=$(vault kv get -field=api_key secret/api-keys/google 2>/dev/null || vault kv get -field=key secret/api-keys/google 2>/dev/null || vault kv get -field=GOOGLE_API_KEY secret/api-keys/google 2>/dev/null); then
    export GOOGLE_API_KEY="$GOOGLE_KEY"
    echo "GOOGLE_API_KEY loaded" >&2
elif GEMINI_KEY=$(vault kv get -field=api_key secret/api-keys/gemini 2>/dev/null || vault kv get -field=key secret/api-keys/gemini 2>/dev/null); then
    export GOOGLE_API_KEY="$GEMINI_KEY"
    echo "GOOGLE_API_KEY loaded (from gemini)" >&2
fi

# If called with --export, output export statements for eval
if [[ "$1" == "--export" ]]; then
    [[ -n "$ANTHROPIC_API_KEY" ]] && echo "export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'"
    [[ -n "$OPENAI_API_KEY" ]] && echo "export OPENAI_API_KEY='$OPENAI_API_KEY'"
    [[ -n "$GOOGLE_API_KEY" ]] && echo "export GOOGLE_API_KEY='$GOOGLE_API_KEY'"
fi

echo "Done. Keys available in environment." >&2
