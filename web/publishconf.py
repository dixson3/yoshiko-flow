# Used only by `make publish` (production build) or when passed explicitly as -s.
import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *  # noqa: F401,F403

# Canonical public site URL — required for the production build, from the environment (local
# .envrc / GitHub repo secret PUBLISH_URL). Never hardcoded here. A non-empty SITEURL anchors
# every generated link on it, which is exactly what the production build wants.
SITEURL = os.environ.get("PUBLISH_URL") or ""
if not SITEURL:
    raise RuntimeError(
        "PUBLISH_URL is required for the production build (it becomes Pelican's SITEURL). "
        "Set it in the repo's .envrc (direnv) or the CI environment."
    )
INSTALL_URL = SITEURL + "/install.sh"
RELATIVE_URLS = False

DELETE_OUTPUT_DIRECTORY = True

# Google Analytics (GA4) — PRODUCTION ONLY. The measurement id is account-specific and is
# NEVER committed: it is read from the environment (local .envrc + GitHub repo secret
# YOSHIKOFLOW_GA_MEASUREMENT_ID). Set here (not in pelicanconf.py) so dev/`make devserver`
# and PR builds never load analytics. When unset, base.html renders no gtag snippet.
GA_MEASUREMENT_ID = os.environ.get("YOSHIKOFLOW_GA_MEASUREMENT_ID")
