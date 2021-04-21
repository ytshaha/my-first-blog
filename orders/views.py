from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings

from billing.models import BillingProfile, Charge
from .models import Order
from mysite.client import Iamport
from mysite.alimtalk import send


IAMPORT_CODE = getattr(settings, "IAMPORT_CODE", 'imp30832141')
IMPORT_REST_API_KEY = getattr(settings, "IMPORT_REST_API_KEY", '8306112827056798')
IMPORT_REST_API_SECRET = getattr(settings, "IMPORT_REST_API_SECRET", 'WmAHFCAyZFfaMy10g6xRPvFawuuJAVPxiqfY2Pw2uMcgkegAlOsak7kQCOzdKpK2PZ0RPxTjj6AEkQfF')


class OrderListView(LoginRequiredMixin, ListView):
    paginate_by = 5
    def get_queryset(self):
        return Order.objects.by_request(self.request).not_created()
        

class OrderDetailView(LoginRequiredMixin, DetailView):

    def get_object(self):
        # return Order.objects.get(id=self.kwargs.get('id'))
        # return Order.objects.get(slug=self.kwargs.get('slug'))
        qs = Order.objects.by_request(self.request).filter(order_id=self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404
    def get_context_data(self, *args, **kwargs):
        context = super(OrderDetailView, self).get_context_data(*args, **kwargs)
        tracking_number = self.object.tracking_number
        if tracking_number is not None: 
            tracking_number_list = tracking_number.split(",")
            tracking_number_list = [tn.strip() for tn in tracking_number_list]
            context['tracking_number_list'] = tracking_number_list
        return context


def cancel_request(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id', None)
        order_qs = Order.objects.filter(id=order_id)
        # next_url = request.POST.get('next', '/')
        context = {
            'order_id': order_id,
        }
        return render(request, 'orders/order_request.html', context)
    else:
        return redirect('orders:list')
def cancel_order(request): 
    # print("캔슬 실행은 되는건가?")
    if request.method == 'POST':
        # print('POST는 드렁온건가?')
        order_id = request.POST.get('order_id', None)
        cancel_reason = request.POST.get('cancel_reason', None)
        
        order_qs = Order.objects.filter(id=order_id)
        # next_url = request.POST.get('next', '/')
        print(order_qs)
        if order_qs.count() == 1:
            order_obj = order_qs.first()
            charge_obj = Charge.objects.get(order=order_obj)
            imp_uid = charge_obj.imp_uid
        
            if order_obj.status == 'paid':
                cancel_result = cancel_iamport(request, imp_uid=imp_uid, cancel_reason=cancel_reason)
                if cancel_result:
                    order_obj.status = 'cancel'
                    order_obj.cancel_reason = cancel_reason
                    order_obj.save()
                    messages.success(request, '주문이 취소되었습니다.')
                    print('{} 주문이 최소되었음.'.format(order_obj))
                    order_cancel_mail(email=order_obj.billing_profile.email, order=order_obj)
                    print('{}님에게 결제 취소 메일이 발송되었습니다.'.format(request.user))
                    
                    # cart_items_name 뽑아내기
                    user = request.user
                    cart_obj = order_obj.cart

                    # 결제시 필요한 name에 물건들을 넣어주자.
                    cart_items_name = "" # 실제 물품명
                    cart_items_name_iamport = "" # 아임포트용 물품명 -> 티켓내용 제외
                    item_count = cart_obj.cart_items.all().count()
                    for i, cart_item in enumerate(cart_obj.cart_items.all()):
                        if cart_item.product_type == 'ticket':
                            cart_items_name = cart_items_name + "ticket_" + str(cart_item.ticket_item.tickets_type)
                            if i < item_count-1:
                                cart_items_name = cart_items_name + ", "
                        else:
                            cart_items_name = cart_items_name + cart_item.product_item.product.title
                            cart_items_name_iamport = cart_items_name_iamport + cart_item.product_item.product.title
                            if i < item_count-1:
                                cart_items_name = cart_items_name + ", "
                                cart_items_name_iamport = cart_items_name_iamport + ", "
                        
                        if len(cart_items_name) > 200:
                            cart_items_name = cart_items_name[:200] + "..."
                    alimtalk_message = '''{user}님이 구매하신 상품의 결제가 취소되었습니다.

물품: {cart_items_name}
'''.format(user=user, cart_items_name=cart_items_name_iamport)
                    send(templateCode='alim5', to=user.phone_number, message=alimtalk_message)
                    print("{}으로 결제완료 알림톡이 보내졌습니다.".format(user.phone_number))
                else:
                    messages.success(request, '결제상에 문제가 있어 주문이 취소되지 않았습니다. 관리자에게 문의바랍니다.')
                    print('{} 주문이 결제상에 문제가 있어 주문이 취소되지 않았습니다. '.format(order_obj))

                return redirect('orders:list')
            elif order_obj.status == 'cancel':
                messages.success(request, '이미 취소되었습니다.')
                print('{} 주문이 이미 취소되었습니다. '.format(order_obj))
                return redirect('orders:list')
            else:
                messages.success(request, '이미 출고가 되었습니다. 취소를 위해서는 상담을 요청해주세요. 고객센터: 031-945-8832')
                print('{} 주문이 이미 출고가 되었습니다. 취소를 위해서는 상담을 요청해주세요.'.format(order_obj))
                return redirect('orders:list')
    else:
        return redirect('orders:list')



def cancel_iamport(request, imp_uid, cancel_reason):
    iamport = Iamport(imp_key=IMPORT_REST_API_KEY, imp_secret=IMPORT_REST_API_SECRET)
    user = request.user
    # 취소시 오류 예외처리(이미 취소된 결제는 에러가 발생함)
    try:    
        response = iamport.cancel(cancel_reason, imp_uid=imp_uid)
        print("취소 리스폰스", response)
        charge_obj = Charge.objects.get(imp_uid=imp_uid)
        charge_obj.status = 'cancel'
        charge_obj.cancelled = True
        charge_obj.refunded = True
        charge_obj.timestamp = response['cancelled_at']
        charge_obj.receipt_url = response['receipt_url']
        charge_obj.save()
        
        return True
    except Iamport.ResponseError as e:
        print(e.code)
        print(e.message)  # 에러난 이유를 알 수 있음
        return False
    except Iamport.HttpError as http_error:
        print(http_error.code)
        print(http_error.reason) # HTTP not 200 에러난 이유를 알 수 있음
        return False




from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import get_template


# 체크아웃완료되면 이메일 보내기.
def order_cancel_mail(email, order):
    base_url = getattr(settings, 'BASE_URL', 'https://moum8.com')
    key_path = reverse("home") # use reverse
    path = "{base}".format(base=base_url)
    
    
    context = {
        'path':path,
        'email': email,
        'order_id': order.order_id,
        'full_name': order.final_address.full_name,
        'phone_number': order.final_address.full_name,
        'address': order.final_address.get_address,
        'cart_items_name': order.cart_items_name,
        'total': order.total, # 물건값
        'shiping_cost': order.shipping_cost,
        'point_total': order.point_total,
        'checkout_total': order.checkout_total,
        'cancel_reason': order.cancel_reason,
        'shipping_count': order.shipping_count,

    }
    txt_ = get_template("orders/emails/order_cancel_email.txt").render(context)
    html_ = get_template("orders/emails/order_cancel_email.html").render(context)
    subject = '명품 병행수입 쇼핑몰_MOUM8_상품결제 취소 메일'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    # send_mail = send_email(
    #                         emailMsg=txt_, 
    #                         to=self.email, 
    #                         subject=subject)
    sent_mail = send_mail(
                subject,
                txt_,
                from_email,
                recipient_list,
                html_message=html_,
                fail_silently=False,
                )
    print("{}님께 결제취소 이메일이 보내졌습니다.".format(order.billing_profile.user))
    return send_mail