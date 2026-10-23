# Secrets guardrail. Run: just check-secrets
check-secrets:
    gitleaks detect --no-git --redact --source .
