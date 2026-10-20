from django.shortcuts import render
from .entities.user import User
from .entities.work_order import Work_order
# Create your views here.

def index(request):
    work_orders = Work_order.get_all()
    counters = Work_order.get_counters()
    return render(request, 'hello/index.html', {'work_orders':work_orders,'counters':counters})


def people(request):
    users = User.get_all()
    return render(request, 'hello/people.html', {'users':users})