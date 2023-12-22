from django.urls import path

from testapp import views


urlpatterns = [
    path('strings/', views.strings),
    path('numbers/', views.numbers),
    path('letters/', views.letters),
    path('words/', views.words),
    path('short_strings/', views.short_strings),
    path('low_numbers/', views.low_numbers),
    path('lowercase_letters/', views.LowerCaseLetters.as_view()),
    path('lorem_words/', views.lorem_words),
    path('error/', views.error),
    path('with_cookie/', views.with_cookie),
    path('private_cache/', views.private_cache),
]
