# Git Guidelines for AI Assistant

## Commit Messages

Keep commits concise and descriptive. No emojis.

**Format:** `<type>: <description>`

**Types:**
- `feat` - new feature
- `fix` - bug fix
- `docs` - documentation changes
- `style` - formatting, no code change
- `refactor` - code restructuring
- `test` - adding/updating tests
- `chore` - maintenance tasks

**Examples:**
```
feat: add user authentication
fix: resolve memory leak in parser
docs: update API documentation
refactor: extract utility functions
feat(auth): implement OAuth integration
fix(parser): handle malformed JSON input
```

**Optional Scope Format:** `<type>(<scope>): <description>`
- Use scope for brand names, phases, or specific areas
- Keep scope short (max 10 chars)
- Examples: `(auth)`, `(api)`, `(ui)`, `(phase1)`

**Rules:**
- Use present tense ("add" not "added")
- Start with lowercase
- No period at end
- Max 50 characters total
- Be specific but brief

## Branch Naming Standards

**Format:** `<type>/<description>` or `<type>/<brand-or-phase>/<description>`

**Types:**
- `feature` - new functionality
- `fix` - bug fixes
- `hotfix` - urgent production fixes
- `docs` - documentation updates
- `refactor` - code restructuring
- `chore` - maintenance tasks

**Examples:**
```
feature/user-authentication
fix/memory-leak-parser
hotfix/security-vulnerability
docs/api-endpoints
refactor/payment-processing
```

**With Project Phases:**
```
feature/phase1/core-auth
feature/phase2/advanced-permissions
fix/phase1/validation-errors
chore/setup/ci-pipeline
```

**Rules:**
- Use lowercase with hyphens
- Be descriptive but concise
- No special characters except hyphens
- Start with type prefix
- Max 50 characters total

## Pull Request Descriptions

Be comprehensive and detailed. Include context, rationale, and impact.

**Template:**
```markdown
## Summary
Brief overview of changes

## Problem
What issue this solves or feature this adds

## Solution
How you implemented the fix/feature

## Changes
- List key modifications
- Include file changes if significant
- Note any breaking changes

## Testing
- How changes were tested
- Any edge cases considered
- Screenshots/videos if UI changes

## Impact
- Performance implications
- Security considerations
- Dependencies affected

## Additional Notes
- Future considerations
- Related issues/PRs
- Migration steps if needed
```

## Releases & Tags

Create releases using GitHub CLI with auto-generated tags.

**Command:**
```bash
gh release create v1.2.3 --generate-notes --title "Release v1.2.3"
```

**Release Notes Should Include:**
- **What's New** - major features added
- **Improvements** - enhancements and optimizations
- **Bug Fixes** - issues resolved
- **Breaking Changes** - backwards compatibility notes
- **Dependencies** - updated libraries/frameworks
- **Migration Guide** - if breaking changes exist

**Version Format:** Semantic versioning (v1.2.3)
- Major: breaking changes
- Minor: new features (backwards compatible)
- Patch: bug fixes

**Release Title Format:** "Release v1.2.3" or "v1.2.3 - Feature Name"

The GitHub CLI will automatically create the corresponding tag when you create a release.