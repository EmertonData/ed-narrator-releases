# Plugin evals

Five cases for `claude plugin eval`, each run three times with and without the plugin:

| Case | Checks |
|---|---|
| `brief-before-action` | a vague demo request gets a short brief before any work |
| `approval-stop` | the style is approved by the user before the heavy render |
| `no-fire-css` | a generic CSS animation request does not trigger the studio |
| `tight-lines` | a cue far too long for its slot is shortened, only that cue |
| `install-confirm` | a large engine is never installed without the size and a yes |

```text
cd plugin/ed-narrator-studio
claude plugin eval . --no-publish --max-cost-usd 8
```

The plugin's real connector is not started (no mock), so Claude cannot reach `check_status`. These cases test what the skills tell Claude to do before and around the tool calls, not a full render. Results go to `evals/results/` (ignored).
