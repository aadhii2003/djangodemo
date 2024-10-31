
from django.contrib.auth.models import User

from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages

from shop.models import Category,Product


# Create your views here.
def allcategories(request):
    c=Category.objects.all()
    context={'cat':c}
    return render(request,'category.html',context)

def allproducts(request,p):
    c=Category.objects.get(id=p)
    p=Product.objects.filter(category=c)
    context={'cat':c,'products':p}
    return render(request,'product.html',context)

def productdetails(request,p):
    p=Product.objects.get(id=p)
    context={'products':p}
    return render(request,'view.html',context)



def user_login(request):
    if(request.method=="POST"):
        u=request.POST['u']
        p=request.POST['p']

        user=authenticate(username=u,password=p)
        if user:
            login(request,user)
            return redirect('shop:allcategories')
        else:
            messages.error(request, "invalid")

    return render(request,'login.html')

def register(request):
    if (request.method=="POST"):
        u=request.POST['u']
        p=request.POST['p']
        cp= request.POST['cp']
        f= request.POST['f']
        l= request.POST['l']
        e= request.POST['e']

        if(p==cp):
            u=User.objects.create_user(username=u,password=p,first_name=f,last_name=l,email=e)
            u.save()
        else:
            return HttpResponse("password is not same")
        return redirect('shop:login')

    return render(request,'register.html')
def user_logout(request):
    logout(request)
    return redirect('shop:login')

def addcategory(request):
    if(request.method=='POST'):
        n=request.POST['n']
        i=request.FILES['i']
        d=request.POST['d']

        c=Category.objects.create(name=n,image=i,desc=d)
        c.save()
        return redirect('shop:allcategories')
    return render(request,'addcategory.html')

def addproducts(request):
    if(request.method=='POST'):
        n=request.POST['n']
        d=request.POST['d']
        i=request.FILES['i']
        p=request.POST['p']
        s=request.POST['s']
        c=request.POST['c']

        cat=Category.objects.get(name=c)

        p=Product.objects.create(name=n,desc=d,image=i,price=p,stock=s,category=cat)
        p.save()
        return redirect('shop:allcategories')

    return render(request,'addproducts.html')

def addstock(request,p):
    p=Product.objects.get(id=p)
    if(request.method=='POST'):
        p.stock=request.POST['s']
        p.save()
        return redirect('shop:allcategories')
    context={'pro':p}
    return render(request,'addstock.html',context)
