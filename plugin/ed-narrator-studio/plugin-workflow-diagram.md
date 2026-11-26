# Plugin Workflow Diagram

Here's a mermaid flowchart visualizing the ED Narrator Studio plugin's four-stage pipeline. This can be rendered in GitHub, GitLab, and many documentation viewers:

```mermaid
flowchart TD
    %% Styles
    classDef stage fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef output fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px

    %% Capture stage
    A[Start: Ask for demo] -->|Brief provided| B[check_status]
    B -->|App reachable| C[studio-capture]
    C -->|Film captured| D[Storyboard: studio-motion]

    %% Motion stage with approval
    D -->|Style approved| E[Render composed.mp4]
    E -->|Silent film saved| F[preview_script]
    F -->|Cues fixed| G[create_voiceover]

    %% Voice stage
    G -->|Voice + music| H[download_result]
    H -->|Voiced MP4| I[Report result]

    %% Decision point - style rejection
    class D decision
    class I output
    D -->|Style rejected| D

    %% Final output
```
## How the plugin connects to the app

```mermaid
flowchart LR
    C[Claude with the plugin] -->|stdio, started by uvx| M[ed-narrator connector]
    M -->|HTTP, loopback only| A[ED Narrator app<br/>127.0.0.1:18090, Docker 8090]
    I[(Input folders<br/>ED_NARRATOR_INPUT_DIRS)] -->|film, script, music: read only| M
    M -->|voiced files| O[(Output folder<br/>ED_NARRATOR_OUTPUT_DIR)]
```

The connector reads only the listed input folders, writes only the output folder, and talks only to a loopback address. See [Security](docs/security.md).
