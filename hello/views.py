from functools import wraps

from django.shortcuts import render, redirect
from django.http import Http404

from .entities.user import User
from .entities.work_order import Work_order
from .entities.work_orders_history import Work_Orders_History
from .enums.profile import Profile
from .enums.work_order_status import Status


def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('index')

        if request.session.get('profile') != 1:
            return redirect('work_orders')

        return view_func(request, *args, **kwargs)
    return wrapper


@login_required_custom
def work_orders(request):
    work_orders = Work_order.get_all()
    counters = Work_order.get_counters()

    return render(request, 'hello/work_orders.html', {
        'work_orders': work_orders,
        'counters': counters
    })


@admin_required
def people(request):
    error = None

    if request.method == 'POST':
        try:
            user_id = int(request.POST.get('user_id', ''))
            profile = Profile(int(request.POST.get('profile', '')))
        except (ValueError, TypeError):
            error = 'Invalid user or profile.'
        else:
            if user_id == request.session.get('user_id'):
                error = 'You cannot change your own profile.'
            elif User.update_profile(user_id, profile) == 0:
                error = 'User not found.'
            else:
                return redirect('people')

    users = User.get_all()

    return render(request, 'hello/people.html', {
        'users': users,
        'profiles': list(Profile),
        'current_user_id': request.session.get('user_id'),
        'error': error
    })


def index(request):
    if request.session.get('user_id'):
        return redirect('work_orders')

    error = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = User.get_by_account(email)

        if user and User.check_login(email, password):
            request.session.cycle_key()
            request.session['user_id'] = user.id
            request.session['profile'] = int(user.profile)
            request.session['name'] = user.name
            request.session.set_expiry(1800)

            return redirect('work_orders')

        error = 'Correo o contraseña incorrectos.'

    return render(request, 'hello/index.html', {
        'error': error
    })

def logout_view(request):
    request.session.flush()
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        account = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if User.save(name, account, password, confirm_password):
            return redirect('index')

    return render(request, 'hello/signup.html')


@admin_required
def add_work_order(request):
    users = Work_order.get_responsibles()
    error = None

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if not title or not description:
            error = 'Title and description are required.'
        elif len(title) > 60:
            error = 'Title must have at most 60 characters.'
        else:
            try:
                status = Status(int(request.POST.get('status', '')))
                responsible = int(request.POST.get('responsible', ''))
            except (ValueError, TypeError):
                error = 'Invalid status or responsible.'
            else:
                if not any(int(u['id']) == responsible for u in users):
                    error = 'Please select a valid responsible.'
                else:
                    Work_order.create(
                        title, description, status.value, responsible
                    )
                    return redirect('work_orders')

    return render(request, 'hello/add_work_order.html', {
        'users': users,
        'statuses': list(Status),
        'error': error
    })


@login_required_custom
def edit_work_order(request, order_id):
    order = Work_order.get_by_id(order_id)

    if order is None:
        raise Http404('Work order not found')

    history = Work_Orders_History.get_history(order_id)
    users = Work_order.get_responsibles()
    error = None

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if not title or not description:
            error = 'Title and description are required.'
        elif len(title) > 60:
            error = 'Title must have at most 60 characters.'
        else:
            try:
                status = Status(int(request.POST.get('status', '')))
                responsible = int(request.POST.get('responsible', ''))
            except (ValueError, TypeError):
                error = 'Invalid status or responsible.'
            else:
                if not any(int(u['id']) == responsible for u in users):
                    error = 'Please select a valid responsible.'
                else:
                    Work_order.update(
                        order_id,
                        title,
                        description,
                        status,
                        responsible
                    )
                    Work_Orders_History.add_history(
                        responsible,
                        status.value,
                        order_id,
                        description
                    )
                    return redirect('work_orders')

    return render(request, 'hello/edit_work_order.html', {
        'order': order,
        'users': users,
        'statuses': list(Status),
        'error': error,
        'history': history
    })


@admin_required
def delete_work_order(request, order_id):
    order = Work_order.get_by_id(order_id)

    if order is None:
        raise Http404('Work order not found')

    error = None

    if request.method == 'POST':
        result = Work_order.delete(order_id)

        if result == 'deleted':
            return redirect('work_orders')
        if result == 'not_found':
            raise Http404('Work order not found')

        error = 'This order has a history and cannot be deleted.'

    return render(request, 'hello/delete_work_order.html', {
        'order': order,
        'error': error
    })
