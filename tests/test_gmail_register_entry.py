import importlib
import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config_store import config_store


_CONFIG_TO_ENV = {
    "chatgpt_gmail_base_email": "CHATGPT_GMAIL_BASE_EMAIL",
    "chatgpt_gmail_alias_suffix": "CHATGPT_GMAIL_ALIAS_SUFFIX",
    "chatgpt_gmail_alt_alias_suffix": "CHATGPT_GMAIL_ALT_ALIAS_SUFFIX",
}


def _apply_gmail_test_config(
    config_overrides: dict[str, str] | None = None,
) -> tuple[dict[str, str], dict[str, str | None]]:
    resolved: dict[str, str] = {}
    previous_env: dict[str, str | None] = {}
    overrides = config_overrides or {}
    for config_key, env_key in _CONFIG_TO_ENV.items():
        override_value = str(overrides.get(config_key, "") or "").strip()
        if override_value:
            previous_env[env_key] = os.environ.get(env_key)
            os.environ[env_key] = override_value
            resolved[env_key] = override_value
            continue

        env_value = str(os.getenv(env_key, "") or "").strip()
        if env_value:
            resolved[env_key] = env_value
            continue

        config_value = str(config_store.get(config_key, "") or "").strip()
        if config_value:
            previous_env[env_key] = os.environ.get(env_key)
            os.environ[env_key] = config_value
            resolved[env_key] = config_value
    return resolved, previous_env


def _restore_env(previous_env: dict[str, str | None]) -> None:
    for env_key, previous_value in previous_env.items():
        if previous_value is None:
            os.environ.pop(env_key, None)
        else:
            os.environ[env_key] = previous_value


def _load_suite(
    config_overrides: dict[str, str] | None = None,
) -> tuple[unittest.TestSuite, dict[str, str], object, dict[str, str | None]]:
    resolved, previous_env = _apply_gmail_test_config(config_overrides=config_overrides)
    module_name = "tests.test_chatgpt_register_gmail"
    if module_name in sys.modules:
        module = importlib.reload(sys.modules[module_name])
    else:
        module = importlib.import_module(module_name)

    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    return suite, resolved, module, previous_env


def run_gmail_register_suite(
    config_overrides: dict[str, str] | None = None,
    *,
    verbosity: int = 2,
) -> dict[str, object]:
    buffer = io.StringIO()
    suite = None
    resolved: dict[str, str] = {}
    module = None
    previous_env: dict[str, str | None] = {}

    try:
        with redirect_stdout(buffer), redirect_stderr(buffer):
            suite, resolved, module, previous_env = _load_suite(
                config_overrides=config_overrides,
            )
            if resolved:
                print("Gmail 测试配置:")
                for env_key, value in resolved.items():
                    print(f"- {env_key}={value}")
            else:
                print("Gmail 测试配置: 未从设置页读取到值，将使用测试文件内默认值")

            result = unittest.TextTestRunner(
                stream=buffer,
                verbosity=verbosity,
            ).run(suite)
    finally:
        _restore_env(previous_env)

    resolved_addresses = {
        "base_email": getattr(module, "GMAIL_BASE_EMAIL", ""),
        "alias_email": getattr(module, "GMAIL_ALIAS_EMAIL", ""),
        "alt_alias_email": getattr(module, "GMAIL_ALT_ALIAS_EMAIL", ""),
    }
    return {
        "ok": result.wasSuccessful(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "resolved_env": resolved,
        "resolved_addresses": resolved_addresses,
        "output": buffer.getvalue(),
    }


def main() -> int:
    result = run_gmail_register_suite()
    sys.stdout.write(str(result.get("output", "")))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
