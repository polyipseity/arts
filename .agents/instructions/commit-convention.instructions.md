# Commit convention

Keep commit messages small, descriptive, and machine-readable.

Recommended style: Conventional Commits (concise summary):

- Format: `type(scope?): short-description`
- Example: `fix(parser): handle empty input`

Common types

- `feat` — a new feature
- `fix` — a bug fix
- `docs` — documentation only changes
- `style` — formatting, missing semicolons, etc.
- `refactor` — code change that neither fixes a bug nor adds a feature
- `test` — adding or fixing tests
- `chore` — maintenance tasks

Guidelines

- Use imperative, present-tense subject (e.g., `add`, not `added`).
- Keep the subject line ≤ 100 characters; aim for ~50 characters.
- Include a body when the change needs explanation; reference issue/PR IDs in the footer.
- Run tests and linters before committing.

Agent-specific

- Present the proposed commit message to the user before committing changes.
- Include test-summary and changed-file list in the PR description when tests are added/modified.
