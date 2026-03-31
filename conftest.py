import os

import pytest


def pytest_collection_modifyitems(config, items):
    """
    By default we skip integration tests because they depend on external network,
    Tor, and/or unstable third-party services.

    Enable by setting RUN_INTEGRATION=1 or passing -m integration explicitly.
    """
    run_integration = os.environ.get("RUN_INTEGRATION") == "1"

    # If user explicitly selected integration via -m, don't auto-skip.
    markexpr = getattr(config.option, "markexpr", "") or ""
    explicitly_selected = "integration" in markexpr

    if run_integration or explicitly_selected:
        return

    skip_integration = pytest.mark.skip(reason="integration test (set RUN_INTEGRATION=1 or use -m integration)")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)

