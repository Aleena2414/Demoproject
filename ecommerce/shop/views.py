from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from shop.models import Category,Product


def allcategories(request):
    c=Category.objects.all()
    context={'cat':c}
    return render(request,'category.html',context)
def allproducts(request,p):
    c=Category.objects.get(id=p)
    p=Product.objects.filter(category=c)
    context={'cat':c,'product':p}
    return render(request,'product.html',context)
def productdetails(request,p):
    p=Product.objects.get(id=p)
    return render(request,'details.html',{'details':p})

def register(request):
    if(request.method=='POST'):
        u=request.POST['u']
        p = request.POST['p']
        cp = request.POST['cp']
        f = request.POST['f']
        l = request.POST['l']
        e = request.POST['e']

        if(p==cp):
            u=User.objects.create_user(username=u,password=p,first_name=f,last_name=l,email=e)
            u.save()
        else:
            return HttpResponse('password is not same')
        return redirect('shop:categories')
    return render(request,'register.html')


def userlogin(request):
    if(request.method=='POST'):
        u = request.POST['u']
        p = request.POST['p']

        user=authenticate(username=u, password=p)
        if user:
            login(request,user)
            return redirect('shop:categories')
        else:
            messages.error(request,'invalid')

    return render(request,'login.html')



def userlogout(request):
    logout(request)
    return redirect('shop:login')

def add_categories(request):
    if (request.method == 'POST'):
        n = request.POST['n']
        d = request.POST['d']
        i = request.FILES['i']

        c=Category.objects.create(name=n,desc=d,image=i)  # create an new record
        c.save()
        return redirect('shop:categories')

    return render(request,'add_categories.html')
def add_products(request):

    if(request.method=='POST'):
        n = request.POST['n']
        d = request.POST['d']
        i = request.FILES.get('i')
        p = request.POST['p']
        s = request.POST['s']
        c=request.POST['c']
        cat=Category.objects.get(name=c)

        p=Product.objects.create(name=n,desc=d,image=i,price=p,stock=s,category=cat)
        p.save()
        return redirect('shop:categories')

    return render(request,'add_products.html')
def add_stock(request,p):
    product=Product.objects.get(id=p)
    if(request.method=="POST"):
        product.stock=request.POST['s']
        product.save()
        return redirect('shop:categories')

    context={'pro':product}

    return render(request,'addstock.html',context)
