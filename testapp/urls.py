from django.urls import path

from testapp import views


urlpatterns = [
    path('strings/', views.strings),
    path('numbers/', views.numbers),
    path('letters/', views.letters),
    path('words/', views.words),
    path('short_strings/', views.short_strings),
    path('low_numbers/', views.low_numbers),
    path('lowercase_letters/', views.lowercase_letters),
]
