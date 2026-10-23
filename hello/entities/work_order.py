from django.db import connection, transaction
from ..enums.work_order_status import Status

class Work_order:
    
    def __init__(self, id, title, description, status, responsible):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.responsible = responsible
        
    
    @staticmethod
    def get_all():
        """
        Regresa una lista de obj Work_order a partir de un fetch a la tabla
        users y work_orders
        """
        
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT wo.id, wo.title, wo.description, wo.status, u.name
                        FROM work_orders wo
                        LEFT JOIN users u ON u.id = wo.responsible
                    """)
            rows = cursor.fetchall()
            
        return [Work_order(row[0], row[1], row[2], Status(row[3]), row[4]) for row in rows]


    @staticmethod
    def get_counters():
        """
        Regresa la cantidad de ordenes en cada estado a manera de dictionary
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT wo.title, wo.description, wo.status, u.name
	                    FROM work_orders wo JOIN users u
                        ON u.id = wo.responsible
                           """)
            rows = cursor.fetchall()
            
        #Diccionario que tiene como keys el estado, y como value la cantidad de WO en respectivo estado para los dashborads
        contadores = {'total':len(rows), 
                      'pending':len([r for r in rows if r[2] == 1]),
                      'ongoing':len([r for r in rows if r[2] == 2]),
                      'finished':len([r for r in rows if r[2] == 3])}
            
        return contadores

    @staticmethod
    def create(title, description, status, responsible):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO work_orders
                (title, description, status, responsible)
                VALUES (%s, %s, %s, %s)
            """, [title, description, status, responsible])

            return cursor.lastrowid

    @staticmethod
    def get_responsibles():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name
                FROM users
                ORDER BY name
            """)
            rows = cursor.fetchall()

        return [
            {'id': row[0], 'name': row[1]}
            for row in rows
        ]

    
    @staticmethod
    def get_by_id(id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, description, status, responsible
                FROM work_orders
                WHERE id = %s
            """, [id])

            row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'status': row[3],
            'responsible': row[4]
        }

    @staticmethod
    def update(id, title, description, responsible):
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE work_orders
                SET title = %s,
                    description = %s,
                    responsible = %s
                WHERE id = %s
            """, [title, description, responsible, id])

            return cursor.rowcount

    
    @staticmethod
    def delete(order_id):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id
                    FROM work_orders
                    WHERE id = %s
                    FOR UPDATE
                """, [order_id])

                if cursor.fetchone() is None:
                    return "not_found"

                cursor.execute("""
                    SELECT 1
                    FROM work_orders_history
                    WHERE id_work_order = %s
                    LIMIT 1
                """, [order_id])

                if cursor.fetchone():
                    return "has_history"

                cursor.execute("""
                    DELETE FROM work_orders
                    WHERE id = %s
                """, [order_id])

                return "deleted"
