from django.db import connection
from ..enums.work_order_status import Status

class Work_order:
    
    def __init__(self, title, description, status, responsible):
        self.title = title
        self.description = description
        self.status = status
        self.responsible = responsible
        
    
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT wo.title, wo.description, wo.status, u.name
	                    FROM work_orders wo JOIN users u
                        ON u.id = wo.responsible
                           """)
            rows = cursor.fetchall()
            
        return [Work_order(row[0], row[1], Status(row[2]), row[3]) for row in rows]


