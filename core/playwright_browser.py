"""Playwright 浏览器启动辅助。"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional


_MISSING_EXECUTABLE_MARKERS = (
    "Executable doesn't exist",
    "Failed to launch chromium because executable doesn't exist",
)

_SYSTEM_CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    str(
        Path.home()
        / "Applications"
        / "Google Chrome.app"
        / "Contents/MacOS/Google Chrome"
    ),
)


def _looks_like_missing_executable_error(exc: Exception) -> bool:
    message = str(exc or "")
    return any(marker in message for marker in _MISSING_EXECUTABLE_MARKERS)


def resolve_system_chrome_executable() -> str:
    for candidate in _SYSTEM_CHROME_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            return str(path)
    return ""


def launch_chromium_with_fallback(
    chromium,
    launch_kwargs: dict,
    *,
    log_fn: Optional[Callable[[str], None]] = None,
):
    try:
        return chromium.launch(**launch_kwargs)
    except Exception as exc:
        if not _looks_like_missing_executable_error(exc):
            raise

        chrome_executable = resolve_system_chrome_executable()
        if not chrome_executable:
            raise

        fallback_kwargs = dict(launch_kwargs or {})
        fallback_kwargs.pop("channel", None)
        fallback_kwargs["executable_path"] = chrome_executable
        if log_fn:
            log_fn(f"Playwright 浏览器缺失，回退系统 Chrome: {chrome_executable}")
        return chromium.launch(**fallback_kwargs)
