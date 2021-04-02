from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


from billing.models import BillingProfile
from .models import Order

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

    
def cancel_order(request):
    # print("캔슬 실행은 되는건가?")
    if request.method == 'POST':
        # print('POST는 드렁온건가?')
        order_id = request.POST.get('order_id', None)
        order_qs = Order.objects.filter(id=order_id)
        next_url = request.POST.get('next', '/')
        print(order_qs)
        if order_qs.count() == 1:
            order_obj = order_qs.first()
            if order_obj.status == 'paid':
                order_obj.status = 'cancel'
                order_obj.save()
                messages.success(request, '취소가 요청되었습니다. 담당자 확인 후 환불될 예정입니다.')
                return redirect(next_url)
            else:
                messages.success(request, '이미 출고가 되었습니다. 취소를 위해서는 상담을 요청해주세요.')
                return redirect(next_url)
    else:
        return redirect('orders:list')
