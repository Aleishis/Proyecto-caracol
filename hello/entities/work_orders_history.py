from django.db import connection
from ..enums.work_order_status import Status

class Work_Orders_History:
    
    def __init__(self, date, title, responsible, status, description):
        self.date = date
        self.title = title
        self.responsible = responsible
        self.status = status
        self.description = description
        
        
    @staticmethod
    def get_history(order_id):
        
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT wh.date, w.title, u.name, wh.status, wh.description
                        FROM work_orders_history wh JOIN users u
                        ON wh.id_user = u.id
                        JOIN work_orders w ON w.id = wh.id_work_order
                        WHERE %s = wh.id_work_order
                           """, [order_id])
            
            rows = cursor.fetchall()
            
            return [Work_Orders_History(row[0], row[1], row[2], Status(row[3]), row[4]) for row in rows]

    def add_history(id_user, status, id_work_order, description):
        
        with connection.cursor() as cursor:
            cursor.execute("""
                        INSERT INTO work_orders_history (id_user, status, id_work_order, description)
                        VALUES (%s, %s, %s, %s)
                           """, [id_user, status, id_work_order, description])
            return cursor.lastrowid