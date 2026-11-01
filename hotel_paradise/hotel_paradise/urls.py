"""
URL configuration for hotel_paradise project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from main.views import home
from about.views import about
from service.views import service
from room.views import room, room_detail
from django.conf import settings
from django.conf.urls.static import static
from booking.views import booking
from team.views import team
from testimonial.views import testimonial
from contact.views import contact

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('about/', about, name="about"),
    path('service/', service, name="service"),
    path('room/', room, name="room"),
    path('room/<int:room_id>/', room_detail, name='room_detail'),
    path('booking/', booking, name='booking_general'),
    path('booking/<int:room_id>/', booking, name="booking"),
    path('team/', team, name="team"),
    path('testimonial/', testimonial, name="testimonial"),
    path('contact/', contact, name="contact"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = _('Hotel Paradise administration')
admin.site.site_title = _('Hotel Paradise administration')
admin.site.index_title = _('Hotel management')
