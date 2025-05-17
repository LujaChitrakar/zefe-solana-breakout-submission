from django.urls import path
from user.views import (
    TelegramUserCreateView,
    UserProfileView,
    UserFeedbackView,
    TestAPIView,
    FieldListView,
    UserPositionsView,
    TelegramLoginView, TelegramMockLoginView, UserOnboardingView,
    WebUserProfileView,
    WebLoginWithTelegramView
    # WebTelegramLoginView
)

urlpatterns = [
    path("init/", TelegramUserCreateView.as_view(), name="telegramuser-create"),
    path("test/", TestAPIView.as_view(), name="testapi"),
    path("userprofile/", UserProfileView.as_view(), name="user-profile"),
    path("userfeedback/", UserFeedbackView.as_view(), name="user-feedback"),
    path('fields/', FieldListView.as_view(), name='field-list'),
    path('positions/', UserPositionsView.as_view(), name='user-positions'),
    #  path('web-telegram-login/', WebTelegramLoginView.as_view(), name='web-telegram-login'),
    path('telegram-login/', TelegramLoginView.as_view(), name='telegram-login'),
    path('telegram-mock-login/', TelegramMockLoginView.as_view(), name='telegram-mock-login'),
    path('auth/web/telegram-login/', WebLoginWithTelegramView.as_view(), name='web-telegram-login'),
    path('onboarding/', UserOnboardingView.as_view(), name='user-onboarding'),
    path('web/profile/', WebUserProfileView.as_view(), name='web-user-profile'), 
]
