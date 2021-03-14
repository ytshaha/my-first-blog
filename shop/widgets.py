from django.forms import DateTimeInput


class XDSoftDateTimePickerInput(DateTimeInput):
    template_name = 'shop/widgets/xdsoft_datetimepicker.html'