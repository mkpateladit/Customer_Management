# from django.contrib import messages
# from django.contrib.auth import login
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Q
# from django.http import HttpResponseForbidden
# from django.shortcuts import render, redirect, get_object_or_404

# from .forms import CustomerForm, DistributorRegisterForm
# from .models import Customer


# def register(request):
#     """Self-service signup for new Distributor accounts."""
#     if request.user.is_authenticated:
#         return redirect('customers:customer_list')

#     if request.method == 'POST':
#         form = DistributorRegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, f"Welcome, {user.username}! Your distributor account is ready.")
#             return redirect('customers:customer_list')
#     else:
#         form = DistributorRegisterForm()
#     return render(request, 'customers/register.html', {'form': form})


# def _base_queryset(user):
#     """Distributors only see their own customers. Admin / Super Admin see all."""
#     profile = getattr(user, 'profile', None)
#     if profile and profile.is_admin:
#         return Customer.objects.select_related('distributor').all()
#     return Customer.objects.filter(distributor=user)


# def _get_owned_customer_or_none(request, pk):
#     """Fetch a customer, enforcing that a distributor can only touch their own records."""
#     customer = get_object_or_404(Customer, pk=pk)
#     profile = getattr(request.user, 'profile', None)
#     if profile and profile.is_admin:
#         return customer
#     if customer.distributor_id == request.user.id:
#         return customer
#     return None


# @login_required
# def customer_list(request):
#     query = request.GET.get('q', '').strip()
#     status_filter = request.GET.get('status', '').strip()

#     customers = _base_queryset(request.user)

#     if query:
#         customers = customers.filter(
#             Q(name__icontains=query) |
#             Q(email__icontains=query) |
#             Q(phone__icontains=query) |
#             Q(company_name__icontains=query) |
#             Q(city__icontains=query) |
#             Q(gst_number__icontains=query)
#         )

#     if status_filter in ('active', 'inactive'):
#         customers = customers.filter(status=status_filter)

#     total_count = customers.count()

#     paginator = Paginator(customers, 10)
#     page_obj = paginator.get_page(request.GET.get('page'))

#     profile = getattr(request.user, 'profile', None)

#     context = {
#         'page_obj': page_obj,
#         'query': query,
#         'status_filter': status_filter,
#         'total_count': total_count,
#         'is_admin': bool(profile and profile.is_admin),
#     }
#     return render(request, 'customers/customer_list.html', context)


# @login_required
# def customer_detail(request, pk):
#     customer = _get_owned_customer_or_none(request, pk)
#     if customer is None:
#         return HttpResponseForbidden("You do not have permission to view this customer.")
#     return render(request, 'customers/customer_detail.html', {'customer': customer})


# @login_required
# def customer_create(request):
#     if request.method == 'POST':
#         form = CustomerForm(request.POST)
#         if form.is_valid():
#             customer = form.save(commit=False)
#             customer.distributor = request.user
#             customer.save()
#             messages.success(request, f"Customer '{customer.name}' was added successfully.")
#             return redirect('customers:customer_list')
#     else:
#         form = CustomerForm()
#     return render(request, 'customers/customer_form.html', {'form': form, 'action': 'Add'})


# @login_required
# def customer_update(request, pk):
#     customer = _get_owned_customer_or_none(request, pk)
#     if customer is None:
#         return HttpResponseForbidden("You do not have permission to edit this customer.")

#     if request.method == 'POST':
#         form = CustomerForm(request.POST, instance=customer)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f"Customer '{customer.name}' was updated successfully.")
#             return redirect('customers:customer_list')
#     else:
#         form = CustomerForm(instance=customer)
#     return render(request, 'customers/customer_form.html', {
#         'form': form, 'action': 'Update', 'customer': customer,
#     })


# @login_required
# def customer_delete(request, pk):
#     customer = _get_owned_customer_or_none(request, pk)
#     if customer is None:
#         return HttpResponseForbidden("You do not have permission to delete this customer.")

#     if request.method == 'POST':
#         name = customer.name
#         customer.delete()
#         messages.success(request, f"Customer '{name}' was deleted.")
#         return redirect('customers:customer_list')

#     return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CustomerForm, DistributorRegisterForm
from .models import Customer


def register(request):
    """Self-service signup for new Distributor accounts."""
    if request.user.is_authenticated:
        return redirect('customers:customer_list')

    if request.method == 'POST':
        form = DistributorRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your distributor account is ready.")
            return redirect('customers:customer_list')
    else:
        form = DistributorRegisterForm()
    return render(request, 'customers/register.html', {'form': form})


def _base_queryset(user):
    """Superusers / Admins see all customers. Distributors only see their own."""
    if user.is_superuser or user.is_staff:
        return Customer.objects.select_related('distributor').all()
    
    profile = getattr(user, 'profile', None)
    if profile and profile.is_admin:
        return Customer.objects.select_related('distributor').all()
        
    return Customer.objects.filter(distributor=user)


def _get_owned_customer_or_none(request, pk):
    """Fetch a customer, enforcing that superusers or owners can touch records."""
    customer = get_object_or_404(Customer, pk=pk)
    
    # Superuser ya staff ko direct full access de do
    if request.user.is_superuser or request.user.is_staff:
        return customer

    profile = getattr(request.user, 'profile', None)
    if profile and profile.is_admin:
        return customer
        
    if customer.distributor_id == request.user.id:
        return customer
        
    return None


@login_required
def customer_list(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    customers = _base_queryset(request.user)

    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(company_name__icontains=query) |
            Q(city__icontains=query) |
            Q(gst_number__icontains=query)
        )

    if status_filter in ('active', 'inactive'):
        customers = customers.filter(status=status_filter)

    total_count = customers.count()

    paginator = Paginator(customers, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    profile = getattr(request.user, 'profile', None)
    is_admin_user = bool(request.user.is_superuser or request.user.is_staff or (profile and profile.is_admin))

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'total_count': total_count,
        'is_admin': is_admin_user,
    }
    return render(request, 'customers/customer_list.html', context)


@login_required
def customer_detail(request, pk):
    customer = _get_owned_customer_or_none(request, pk)
    if customer is None:
        return HttpResponseForbidden("You do not have permission to view this customer.")
    return render(request, 'customers/customer_detail.html', {'customer': customer})


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.distributor = request.user
            customer.save()
            messages.success(request, f"Customer '{customer.name}' was added successfully.")
            return redirect('customers:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': form, 'action': 'Add'})


@login_required
def customer_update(request, pk):
    customer = _get_owned_customer_or_none(request, pk)
    if customer is None:
        return HttpResponseForbidden("You do not have permission to edit this customer.")

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer '{customer.name}' was updated successfully.")
            return redirect('customers:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_form.html', {
        'form': form, 'action': 'Update', 'customer': customer,
    })


@login_required
def customer_delete(request, pk):
    customer = _get_owned_customer_or_none(request, pk)
    if customer is None:
        return HttpResponseForbidden("You do not have permission to delete this customer.")

    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f"Customer '{name}' was deleted.")
        return redirect('customers:customer_list')

    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})