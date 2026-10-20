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
        """
        Regresa una lista de obj Work_order a partir de un fetch a la tabla
        users y work_orders
        """
        
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT wo.title, wo.description, wo.status, u.name
	                    FROM work_orders wo JOIN users u
                        ON u.id = wo.responsible
                           """)
            rows = cursor.fetchall()
            
        return [Work_order(row[0], row[1], Status(row[2]), row[3]) for row in rows]


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