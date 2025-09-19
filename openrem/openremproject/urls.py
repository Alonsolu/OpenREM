from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from remapp import views

admin.autodiscover()

urlpatterns = [
    re_path(r'^openrem/', include('remapp.urls')),
    re_path(r'^admin/', admin.site.urls),
    # Login / logout.
    re_path(r'^login/$', auth_views.LoginView.as_view()),
    re_path(r'^logout/$', views.logout_page),
]
