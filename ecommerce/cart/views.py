from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from cart.models import Cart,Payment,Orderdetails
from shop.models import Product
from django.contrib.auth import login
import razorpay


# Create your views here.

@login_required
def cart(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)
        if(p.stock>0):
            c.quantity+=1
            c.save()
            p.stock-=1
            p.save()
    except:
        if(p.stock>0):
            c=Cart.objects.create(product=p,user=u,quantity=1)
            c.save()
            p.stock-=1
            p.save()



    return redirect('cart:cartview')

def cart_view(request):
    u=request.user
    total=0
    c=Cart.objects.filter(user=u)
    for i in c:
        total+=i.quantity * i.product.price

    context={'cart':c,'total':total}
    return render(request,'cart.html',context)

@login_required()
def cartremove(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)
        if(c.quantity>1):
            c.quantity-=1
            c.save()
            p.stock+=1
            p.save()

        else:
            c.delete()
            p.stock += 1
            p.save()

    except:
        pass
    return redirect('cart:cartview')
@login_required
def delete(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)
        c.delete()
        p.stock+=c.quantity
        p.save()
    except:
        pass

    return redirect('cart:cartview')

def ordernow(request):
    if(request.method=="POST"):
        address=request.POST['a']
        phone=request.POST['p']
        pin=request.POST['pi']

        u=request.user

        c=Cart.objects.filter(user=u)
        total=0

        for i in c:
            total+=i.quantity*i.product.price
        total=int(total*100)

        client=razorpay.Client(auth=('rzp_test_nZILgn6mW25IBc','XdkWr2fczip4WIGCRlAbvhvK')) #create a client connection using razorpay id and secret

        response_payment=client.order.create(dict(amount=total,currency="INR"))#create an order with razorpay with rauzorpay client
        # print(response_payment)
        order_id=response_payment['id'] #retrive the order_id from response
        order_status=response_payment['status']#retrive status from response
        if(order_status=="created"): #if status is created then store order_id in payment and order_deatils table
            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c: #for each items creates a record inside orderdeatisl table
                o=Orderdetails.objects.create(product=i.product,user=u,noofitems=i.quantity,address=address,phoneno=phone,pin=pin,order_id=order_id)
                o.save()
            else:
                pass
        response_payment['name']=u.username
        context={'payment':response_payment}

        return render(request,'payment.html',context)
    return render(request,'ordernow.html')

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def payment_status(request,u):
    user=User.objects.get(username=u)
    if(not request.user.is_authenticated): #if user is not authenticated this code for after payment automatic logouted
        login(request,user) #allowing request user to login
    if(request.method=="POST"):
        response=request.POST
        print(response)

        param_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id':response['razorpay_payment_id'],
            'razorpay_signature':response['razorpay_signature']
        }
        client = razorpay.Client(auth=('rzp_test_nZILgn6mW25IBc', 'XdkWr2fczip4WIGCRlAbvhvK')) #to create razorpay client
        print(client)
        try:
            status=client.utility.verify_payment_signature(param_dict) #to check the authenticity of the razorpay signature
            print(status)
           #to retrive a particular record in payment Table whose order id matches the response order id
            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            print(p)
            p.razorpay_payment_id=response['razorpay_payment_id'] #add the payment id after succesful payment
            p.paid=True # to change the paid status to True
            p.save()

            user=User.objects.get(username=u)
            o=Orderdetails.objects.filter(user=user,order_id=response['razorpay_order_id']) #retrive the record in order_details
            #matching with current user and response order_id
            for i in o:
                i.payment_status="paid"
                i.save()

            #after succesful payment deletes the item in cart for a particular useer
            c=Cart.objects.filter(user=user)
            c.delete()


        except:
            pass


    return render(request,'payment_status.html',{'status':status})

@login_required
def order_view(request):
    user=request.user
    o=Orderdetails.objects.filter(user=user,payment_status="paid")
    context={'orderview':o}
    return render(request,'orderview.html',context)

