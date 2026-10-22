from django.db import connection, IntegrityError
from ..enums.profile import Profile
from django.contrib.auth.hashers import make_password, check_password

class User:
    
    def __init__(self, name, account, profile):
        self.name = name
        self.account = account
        self.profile = profile
        
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT name, account, profile FROM users
                    """)
            
            rows = cursor.fetchall()
            
        return [User(row[0], row[1], Profile(row[2])) for row in rows]
    
    @staticmethod
    def check_login(account, password):
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT password FROM users WHERE account = %s
                           """, [account])
            row = cursor.fetchone()
            
            if row != None:
                
                if check_password(password, row[0]):
                    return True #si las passwords coinciden
                return False #si existe el usuario pero la password es erronea
            
            return False #si el usuario no se encuentra
    
    @staticmethod
    def save(name, account, password, confirm_password):
        try:
            with connection.cursor() as cursor:
                
                if password != confirm_password:
                    return False
                
                cursor.execute("""
                            INSERT INTO users (name, account, password, profile)
                            VALUES (%s, %s, %s, %s)
                            """,
                            [name, account, make_password(password), 2])
                
                return cursor.rowcount == 1 #regresa True si pudo insertar la fila 
        except IntegrityError:
            return False