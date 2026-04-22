import random
import unittest

from platforms.chatgpt.gmail_alias import (
    build_gmail_alias_address,
    generate_gmail_alias_suffix,
    normalize_gmail_base_address,
)


class GmailAliasTests(unittest.TestCase):
    def test_normalize_gmail_base_address_strips_existing_tag(self):
        self.assertEqual(
            normalize_gmail_base_address("FooYouLiao2+oldtag@gmail.com"),
            "fooyouliao2@gmail.com",
        )

    def test_normalize_googlemail_domain_to_gmail(self):
        self.assertEqual(
            normalize_gmail_base_address("fooyouliao2@googlemail.com"),
            "fooyouliao2@gmail.com",
        )

    def test_normalize_rejects_non_gmail_domain(self):
        with self.assertRaises(ValueError):
            normalize_gmail_base_address("demo@example.com")

    def test_generate_gmail_alias_suffix_supports_seeded_rng(self):
        rng = random.Random(7)
        self.assertEqual(
            generate_gmail_alias_suffix(6, rng=rng),
            "ujzde8",
        )

    def test_build_gmail_alias_address_with_explicit_suffix(self):
        result = build_gmail_alias_address(
            "fooyouliao2@gmail.com",
            suffix="abc123",
        )

        self.assertEqual(result.base_email, "fooyouliao2@gmail.com")
        self.assertEqual(result.canonical_local_part, "fooyouliao2")
        self.assertEqual(result.suffix, "abc123")
        self.assertEqual(result.alias_email, "fooyouliao2+abc123@gmail.com")

    def test_build_gmail_alias_address_generates_suffix(self):
        rng = random.Random(11)
        result = build_gmail_alias_address(
            "fooyouliao2+legacy@gmail.com",
            suffix_length=5,
            rng=rng,
        )

        self.assertEqual(result.base_email, "fooyouliao2@gmail.com")
        self.assertEqual(result.alias_email, "fooyouliao2+29326@gmail.com")


if __name__ == "__main__":
    unittest.main()
