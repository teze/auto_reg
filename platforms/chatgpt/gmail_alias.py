"""Gmail 别名邮箱生成工具。

仅负责生成形如 ``name+suffix@gmail.com`` 的地址，不处理收件、登录或验证码读取。
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import string


_DEFAULT_SUFFIX_ALPHABET = string.ascii_lowercase + string.digits


@dataclass(frozen=True)
class GmailAliasAddress:
    base_email: str
    canonical_local_part: str
    suffix: str
    alias_email: str


def normalize_gmail_base_address(base_email: str) -> str:
    """归一化 Gmail 基础地址。

    - 仅接受 ``gmail.com`` / ``googlemail.com``
    - 移除已有 ``+tag``
    - 统一输出为 ``gmail.com``
    """
    value = str(base_email or "").strip().lower()
    if not value or "@" not in value:
        raise ValueError("Gmail 基础邮箱格式无效")

    local_part, domain = value.split("@", 1)
    local_part = local_part.strip()
    domain = domain.strip()

    if not local_part:
        raise ValueError("Gmail 本地部分不能为空")
    if domain not in {"gmail.com", "googlemail.com"}:
        raise ValueError("仅支持 gmail.com / googlemail.com 地址")

    canonical_local = local_part.split("+", 1)[0].strip()
    if not canonical_local:
        raise ValueError("Gmail 本地部分不能为空")

    return f"{canonical_local}@gmail.com"


def generate_gmail_alias_suffix(
    length: int = 8,
    *,
    alphabet: str = _DEFAULT_SUFFIX_ALPHABET,
    rng: random.Random | None = None,
) -> str:
    """生成 Gmail 别名后缀。"""
    size = max(int(length or 0), 1)
    charset = str(alphabet or "").strip()
    if not charset:
        raise ValueError("后缀字符集不能为空")

    chooser = rng or random.SystemRandom()
    return "".join(chooser.choice(charset) for _ in range(size))


def build_gmail_alias_address(
    base_email: str,
    *,
    suffix: str | None = None,
    suffix_length: int = 8,
    separator: str = "+",
    alphabet: str = _DEFAULT_SUFFIX_ALPHABET,
    rng: random.Random | None = None,
) -> GmailAliasAddress:
    """根据基础 Gmail 地址构造别名地址。"""
    normalized = normalize_gmail_base_address(base_email)
    local_part, _ = normalized.split("@", 1)
    resolved_suffix = str(suffix or "").strip().lower()
    if not resolved_suffix:
        resolved_suffix = generate_gmail_alias_suffix(
            suffix_length,
            alphabet=alphabet,
            rng=rng,
        )

    sep = str(separator or "+")
    alias_email = f"{local_part}{sep}{resolved_suffix}@gmail.com"
    return GmailAliasAddress(
        base_email=normalized,
        canonical_local_part=local_part,
        suffix=resolved_suffix,
        alias_email=alias_email,
    )
