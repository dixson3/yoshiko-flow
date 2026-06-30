# Upstream #54 — Level up getting-started documentation

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/54
- **State:** OPEN
- **Labels:** type::task, priority::medium
- **Disposition in this plan:** partial (install / getting-started docs only)

## Body (verbatim)

> Improve the getting-started docs: how to properly initialize `yf` post-install for user scope,
> and the available configuration options — including upstream tracking (GitHub/GitLab/Jira/Linear)
> and beads usage. Should give a new user a clear path from install -> user-scope init ->
> configuring upstream + beads.

## How this plan partially addresses it

This plan owns the **install** half: Issue 5.1 rewrites `README.md` + `website/docs/install.md` so
`curl|sh` is the primary path (Homebrew secondary), and documents `yf self {update,install,uninstall}`,
the XDG dirs + env overrides (`XDG_*`, `YF_NO_UPDATE_CHECK`, `YF_VERSION`), the macOS quarantine note,
and uninstall. The **broader** getting-started arc (user-scope init flow, upstream-tracking
configuration across GitHub/GitLab/Jira/Linear, beads usage) is **out of scope here** and remains
open under #54 after this plan lands — reconcile by updating #54 to reflect the install-docs portion
done, not closing it.
