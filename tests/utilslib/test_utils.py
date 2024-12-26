from unittest import TestCase
from libs.utilslib.utils import is_valid_email


class UtilsTestCase(TestCase):
    def setUp(self):
        pass

    def test_valid_emails(self):
        valid_emails = [
            "example@example.com",
            "user.name+tag+sorting@example.com",
            "user@sub.example.com",
            "user@example.co.uk",
            "customer/department=shipping@example.com",
            "user.name@example.com",
            "user_name@example.com",
            "user-name@example.com",
            "u.s.e.r.n.a.m.e@mail.com",
        ]
        for email in valid_emails:
            self.assertTrue(
                is_valid_email(email),
                f"Valid email has been marked as invalid: {email}",
            )

    def test_invalid_emails(self):
        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "username@.com\nusername@com",
            "tryme\ntryme\nusername@com",
            "\nusername@com\n",
            "user name@com",
            "username@c om",
            "username@.com",
            "username@.com.",
            "username@.com@com.com",
            "username@.com..com",
            "username@.com,com",
            "username@-example.com",
            "username@example..com",
            "username@.example.com",
            "username@.com@example.com",
            "username@sub.example..com",
            "u..s.e.r.n.a.m.e@mail.com",
            "u.s.e.r.n.a.m.e@mail.com.",
            ".u.s.e.r.n.a.m.e@mail.com",
        ]
        for email in invalid_emails:
            self.assertFalse(
                is_valid_email(email),
                f"Invalid email has been marked as valid: {email}",
            )
