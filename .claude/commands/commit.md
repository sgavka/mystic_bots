Compose a git commit message for all current changes.

Steps:
1. Run `git status` to see all modified, staged, and untracked files
2. Run `git diff` to see unstaged changes
3. Run `git diff --cached` to see staged changes
4. Analyze all changes and compose a commit message following the format from CLAUDE.md:

Format:
```
type: [short description in general]

- Detailed point 1;
- Detailed point 2;
- More details as needed.
```

Types:fix
- feat: New feature or functionality
- improvement: Enhancement to existing feature
- fix: Bug fix
- refactor: Code refactoring without behavior change
- docs: Documentation changes
- test: Adding or updating tests
- chore: Maintenance tasks, dependencies, configs

DO NOT stage or commit automatically. Only present the composed commit message.

After presenting the message:
1. Copy the commit message to clipboard using: `echo -n "MESSAGE" | xclip -selection clipboard`
2. Inform user that the message was copied to clipboard
3. Ask if user wants to proceed with the commit

IMPORTANT:
- Do NOT add "Generated with Claude Code" or similar attribution
- Do NOT add "Co-Authored-By" lines
- Keep the commit message clean and focused on the changes only
