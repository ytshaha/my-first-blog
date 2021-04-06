from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings

from billing.models import BillingProfile, Charge
from .models import Order
from mysite.client import Iamport

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
                    order_obj.save()
                    messages.success(request, '주문이 취소되었습니다.')
                    print('{} 주문이 최소되었음.'.format(order_obj))
                    
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

    # 취소시 오류 예외처리(이미 취소된 결제는 에러가 발생함)
    try:    
        response = iamport.cancel(cancel_reason, imp_uid=imp_uid)
        print("취소 리스폰스", response)
        charge_obj = Charge.objects.get(order=order_obj)
        charge_obj.status = 'cancel'
        charge_obj.cancelled = True
        charge_obj.refunded = True
        charge_obj.timestamp = response['cancelled_at']
        charge_obj.receipt_url = response['receipt_url']
        charge_obj.save()
        charge_obj
        return True
    except Iamport.ResponseError as e:
        print(e.code)
        print(e.message)  # 에러난 이유를 알 수 있음
        return False
    except Iamport.HttpError as http_error:
        print(http_error.code)
        print(http_error.reason) # HTTP not 200 에러난 이유를 알 수 있음
        return False