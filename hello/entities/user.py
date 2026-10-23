from django.db import connection, IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from ..enums.profile import Profile


class User:

    def __init__(self, name, account, profile, user_id=None, password=None):
        self.id = user_id
        self.name = name
        self.account = account
        self.profile = profile
        self.password = password

    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, account, profile
                FROM users
            """)
            rows = cursor.fetchall()

        return [
            User(
                name=row[1],
                account=row[2],
                profile=Profile(row[3]),
                user_id=row[0]
            )
            for row in rows
        ]

    @staticmethod
    def get_by_account(account):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, account, password, profile
                FROM users
                WHERE account = %s
            """, [account])
            row = cursor.fetchone()

        if row is None:
            return None

        return User(
            name=row[1],
            account=row[2],
            password=row[3],
            profile=Profile(row[4]),
            user_id=row[0]
        )

    @staticmethod
    def check_login(account, password):
        user = User.get_by_account(account)

        if user is None:
            return False

        return check_password(password, user.password)

    @staticmethod
    def save(name, account, password, confirm_password):
        if password != confirm_password:
            return False

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, account, password, profile)
                    VALUES (%s, %s, %s, %s)
                """, [
                    name,
                    account,
                    make_password(password),
                    Profile.OPERATOR.value
                ])

                return cursor.rowcount == 1

        except IntegrityError:
            return False
