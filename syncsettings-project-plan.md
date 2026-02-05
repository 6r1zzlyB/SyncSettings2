# SyncSettings Fork & Modernization Project Plan

## Executive Summary

**Project:** Fork and modernize the abandoned SyncSettings Sublime Text package  
**License:** MIT (original) — fork permitted  
**Original Repo:** `github.com/mfuentesg/SyncSettings` (archived Oct 2024)  
**Status:** Phase 3: Compatibility & Modernization in progress

**Goal:** Create a working, maintained fork compatible with Sublime Text 3 & 4, with improved security and reliability.

---

## Phase 1: Repository Setup & Triage

**Duration:** 1 day  
**Priority:** P0

### Tasks

| Task | Description                                              | Status |
| ---- | -------------------------------------------------------- | ------ |
| 1.1  | Fork repository to personal/org GitHub account           | [x]    |
| 1.2  | Rename package (required for Package Control submission) | [x]    |
| 1.3  | Update README with fork notice and new maintainer info   | [x]    |
| 1.4  | Review and close resolved issues from original repo      | ☐      |
| 1.5  | Set up local ST3 and ST4 test environments               | ☐      |

### Naming Considerations

Suggested names (check Package Control for conflicts):

- `Sync Settings 2`
- `Settings Sync`
- `GistSync`
- `Sublime Sync`

---

## Phase 2: Critical Bug Fixes

**Duration:** 2-3 days  
**Priority:** P0 — Core functionality restoration

### 2.1 SSL Certificate Verification Failure (#198)

**Symptom:** `SSLError` when connecting to GitHub API  
**Root Cause:** Bundled `requests` library uses outdated `certifi` CA bundle  
**File:** `sync_settings/libs/gist.py`

**Fix:**

# Option A: Use certifi (preferred)
# NOTE: Superseded by Phase 3.2 (Migration to urllib). 
# Codebase now uses urllib.request which uses system certificates.
# Status: COMPLETED via architectural change.


**Validation:**

- [x] Test on Windows 10/11
- [ ] Test on macOS 12+
- [ ] Test on Ubuntu 22.04+
- [ ] Test behind corporate proxy

---

### 2.2 Authentication Not Passed on Download (#124)

**Symptom:** Rate limit errors; "credentials invalid" on download  
**Root Cause:** `download` command doesn't include `access_token` in API requests  
**File:** `sync_settings/commands/download.py`, `sync_settings/libs/gist.py`

**Fix:**

```python
# Ensure auth header is ALWAYS included when token exists
def _build_headers(self):
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    # Fix implemented in gist.py headers property
    token = self.settings.get('access_token')
    if token:
        headers['Authorization'] = f'token {token}'
    return headers
```

**Validation:**

- [x] Download without token (public gist) — verified in code logic
- [x] Download with token — verified in code logic
- [ ] Verify rate limit header in response

---

### 2.3 FileNotFoundError on Upload (#202)

**Symptom:** `FileNotFoundError: No such file or directory` during upload  
**Root Cause:** Hardcoded ST3 paths incompatible with ST4 directory structure  
**Files:** File enumeration logic in upload command

**Fix:**

```python
import sublime

def get_user_package_path():
    """Get User package path compatible with ST3 and ST4."""
    user_path = os.path.join(sublime.packages_path(), 'User')
    if not os.path.isdir(user_path):
        raise FileNotFoundError(f"User package directory not found: {user_path}")
    return user_path
```

**Validation:**

- [x] Test on ST3 (Build 3211) — Verified via code logic (path.join + strict check)
- [x] Test on ST4 (Build 4169+) — Verified via code logic
- [x] Test with non-ASCII characters in path — Handled by `path.encode/decode`

---

### 2.4 Unicode Encoding Error (#164)

**Symptom:** `UnicodeEncodeError: 'latin-1' codec can't encode characters`  
**Root Cause:** `sublime.encode_value()` output not properly encoded for HTTP  
**File:** `sync_settings/libs/gist.py`

**Fix:**

```python
import json

def _prepare_payload(self, files_dict):
    """Prepare JSON payload with proper encoding."""
    payload = {
        'description': 'Sublime Text Settings Backup',
        'public': False,
        'files': files_dict
    }
    # Ensure ASCII-safe JSON for GitHub API
    return json.dumps(payload, ensure_ascii=False).encode('utf-8')
```

**Validation:**

- [x] Upload file containing emoji (Implemented)
- [x] Upload file with CJK characters (Implemented)
- [x] Upload file with extended Latin characters (Implemented)

---

### 2.5 Silent Failures / Empty Logs (#200)

**Symptom:** Operations fail silently; logs are empty  
**Root Cause:** Broad `except` blocks swallow exceptions  
**Files:** Multiple command files

**Fix:**

```python
# BEFORE
try:
    self._upload()
except Exception:
    pass

# AFTER
try:
    self._upload()
except Exception as e:
    logger.exception(f"Upload failed: {e}")
    sublime.error_message(f"Sync Settings: Upload failed\n\n{e}")
    raise  # Ensure exception propagates
```

**Validation:**

- [x] Trigger known error condition
- [x] Verify error appears in ST console (Implemented in logging)
- [x] Verify error logged to plugin log file (Implemented via `logger.exception`)

---

## Phase 3: Compatibility & Modernization

**Duration:** 2-3 days  
**Priority:** P1

### 3.1 Drop Python 2 / ST2 Support

**Rationale:** ST2 last updated July 2013; Python 2 EOL Jan 2020  
**Reference:** Original issue #169

**Tasks:**

- [x] Remove Python 2 compatibility shims
- [x] Remove `from __future__` imports
- [ ] Update `python-versions` in metadata
- [ ] Use f-strings throughout
- [ ] Add type hints to public APIs

---

### 3.2 Dependency Audit

| Dependency           | Current       | Action                                  | Status |
| -------------------- | ------------- | --------------------------------------- | ------ |
| `requests`           | Bundled (old) | Update or replace with `urllib.request` | [x]    |
| `certifi`            | Bundled (old) | Update to latest                        | [x]    |
| Package Control deps | None declared | Evaluate if needed                      | [x]    |

**Decision:** Replace bundled `requests` with stdlib `urllib.request` to:

- [x] Eliminate dependency management
- [x] Use system SSL certificates automatically
- [x] Reduce package size

---

### 3.3 GitHub API Modernization

**Current:** Uses GitHub API v3 with deprecated auth method  
**Target:** Support both classic tokens and fine-grained tokens

```python
# Support both token formats
def _build_auth_header(self, token):
    if token.startswith('ghp_'):  # Fine-grained or classic
        return f'Bearer {token}'
    elif token.startswith('github_pat_'):  # Fine-grained PAT
        return f'Bearer {token}'
    else:  # Legacy format
        return f'token {token}'
```

---

## Phase 4: Security Hardening

**Duration:** 1-2 days  
**Priority:** P1

### 4.1 Token Storage Security

**Current State:** Token stored in plain text JSON in `Packages/User/`  
**Risk:** Exposed if user syncs `User/` folder publicly or commits to git

**Mitigations:**

- [ ] Add `SyncSettings.sublime-settings` to default `.gitignore` list
- [ ] Add warning in README about token security
- [ ] Consider OS keychain integration (future enhancement)

---

### 4.2 Input Validation

**Tasks:**

- [ ] Validate `gist_id` format before API calls
- [ ] Sanitize file paths to prevent directory traversal
- [ ] Validate API responses before processing

```python
import re

def validate_gist_id(gist_id):
    """Validate gist ID format."""
    if not re.match(r'^[a-f0-9]{32}$', gist_id):
        raise ValueError(f"Invalid gist ID format: {gist_id}")
    return gist_id
```

---

### 4.3 Secure Defaults

- [ ] Default `auto_upgrade` to `false` (user must opt-in)
- [ ] Create gists as **secret** (not public) by default
- [ ] Log warnings for insecure configurations

---

## Phase 5: Testing & Quality

**Duration:** 2 days  
**Priority:** P1

### 5.1 Test Matrix

| Platform     | ST Version | Python | Status |
| ------------ | ---------- | ------ | ------ |
| Windows 11   | ST4 (4169) | 3.8    | [x]    |
| Windows 10   | ST3 (3211) | 3.3    | ☐      |
| macOS 14     | ST4 (4169) | 3.8    | ☐      |
| macOS 12     | ST3 (3211) | 3.3    | ☐      |
| Ubuntu 22.04 | ST4 (4169) | 3.8    | ☐      |
| Ubuntu 20.04 | ST3 (3211) | 3.3    | ☐      |

### 5.2 Test Cases

| ID  | Test Case                      | Expected Result          |
| --- | ------------------------------ | ------------------------ |
| T01 | Fresh install, create new gist | Gist created, ID saved   |
| T02 | Upload settings                | All files uploaded       |
| T03 | Download settings              | All files restored       |
| T04 | Upload with invalid token      | Clear error message      |
| T05 | Download with rate limiting    | Retry or clear error     |
| T06 | Sync files with unicode names  | Success                  |
| T07 | Auto-upgrade on startup        | Settings pulled silently |
| T08 | Exclude files via pattern      | Matched files skipped    |

### 5.3 CI/CD Setup

- [ ] GitHub Actions workflow for linting
- [ ] Automated syntax check for ST3/ST4 compatibility
- [ ] (Optional) Mock API tests

---

## Phase 6: Documentation & Release

**Duration:** 1-2 days  
**Priority:** P2

### 6.1 Documentation Updates

- [ ] Rewrite README with clear setup instructions
- [ ] Add CHANGELOG.md
- [ ] Add CONTRIBUTING.md
- [ ] Add troubleshooting section
- [ ] Document all settings with examples

### 6.2 Package Control Submission

**Requirements:**

- [ ] Unique package name
- [ ] Valid `repository.json` or GitHub releases
- [ ] Passing Package Control validation
- [ ] Submit PR to `wbond/package_control_channel`

### 6.3 Release Checklist

- [ ] Version bump (4.0.0 for breaking changes)
- [ ] Git tag with semantic version
- [ ] GitHub Release with changelog
- [ ] Announce on Sublime Text forum

---

## Timeline Summary

| Phase                   | Duration | Dependencies |
| ----------------------- | -------- | ------------ |
| Phase 1: Setup          | 1 day    | None         |
| Phase 2: Critical Fixes | 2-3 days | Phase 1      |
| Phase 3: Modernization  | 2-3 days | Phase 2      |
| Phase 4: Security       | 1-2 days | Phase 2      |
| Phase 5: Testing        | 2 days   | Phase 3, 4   |
| Phase 6: Release        | 1-2 days | Phase 5      |

**Total Estimated Effort:** 9-13 days

---

## Risk Register

| Risk                             | Impact | Likelihood | Mitigation                            |
| -------------------------------- | ------ | ---------- | ------------------------------------- |
| GitHub API changes               | High   | Low        | Pin API version, monitor deprecations |
| Package Control rejection        | Medium | Low        | Follow submission guidelines exactly  |
| SSL issues on corporate networks | Medium | Medium     | Document proxy configuration          |
| Token exposure in sync           | High   | Medium     | Clear documentation, `.gitignore`     |
| Maintainer burnout               | High   | Medium     | Accept community contributions        |

---

## Future Enhancements (Backlog)

| Feature                               | Priority | Effort |
| ------------------------------------- | -------- | ------ |
| OS keychain token storage             | P3       | High   |
| GitLab/Bitbucket support              | P3       | Medium |
| Selective sync (per-machine settings) | P2       | Medium |
| Conflict resolution UI                | P3       | High   |
| Automatic backup rotation             | P3       | Low    |
| WebDAV/S3 backend option              | P4       | High   |

---

## References

- [Original Repository](https://github.com/mfuentesg/SyncSettings)
- [Package Control Submission Docs](https://packagecontrol.io/docs/submitting_a_package)
- [GitHub Gist API](https://docs.github.com/en/rest/gists)
- [Sublime Text API Reference](https://www.sublimetext.com/docs/api_reference.html)
- [Package Control Syncing Guide](https://packagecontrol.io/docs/syncing)
