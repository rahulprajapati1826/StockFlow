from django.views.decorators.cache import never_cache
from io import BytesIO
from django.db.models import Q
from django.db.models import Sum
from django.urls import reverse
from datetime import date as date_type 
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Store, Bills, Users
from .form import p_add_form, p_edit_form, register_user, login_user, reset_pass, make_inventory, make_report
from .decorators import custom_login_required

@never_cache
@custom_login_required
def product_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login-user')
    user = Users.objects.get(id=user_id)
    store_name = user.store_name
    all_p = Store.objects.filter(user_id=user_id, user=user)
    total_products = Store.objects.filter(user_id=user_id, user=user).count()
    total_bills = Bills.objects.filter(user_id=user_id, user=user).count()
    total_stock = Store.objects.filter(user_id=user_id, user=user).aggregate(total=Sum('p_quantity'))['total'] or 0
    return render (request, 'p_list.html', {'products':all_p ,'total_product':total_products, 'total_bills': total_bills,'total_stock': total_stock, 'store_name':store_name})

@never_cache
@custom_login_required
def add_product(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login-user')

    user = Users.objects.get(id=user_id)

    if request.method == 'POST':
        fm = p_add_form(request.POST)

        Product_ID = request.POST.get('Product_ID', '').strip()
        Product_Name = request.POST.get('Product_Name', '').strip()
        Product_Price = request.POST.get('Product_Price', '').strip()
        Product_quantity = request.POST.get('Product_quantity', '').strip()

        if fm.is_valid():

            if Store.objects.filter(p_id=Product_ID, user=user).exists():
                message = "Product already exists"
                return render(request, 'p_add.html', {
                    'fm': fm,
                    'message': message
                })

            Store.objects.create(
                p_id=Product_ID,
                p_name=Product_Name,
                p_price=Product_Price,
                p_quantity=Product_quantity,
                user=user
            )

            return redirect('product_list')

        return render(request, 'p_add.html', {'fm': fm})

    fm = p_add_form()
    return render(request, 'p_add.html', {'fm': fm})

@never_cache
@custom_login_required
def edit_product(request, pk):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login-user')

    user = Users.objects.get(id=user_id)

    product = get_object_or_404(
        Store,
        p_id=pk,
        user=user
    )

    if request.method == 'POST':

        Product_Name = request.POST.get('Product_Name', '').strip()
        Product_Price = request.POST.get('Product_Price', '').strip()
        Product_Quantity = request.POST.get('Product_Quantity', '').strip()

        if Product_Name:
            product.p_name = Product_Name

        if Product_Price:
            product.p_price = Product_Price

        if Product_Quantity != '':
            product.p_quantity = Product_Quantity

        product.save()

        return redirect('product_list')

    fm = p_edit_form()

    return render(
        request,
        'edit_product.html',
        {'form': fm, 'product': product}
    )

@never_cache
@custom_login_required
def delete_product(request, pk):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login-user')

    user = Users.objects.get(id=user_id)

    product = get_object_or_404(
        Store,
        p_id=pk,
        user=user
    )

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')

    return render(
        request,
        'conform_delete.html',
        {'product': product}
    )

@never_cache
def make_bill(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login-user')
    user = Users.objects.get(id=user_id)
    if request.method == 'POST':
        action = request.POST.get('action')

        c_name = request.POST.get('Customer_Name', '').strip()
        c_mobile = request.POST.get('Customer_Mobile', '').strip()
        p_id = request.POST.get('Product_ID', '').strip()
        quantity = request.POST.get('Quantity', '').strip()

        context = {
            'customer_name': c_name,
            'customer_mobile': c_mobile,
            'product_id': p_id,
            'quantity': quantity,
        }

        if action == 'fetch':

            if p_id:
                product = Store.objects.filter(p_id=p_id, user=user).first()
                context['product'] = product
                context['searched'] = True
                context['product_fetched'] = 'yes' if product else ''
            return render(request, 'bill.html', context)
        
        elif action == 'generate':
            product = Store.objects.filter(p_id=p_id, user=user).first()
            if not request.POST.get('product_fetched'):
                context['error'] = "Please fetch the product first!"
                return render(request, 'bill.html', context)
            if product.p_quantity == 0:
                message = "Can't generate bill because product stock is 0."
                return render(request, 'bill.html', {'message':message})

            bill_user = Bills.objects.create(customer_name=c_name, customer_mobile=c_mobile, purchase_product=p_id, quantity=quantity, user=user)
            available_stock = product.p_quantity - int(quantity)
            bill_date = bill_user.bill_date
            if available_stock >= 0:
                product.p_quantity = available_stock
                product.save()

            if not p_id or not quantity.isdigit() or int(quantity) <= 0:
                context['error'] = 'Enter valid Product ID and Quantity'
                return render(request, 'bill.html', context)

            if not product:
                context['error'] = 'Product not found!'
                return render(request, 'bill.html', context)

            quantity = int(quantity)
            total_amount = 0
            total = product.p_price * quantity
            total_amount += total

            bill_details = {
                'customer_name': c_name,
                'customer_mobile': c_mobile,
                'product': product,
                'quantity': quantity,
                'total': total,
                'date':bill_date
            }
            request.session['last_bill'] = {
                'customer_name': c_name,
                'customer_mobile': c_mobile,
                'product_id': product.p_id,
                'quantity': quantity,
                'bill_date': bill_date.strftime('%d-%m-%Y %I:%M %p'),
            }
    
            return render(request, 'print_bill.html', {
                'bill': bill_details
            })

    return render(request, 'bill.html')

@never_cache
def download_bill_pdf(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login-user')
    user = Users.objects.get(id=user_id)
    bill = request.session.get('last_bill')

    if not bill:
        return HttpResponse("Please generate a bill first.")

    product = get_object_or_404(
        Store,
        p_id=bill['product_id'], user=user
    )

    quantity = bill['quantity']
    total = product.p_price * quantity

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Title'],
        textColor=colors.HexColor('#4338ca'),
        fontSize=24,
        alignment=TA_RIGHT
    )

    elements = []

    heading = Table([
        [
            Paragraph("<b>StockFlow</b><br/>Inventory Management System", styles['Normal']),
            Paragraph("INVOICE", title_style)
        ]
    ], colWidths=[85*mm, 85*mm])

    heading.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))

    elements.append(heading)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>Customer Details</b>", styles['Heading2']))
    elements.append(Spacer(1, 8))

    customer_data = [
        ["Customer Name:", bill['customer_name']],
        ["Mobile:", bill['customer_mobile']],
        ['Date',bill['bill_date']]
    ]

    customer_table = Table(customer_data, colWidths=[40*mm, 130*mm])

    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    elements.append(customer_table)
    elements.append(Spacer(1, 25))

    elements.append(Paragraph("<b>Product Details</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    product_data = [
        ["Product ID", "Product Name", "Price", "Quantity", "Total"],
        [
            str(product.p_id),
            str(product.p_name),
            f"Rs. {product.p_price}",
            str(quantity),
            f"Rs. {total}"
        ]
    ]

    product_table = Table(
        product_data,
        colWidths=[25*mm, 48*mm, 30*mm, 25*mm, 42*mm]
    )

    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4338ca')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(product_table)
    elements.append(Spacer(1, 25))

    total_table = Table([
        ["Grand Total", f"Rs. {total}"]
    ], colWidths=[120*mm, 50*mm])

    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eef2ff')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#4338ca')),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))

    elements.append(total_table)
    elements.append(Spacer(1, 40))

    elements.append(
        Paragraph(
            "Thank you for Purchase!",
            styles['Heading2']
        )
    )

    elements.append(
        Paragraph(
            "This is a computer-generated invoice.",
            styles['Normal']
        )
    )

    pdf.build(elements)

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/pdf'
    )

    response['Content-Disposition'] = ('attachment; filename="StockFlow_Invoice.pdf"')

    return response

def user_registration(request):
    
    if request.method == 'POST':
        fm = register_user(request.POST)

        name = request.POST.get('Name', '').strip()
        mobile = request.POST.get('Mobile', '').strip()
        password = request.POST.get('Password', '')
        conform_password = request.POST.get('Conform_Password', '')

        user = Users.objects.filter(user_mobile=mobile).exists()
        if user:
            error = 'User already register. Please login'
            return render(request, 'register.html', {'fm':fm, 'error':error})
        if password != conform_password:
            error = "Password Dose't match!"
            return render(request, 'register.html', {'fm':fm, 'error':error})
        else:
            Users.objects.create(user_name=name, user_mobile=mobile, user_password=password)
            message = "Account created successfully. Login now"
            return render(request, 'register.html', {'fm':register_user(), 'message':message})
    else:
        fm = register_user()
        return render(request, 'register.html', {'fm':fm})

def user_login(request):
    if request.method == 'POST':
        form = login_user(request.POST)

        mobile = request.POST.get('Mobile', '').strip()
        password = request.POST.get('Password', '')

        user = Users.objects.filter(user_mobile=mobile).first()
        if not user:
            message = "Mobile number not register, please first register mobile number"
            return render(request, 'login_page.html', {'fm':form, 'error':message})
        
        user_password = user.user_password
        if user_password != password:
            error = "Password is incorrect!"
            return render(request, 'login_page.html', {'fm':form, 'error':error})
        request.session.cycle_key()
        request.session['user_id'] = user.id
        request.session['user_name'] = user.user_name
        return redirect('make_store')
    else:
        fm = login_user()
        return render(request, 'login_page.html', {'fm':fm})

def reset_password(request):
    fm = reset_pass()
    if request.method == 'POST':
        form = reset_pass(request.POST)
        mobile = request.POST.get('Mobile', '').strip()
        new_pass = request.POST.get('New_Password', '')
        user = Users.objects.filter(user_mobile=mobile).first()
        if not user:
            error = "User does not exists, please register."
            return render(request, 'reset_pass.html', {'fm':form, 'error':error})
        else:
            user.user_password = new_pass
            user.save()
            message = "Password reset successfully."
            return render(request, 'success_pass.html', {'message':message})
    else:
        return render(request, 'reset_pass.html', {'fm':fm})

@never_cache
@custom_login_required
def user_logout(request):
    request.session.flush()
    return redirect('login-user')

@never_cache
@custom_login_required
def make_store(request):

    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login-user')
    
    user = Users.objects.get(id=user_id)
    
    if user.store_name:
        return redirect('product_list')
    
    if request.method == 'POST':
        fm = make_inventory(request.POST)
        if fm.is_valid():
            store_name = fm.cleaned_data['Enter_Inventory_Name'].strip()
            if store_name:
                user.store_name = store_name
                user.save()
                return redirect('product_list')
    else:
        fm = make_inventory()

    return render(request, 'store_make.html', {'fm': fm})

@never_cache
@custom_login_required
def sales_report(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login-user')

    user = Users.objects.get(id=user_id)

    fm = make_report()
    report_generated = False
    data = []

    if request.method == 'POST':
        fm = make_report(request.POST)

        if fm.is_valid():
            date = fm.cleaned_data['date']
            print("Selected Date:", date)
            print("Date Type:", type(date))

            data = Bills.objects.filter(
                bill_date__date=date,
                user=user
            )

            report_generated = True

    return render(request, 'sales_report.html', {
        'fm': fm,
        'all_bills': data,
        'report_generated': report_generated,
        'selected_date': date if report_generated else None,
        'download_error': request.GET.get('download_error') 
    })

@never_cache
@custom_login_required
def download_sales_report(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login-user')

    user = Users.objects.get(id=user_id)

    selected_date = request.GET.get('date', '')

    try:
        selected_date = date_type.fromisoformat(selected_date)
    except (ValueError, TypeError):
        return redirect('sales_report')

    bills = Bills.objects.filter(
        bill_date__date=selected_date,
        user=user
    ).order_by('bill_date')

    if not bills.exists():
        return redirect(
            reverse('sales_report') + '?download_error=1'
        )

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        textColor=colors.HexColor('#4f46e5'),
        fontSize=20,
        alignment=1,
        spaceAfter=10
    )

    elements = []

    elements.append(
        Paragraph("StockFlow - Daily Sales Report", title_style)
    )

    elements.append(
        Paragraph(
            f"Report Date: {selected_date.strftime('%d-%m-%Y')}",
            styles['Normal']
        )
    )

    elements.append(Spacer(1, 20))

    table_data = [[
        'Bill ID',
        'Customer Name',
        'Mobile',
        'Product ID',
        'Qty',
        'Bill Date & Time'
    ]]

    for bill in bills:

        bill_time = bill.bill_date

        if timezone.is_aware(bill_time):
            bill_time = timezone.localtime(bill_time)

        table_data.append([
            str(bill.id),
            Paragraph(str(bill.customer_name), styles['BodyText']),
            str(bill.customer_mobile),
            str(bill.purchase_product),
            str(bill.quantity),
            bill_time.strftime('%d-%m-%Y %I:%M %p')
        ])

    # PDF table
    table = Table(
        table_data,
        colWidths=[
            0.55 * inch,
            1.15 * inch,
            1.05 * inch,
            0.85 * inch,
            0.45 * inch,
            1.65 * inch
        ],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LEADING', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor('#f1f5f9')
        ]),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    elements.append(table)

    # Total bills
    elements.append(Spacer(1, 18))

    elements.append(
        Paragraph(
            f"Total Bills: {bills.count()}",
            styles['Heading2']
        )
    )

    pdf.build(elements)

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="StockFlow_Report_{selected_date}.pdf"'
    )

    buffer.close()

    return response

def search_products(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login-user')

    user = Users.objects.get(id=user_id)

    query = request.GET.get('q', '').strip()

    products = Store.objects.filter(user=user)

    if query:
        products = products.filter(
            Q(p_id__icontains=query) |
            Q(p_name__icontains=query)
        )

    products = products.order_by('-p_id')

    return render(
        request,
        'product_search_results.html',
        {
            'products': products,
            'query': query,
            'has_inventory': Store.objects.filter(user=user).exists()
        }
    )

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)