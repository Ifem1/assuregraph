import os
import pytest

# genlayer-test 0.29.2 otherwise chooses the newest GenVM release. That can be
# a release candidate which no longer ships the stable runner hash pinned by
# these contracts. Keep Direct Mode deterministic on the compatible stable
# artifact; this does not alter the contract SDK or any network target.
try:
    import gltest.direct.sdk_loader as _sdk_loader

    _sdk_loader.get_latest_version = lambda: "v0.2.16"
except ImportError:
    pass

_PENDING_STDIN_FILES: list[str] = []

@pytest.fixture(autouse=True)
def _defer_open_stdin_unlinks(monkeypatch):
    """Work around genlayer-test 0.29.2's fd-0 temp-file cleanup on Windows.

    Direct Mode replaces fd 0 with the message file, then unlinks that file
    immediately. Windows refuses to unlink an open file; the next fd-0
    replacement closes the previous handle, so retry its deletion then.
    This keeps the pinned runner and exercises the real contract unchanged.
    """
    if os.name != "nt":
        yield
        return

    original_unlink = os.unlink
    def windows_safe_unlink(path, *args, **kwargs):
        remaining = []
        for deferred in _PENDING_STDIN_FILES:
            try:
                original_unlink(deferred)
            except FileNotFoundError:
                pass
            except PermissionError:
                remaining.append(deferred)
        _PENDING_STDIN_FILES[:] = remaining

        try:
            return original_unlink(path, *args, **kwargs)
        except PermissionError as exc:
            if getattr(exc, "winerror", None) != 32:
                raise
            _PENDING_STDIN_FILES.append(os.fspath(path))

    monkeypatch.setattr(os, "unlink", windows_safe_unlink)
    yield


@pytest.fixture(autouse=True)
def _keep_direct_mode_message_time_in_sync(direct_vm, monkeypatch):
    """The pinned runner's warp updates VMContext but not SDK message_raw."""
    original_warp = direct_vm.warp

    def warp_and_refresh_message(timestamp):
        original_warp(timestamp)
        try:
            import genlayer.gl as gl
        except ImportError:
            return
        if isinstance(getattr(gl, "message_raw", None), dict):
            gl.message_raw["datetime"] = timestamp

    monkeypatch.setattr(direct_vm, "warp", warp_and_refresh_message)


@pytest.fixture(autouse=True)
def _reset_contract_registry():
    yield
    try:
        import genlayer.gl.genvm_contracts as contracts
    except ImportError:
        return
    contracts.__known_contract__ = None
