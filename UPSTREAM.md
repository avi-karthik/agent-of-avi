# Upstream Sync

## Source
- **Origin**: [cagataycali/strands-coder](https://github.com/cagataycali/strands-coder) (public reference implementation)
- **Extended reference**: [agent-of-mkmeral/strands-coder-private](https://github.com/agent-of-mkmeral/strands-coder-private) (production deployment with additional guardrails)
- **Maintainers**: mkmeral / cagataycali (Murat Meral / Cagatay Cali)

## Sync Cadence
- Check upstream weekly for new commits
- Prioritize pulling: security patterns, activity throttling, guardrails, new tools, bug fixes
- Review before merging: changes to system prompt, agent behavior, tool interfaces

## What to Pull
- Security guardrails (owner allowlist, activity throttling, self-trigger protection)
- New tools (projects, scheduler, knowledge base improvements)
- Workflow improvements (action.yml, agent.yml patterns)
- Bug fixes and stability improvements
- Observability features (Langfuse, OTEL, dashboard patterns)

## What NOT to Pull
- Strands-specific system prompt content
- Their authorized users list
- Their repo scope (strands-agents/*)
- Their git identity configuration
- Model configuration (we choose our own)

## How to Sync
```bash
git remote add upstream https://github.com/cagataycali/strands-coder.git
git fetch upstream
git log upstream/main --oneline -20  # Review recent commits
git cherry-pick <commit>             # Pull specific changes
# OR
git merge upstream/main              # Pull everything (review carefully)
```

## Changelog of Divergences
- `SYSTEM_PROMPT.md` — fully rewritten for AWS Amplify / Blocks scope
- `.github/workflows/agent.yml` — all events enabled, git identity set to agent-of-avi/avinash-karthik, 4-hour schedule enabled
