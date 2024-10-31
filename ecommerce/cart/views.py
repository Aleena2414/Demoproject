from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from cart.models import Cart
from django.views.decorators.csrf import csrf_exempt
from shop.models import Product
import razorpay

from cart.models import payment,Order_details


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

@login_required
def cart_remove(request,i):
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

def cart_view(request):
    u=request.user
    total=0
    c=Cart.objects.filter(user=u)
    for i in c:
        total+=i.quantity*i.product.price #calculate the sum of each product price*quantity
    context={'cart':c,'total':total}
    return render(request,'cart.html',context)
@login_required
def cart_delete(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    c=Cart.objects.get(user=u,product=p)
    c.delete()
    p.stock+=c.quantity
    p.save()
    return redirect('cart:cartview')
@login_required
def order_now(request):
    if(request.method=='POST'):
        address=request.POST['a']
        phone_no = request.POST['p']
        pincode = request.POST['pi']
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.quantity*i.product.price

        total=int(total*100)

        client=razorpay.Client(auth=('rzp_test_WS1fHiXBO06rof','TcRrUCd33JMDL29usyjNxgc0'))#create a client conncetion using razorpay id and sceret


        response_payment=client.order.create(dict(amount=total,currency='INR'))#create an order with razorpay with razorpay client
        print(response_payment)

        order_id = response_payment['id']#retrive the order_id from response
        order_status=response_payment['status']#retrive status from response
        if(order_status=='created'): # if status is created then store order_id in payment and order_details table
            p=payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c: #for each item create a record inside Order_details table
                o=Order_details.objects.create(product=i.product,user=u,no_of_items=i.quantity,address=address,phone_no=phone_no,pincode=pincode,order_id=order_id)
                o.save()
            else:
                pass
        response_payment['name']=u.username #additional information name
        context={'payment':response_payment}

        return render(request,'payment.html',context)
    return render(request,'ordernow.html')

@csrf_exempt
def payment_status(request,u):
    if(request.method=='POST'):
        response=request.POST
        print(response)
        user=User.objects.get(username=u)
        if(not request.user.is_authenticated):#if user is not authenticated
            login(request,user)#allowing request user to login

        param_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id':response['razorpay_payment_id'],
            'razorpay_signature':response['razorpay_signature']
        }
        client=razorpay.Client(auth=('rzp_test_WS1fHiXBO06rof','TcRrUCd33JMDL29usyjNxgc0'))#to create razorpay client
        print(client)
        try:
            status=client.utility.verify_payment_signature(param_dict)#to check the authenticity of the razorpay signature
            print(status)
            #to retrive a particluar record in payment Table whose order id matches the response order id
            p=payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id=response['razorpay_payment_id']
            p.paid=True
            p.save()


            o=Order_details.objects.filter(user=user,order_id=response['razorpay_order_id'])#retrive the rocorde in order_details
            #matching with current user and response order_id
            for i in o:
                i.payment_status='paid'
                i.save()
            #after successfull payment delete the items in cart for a particular user
            c=Cart.objects.filter(user=user)
            c.delete()


        except:
            pass
    return render(request,'payment_status.html',{'status':status})
@login_required
def order_view(request):
    u=request.user
    o=Order_details.objects.filter(user=u,payment_status='paid')
    context={'order_view':o}
    return render(request,'order_view.html',context)




