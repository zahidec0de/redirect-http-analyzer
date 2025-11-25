# redirect-http-analyzer
A Python script that analyzes website redirect chains and scans static HTML to detect insecure HTTP links.

## WHAT THIS SCRIPT DOES?---

### A) Redirect Chain Analysis
    -Starts with the input URL
    - Follows up to 5 redirects
    - Records each step
    - Flags if any step uses HTTP

### B) Static HTML Analysis

    - Extracts insecure links from:
    - <a href="http://...">
    - <meta http-equiv="refresh" content="url=http://...">
    - Does NOT execute JavaScript (same limitation as CTM360)

### C) Output
    - Clear human-readable report
    - Full JSON for ingestion
