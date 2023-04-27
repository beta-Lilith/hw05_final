# Импортируем из приложения django.contrib.auth нужный view-классы
from django.contrib.auth.views import (
    LogoutView,
    LoginView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView
)
from django.urls import path
from . import views
app_name = 'users'

urlpatterns = [
    # Полный адрес страницы регистрации - auth/signup/,
    # но префикс auth/ обрабатывется в головном urls.py
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        # Прямо в описании обработчика укажем шаблон,
        # который должен применяться для отображения возвращаемой страницы.
        # Да, во view-классах так можно!
        LogoutView.as_view(
            template_name='users/logged_out.html'
        ),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(
            template_name='users/login.html'
        ),
        name='login'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset'
    ),
]
