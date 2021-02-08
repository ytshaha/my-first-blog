from django.shortcuts import render

from .models import Cart

# Create your views here.
def cart_home(request):
    del request.session['cart_id']
    cart_id = request.session.get("cart_id", None)
    if cart_id is None: # and isinstance(cart_id, int):
        cart_obj = Cart.objects.create(user=None)
        request.session['cart_id'] = cart_obj.id
        print('New Cart created')
    else:
        print("Cart ID exists")
        print(cart_id)
        cart_obj = Cart.objects.get(id=cart_id)
    return render(request, "carts/home.html", {})