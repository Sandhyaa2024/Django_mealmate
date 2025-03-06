from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Customer,Restaurants,Menu, Cart
from delivery.forms import ResForm, MenuForm
import razorpay
from django.conf import settings

# Create your views here.
def sign_in(request):
    return render(request, 'delivery/sign_in.html')


def sign_up(request):
    return render(request,'delivery/sign_up.html')


def index(request):
    return render(request,'delivery/index.html')


def handle_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        try:
            cus = Customer.objects.get(username=username, password=password)
        except:
            cus = Customer(username=username,password=password,email=email,mobile=mobile,address=address)
            cus.save()
        return render(request,'delivery/sign_in.html')
    else:
        return HttpResponse("Invalid data")
    
  
def handle_signin(request):
    li = Restaurants.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            cus = Customer.objects.get(username=username, password=password)
            if username == 'admin':
                return render(request, 'delivery/success.html')
            else:
                return render(request, 'delivery/cusdisplay_res.html',{'username':username,'li':li})
        except:
            return render(request,'delivery/failed.html')


def add_res(request):
    form = ResForm(request.POST or None)
    if form.is_valid():
        res_name = request.POST.get('resname')
        try:
            res = Restaurants.objects.get(resname = res_name)
        except:
            form.save()
            return redirect('delivery:display_res')
    return render(request,'delivery/add_res.html',{'form': form})


def display_res(request):
    li = Restaurants.objects.all()
    return render(request,'delivery/display_res.html',{'li':li})


def view_menu(request, id):
    res = Restaurants.objects.get(pk = id)
    menu = Menu.objects.filter(res = res)
    return render(request, 'delivery/menu.html', {'res': res, 'menu':menu})


def add_menu(request, id):
    form = MenuForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('delivery:view_menu', id)
    return render(request, 'delivery/menu_form.html',{'form': form})


def delete_menu(requset, id):
    menu = Menu.objects.get(pk = id)
    res_id = menu.res.id
    menu.delete()
    return redirect('delivery:view_menu',res_id)


def cusdisplay_res(request, username):
    customer = Customer.objects.get(username=username)
    li = Restaurants.objects.all()
    return render(request,'delivery/cusdisplay_res.html',{'li':li, 'username':username})


def cusmenu(request,id,username):
    
    res = Restaurants.objects.get(pk = id)
    menu = Menu.objects.filter(res = res)
    return render(request, 'delivery/cusmenu.html', {'res': res, 'menu':menu, 'username':username})


def delete_res(requser,id):
    cus = Restaurants.objects.get(pk = id)
    cus.delete()
    return redirect('delivery:display_res')


def update_res(request, id):
    res = Restaurants.objects.get(pk = id)
    form = ResForm(request.POST or None, instance = res)
    if form.is_valid():
        form.save()
        return redirect('delivery:display_res')
    return render(request, 'delivery/add_res.html',{'form': form})


def show_cart(request, username):
    customer = Customer.objects.get(username=username)
    cart = Cart.objects.filter(customer = customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0
    return render(request, 'delivery/show_cart.html',{'items':items, 'total_price':total_price ,'username':username})


def add_to_cart(request, menuid, username):
    item = Menu.objects.get(pk = menuid)
    customer = Customer.objects.get(username=username)
    cart, created = Cart.objects.get_or_create(customer= customer)
    cart.items.add(item)
    messages.success(request,f"{item.item_name} added")
    return redirect('delivery:cusmenu', id = item.res.id, username=username)


def checkout(request, username):
    customer = Customer.objects.get(username = username)
    cart = Cart.objects.filter(customer = customer).first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    if total_price == 0:
        return render(request, 'delivery/checkout.html',{'error':'Your cart is Empty'})

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    order_data = {
        'amount':int(total_price * 100),
        'currency':'INR',
        'payment_capture':'1',
    }
    order = client.order.create(data = order_data)
    return render(
        request, 'delivery/checkout.html',
        {'username':username,
        'cart_items':cart_items,
        'total_price':total_price,
        'razorpay_key_id':settings.RAZORPAY_KEY_ID,
        'order_id':order['id'],
        'amount':total_price,
        }
    )


def orders(request, username):
        customer = Customer.objects.get(username = username)
        cart = Cart.objects.filter(customer=customer).first()
        cart_items = cart.items.all() if cart else []
        total_price = cart.total_price() if cart else 0

        if cart:
            cart.items.clear()

        return render(request, 'delivery/orders.html',{
        'username':username,
        'cart_items':cart_items,
        'total_price':total_price,
        'customer':customer
        })
