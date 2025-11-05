from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.contrib.auth.models import User
from .models import Customer, Purchase, ActivityLog, UserProfile
from .forms import CustomerForm, PurchaseForm, WalletReductionForm
from django.http import HttpResponse
from django.core.exceptions import ValidationError
import csv
from .auth import OperatorCreationForm

def normalize_phone(phone):
    if not phone:
        return ''
    # Persian and Arabic digits to English
    persian_digits = '۰۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸۹'  # Persian ۰-۹ and Arabic ٠-٩
    english_digits = '01234567890123456789'
    translation = str.maketrans(persian_digits, english_digits)
    return phone.translate(translation)

def is_admin(user):
    """Check if user is an admin"""
    try:
        return user.userprofile.user_type == 'admin'
    except:
        return False

@login_required
def dashboard(request):
    """Dashboard view for both operators and admins"""
    # Get statistics
    total_customers = Customer.objects.count()
    total_purchases = Purchase.objects.count()
    total_cashback = Purchase.objects.aggregate(Sum('cashback_amount'))['cashback_amount__sum'] or 0
    
    # Get recent activities
    recent_activities = ActivityLog.objects.all()[:10]
    
    context = {
        'total_customers': total_customers,
        'total_purchases': total_purchases,
        'total_cashback': total_cashback,
        'recent_activities': recent_activities,
    }
    
    # Log activity
    ActivityLog.objects.create(
        user=request.user,
        activity_type='user_login',
        description=f"کاربر {request.user.username} وارد داشبورد شد",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return render(request, 'dashboard.html', context)

# Customer Management Views
@login_required
def customer_list(request):
    """List all customers"""
    # Support sorting by wallet balance
    sort = request.GET.get('sort')
    direction = request.GET.get('dir', 'desc')

    customers_qs = Customer.objects.all()

    if sort == 'wallet':
        order_field = 'wallet_balance' if direction == 'asc' else '-wallet_balance'
        customers_qs = customers_qs.order_by(order_field)

    context = {
        'customers': customers_qs,
        'current_sort': sort or '',
        'current_dir': direction,
    }
    return render(request, 'customers/list.html', context)

@login_required
def customer_export_csv(request):
    """Export customers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'First Name', 'Last Name', 'National Code', 'Phone', 'Created At'])

    customers = Customer.objects.all().values_list('id', 'first_name', 'last_name', 'national_code', 'phone_number', 'created_at')

    for customer in customers:
        writer.writerow(customer)

    return response

@login_required
def customer_create(request):
    """Create a new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            # Save with defensive error handling in case model-level validation fails
            try:
                customer.save()
            except ValidationError as e:
                # Attach error to form so it renders nicely instead of a server error
                message = e.messages[0] if getattr(e, 'messages', None) else str(e)
                form.add_error('national_code', message)
                # Fall through to final render with form errors
            else:
                # Log activity
                ActivityLog.log_activity(
                    user=request.user,
                    activity_type='customer_create',
                    description=f"مشتری جدید ایجاد شد: {customer.first_name} {customer.last_name}",
                    customer=customer,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, "مشتری با موفقیت ثبت شد")
                return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    return render(request, 'customers/form.html', {'form': form, 'title': 'ثبت مشتری جدید'})

@login_required
def customer_edit(request, pk):
    """Edit an existing customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            
            # Log activity
            ActivityLog.log_activity(
                user=request.user,
                activity_type='customer_edit',
                description=f"اطلاعات مشتری ویرایش شد: {customer.first_name} {customer.last_name}",
                customer=customer,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, "اطلاعات مشتری با موفقیت بروزرسانی شد")
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customers/form.html', {'form': form, 'title': 'ویرایش اطلاعات مشتری'})

@login_required
def customer_detail(request, pk):
    """View customer details and purchase history"""
    customer = get_object_or_404(Customer, pk=pk)
    purchases = customer.purchases.all()
    
    return render(request, 'customers/detail.html', {
        'customer': customer,
        'purchases': purchases
    })

@login_required
def wallet_reduction(request, pk):
    """Reduce customer wallet balance"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = WalletReductionForm(request.POST, customer=customer)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            reason = form.cleaned_data['reason']
            
            # Reduce wallet balance
            customer.wallet_balance -= amount
            customer.save()
            
            # Log activity
            ActivityLog.log_activity(
                user=request.user,
                activity_type='wallet_reduction',
                description=f"کسر از کیف پول: {amount:,} ریال از کیف پول {customer.first_name} {customer.last_name} کسر شد. دلیل: {reason}",
                customer=customer,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"مبلغ {amount:,} ریال از کیف پول مشتری کسر شد")
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = WalletReductionForm(customer=customer)
    
    return render(request, 'customers/wallet_reduction.html', {
        'form': form,
        'customer': customer,
        'title': 'کسر از کیف پول'
    })

@login_required
def customer_search(request):
    """Search for a customer by national code, name, family, or phone"""
    national_code = request.GET.get('national_code', '')
    name = request.GET.get('name', '')
    last_name = request.GET.get('last_name', '')
    phone = request.GET.get('phone', '')
    
    if national_code:
        # Normalize Persian/Arabic digits and strip non-digit characters
        national_code_normalized = Customer.normalize_national_code(national_code)
        try:
            customer = Customer.objects.get(national_code=national_code_normalized)
            return redirect('customer_detail', pk=customer.pk)
        except Customer.DoesNotExist:
            messages.error(request, "مشتری با این کد ملی یافت نشد")
            customers = Customer.objects.none()
    else:
        queries = Q()
        if name:
            queries |= Q(first_name__icontains=name)
        if last_name:
            queries |= Q(last_name__icontains=last_name)
        if phone:
            phone_normalized = normalize_phone(phone)
            queries |= Q(phone_number__icontains=phone_normalized)
        
        if queries:
            customers = Customer.objects.filter(queries)
        else:
            customers = Customer.objects.none()
    
    return render(request, 'customers/search.html', {'customers': customers})

# Purchase Management Views
@login_required
def purchase_create(request, customer_id=None):
    """Create a new purchase for a customer"""
    customer = None
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
    
    if request.method == 'POST':
        data = request.POST.copy()
        if customer:
            data['customer'] = str(customer.id)
        form = PurchaseForm(data)
        if form.is_valid():
            purchase = form.save(commit=False)
            if customer:
                purchase.customer = customer
            purchase.created_by = request.user
            purchase.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type='purchase_create',
                description=f"خرید جدید ثبت شد برای مشتری: {purchase.customer.first_name} {purchase.customer.last_name} به مبلغ {int(purchase.amount):,} ریال",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"خرید با موفقیت ثبت شد. مبلغ {int(purchase.cashback_amount):,} ریال به کیف پول مشتری اضافه شد")
            return redirect('customer_detail', pk=purchase.customer.pk)
        # If invalid, the form with errors will be rendered below
    else:
        initial_data = {}
        if customer:
            initial_data = {'customer': customer}
        form = PurchaseForm(initial=initial_data)
    
    return render(request, 'purchases/form.html', {
        'form': form,
        'customer': customer,
        'title': 'ثبت خرید جدید'
    })

# Admin Views
@login_required
@user_passes_test(is_admin)
def operator_list(request):
    """List all operators (admin only)"""
    operators = UserProfile.objects.filter(user_type='operator')
    return render(request, 'admin/operator_list.html', {'operators': operators})

@login_required
@user_passes_test(is_admin)
def operator_create(request):
    """Create a new operator (admin only)"""
    if request.method == 'POST':
        form = OperatorCreationForm(request.POST)
        if form.is_valid():
            operator = form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type='operator_create',
                description=f"اپراتور جدید ایجاد شد: {operator.username}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, "اپراتور جدید با موفقیت ایجاد شد")
            return redirect('operator_list')
    else:
        form = OperatorCreationForm()
    
    return render(request, 'admin/operator_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def activity_logs(request):
    """View all activity logs (admin only)"""
    logs = ActivityLog.objects.all()
    return render(request, 'admin/activity_logs.html', {'logs': logs})

@login_required
def reports(request):
    """View system reports (for operators and admins)"""
    # Get statistics
    total_customers = Customer.objects.count()
    total_purchases = Purchase.objects.count()
    total_cashback = Purchase.objects.aggregate(Sum('cashback_amount'))['cashback_amount__sum'] or 0
    
    # Calculate average cashback
    average_cashback = total_cashback / total_purchases if total_purchases > 0 else 0
    
    # Get top customers by purchase amount
    top_customers = Customer.objects.annotate(
        total_purchase=Sum('purchases__amount')
    ).order_by('-total_purchase')[:10]
    
    context = {
        'total_customers': total_customers,
        'total_purchases': total_purchases,
        'total_cashback': total_cashback,
        'average_cashback': average_cashback,
        'top_customers': top_customers,
    }
    
    return render(request, 'admin/reports.html', context)

@login_required
def report_export_csv(request):
    """Export reports data to CSV"""
    # Get statistics
    total_customers = Customer.objects.count()
    total_purchases = Purchase.objects.count()
    total_cashback = Purchase.objects.aggregate(Sum('cashback_amount'))['cashback_amount__sum'] or 0
    average_cashback = total_cashback / total_purchases if total_purchases > 0 else 0
    
    # Get top customers by purchase amount
    top_customers = Customer.objects.annotate(
        total_purchase=Sum('purchases__amount')
    ).order_by('-total_purchase')[:10]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'

    writer = csv.writer(response)
    
    # Write statistics
    writer.writerow(['گزارشات کلی'])
    writer.writerow(['تعداد کل مشتریان', total_customers])
    writer.writerow(['تعداد کل خریدها', total_purchases])
    writer.writerow(['مجموع کشبک', total_cashback])
    writer.writerow(['میانگین کشبک', f'{average_cashback:.2f}'])
    writer.writerow([])  # Empty row
    
    # Write top customers
    writer.writerow(['10 مشتری برتر بر اساس مبلغ خرید'])
    writer.writerow(['نام مشتری', 'مبلغ کل خرید'])
    for customer in top_customers:
        name = f"{customer.first_name} {customer.last_name}"
        total = customer.total_purchase or 0
        writer.writerow([name, total])

    return response
