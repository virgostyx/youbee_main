from django.urls import path, re_path

from .views import RegisterView, SigninView, SignoutView, MyPasswordResetView, MyPasswordResetDoneView, \
    MyPasswordResetFromKeyView,MyPasswordResetFromKeyDoneView, MyPasswordChangeView, UserDetailView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', SigninView.as_view(), name='signin'),
    path('logout/', SignoutView.as_view(), name='signout'),
    path('password/change/', MyPasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', MyPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', MyPasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", MyPasswordResetFromKeyView.as_view(),
            name="reset_password_from_key", ),
    path("password/reset/key/done/", MyPasswordResetFromKeyDoneView.as_view(), name="reset_password_from_key_done", ),
    path('user/detail/', UserDetailView.as_view(), name='user_detail'),
    ]
