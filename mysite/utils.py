
import random
import string
from django.utils import timezone

from django.utils.text import slugify

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def unique_key_generator(instance):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    size    = random.randint(30,45)
    key     = random_string_generator(size=size)
 
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return key

    
    qs      = EmailActivation.objects.filter(key__iexact=key)
    if qs.exists():
        key     = random_string_generator(size=size)
    instance.key = key


def unique_order_id_generator(instance):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    order_new_id = random_string_generator()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=order_new_id).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return order_new_id

def unique_ticket_id_generator(instance):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    ticket_new_id = random_string_generator()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(ticket_id=ticket_new_id).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return ticket_new_id


def unique_bidding_id_generator(instance, username):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    bidding_new_id = username + "_" + random_string_generator()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(bidding_id=bidding_new_id).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    print("bidding_new_id: ",bidding_new_id)
    return bidding_new_id


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        # slug = slugify(instance.title) #원래 instance.title 이었는데 바꿈.. 그러고 보니 product는 뭔가 겹치는느낌이라 바꿔줘야할듯.
        slug = instance.title #원래 instance.title 이었는데 바꿈.. 그러고 보니 product는 뭔가 겹치는느낌이라 바꿔줘야할듯.
        
    print(instance.title)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    print(slug)
    return slug



def check_ticket_activate(user, request, model):
    if user is not None:
        ticket_qs = model.objects.filter(user=user, status='activate')
        if ticket_qs.count() == 1:
            ticket_obj = ticket_qs.first()
            if ticket_obj.timestamp + timezone.timedelta(days=1) < timezone.now():
                ticket_obj.status = 'used'
                request.session['ticket_activate'] = False
                return True
            elif ticket_obj.timestamp + timezone.timedelta(days=1) >= timezone.now():
                request.session['ticket_activate'] = True
                return False
    return False