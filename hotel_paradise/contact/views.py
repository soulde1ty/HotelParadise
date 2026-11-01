from django.contrib import messages
from django.utils.translation import gettext as _
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from .forms import ContactForm


@require_http_methods(['GET', 'POST'])
def contact(request):
    form = ContactForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Thank you! Your message has been received.'))
        return redirect('contact')
    return render(request, 'contact_main.html', {'form': form})
