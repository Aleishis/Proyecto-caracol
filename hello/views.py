from django.shortcuts import render, redirect
from .entities.user import User
from .entities.work_order import Work_order
# Create your views here.

def work_orders(request):
    work_orders = Work_order.get_all()
    counters = Work_order.get_counters()
    return render(request, 'hello/work_orders.html', {'work_orders':work_orders,'counters':counters})


def people(request):
    users = User.get_all()
    return render(request, 'hello/people.html', {'users':users})

def index(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.check_login(email, password):
            return redirect('work_orders')
    
    return render(request, 'hello/index.html')

def signup(request):
    
    if request.method == 'POST':
        name = request.POST.get('name')
        account = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        if User.save(name, account, password, confirm_password):
           return redirect('index')
    
    return render(request, 'hello/signup.html')