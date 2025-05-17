
from django.urls import path
from events import views

urlpatterns = [
    path('event/', views.EventJoinOrCreateView.as_view(), name='events-create'),
    path('admin_event/', views.AdminUserEventListView.as_view(), name='admin-events'),
    path('create-a-network/', views.UserNetworkCreateView.as_view(), name='network-create'),
    path('networks_and_connnections/', views.UserNetworkConnectionView.as_view(), name='my-network'),
    path('networks_and_connnections/<int:connected_network_user_id>/', views.ConnectedNetworkUserDetailedView.as_view(), name='my-network-details'),
    path('get-network-information/<int:network_id>/', views.MeetingInformationDetailView.as_view(), name='network-info'),
    path('save-network-information/', views.MeetingInformationCreateView.as_view(), name='save-network-information'),
    path('wallet/connect/', views.WalletConnectionView.as_view(), name='wallet-connect'),
    path('networking/send-request/', views.SendNetworkingRequestView.as_view(), name='send-networking-request'),
    path('networking/received-requests/', views.ReceivedNetworkingRequestsView.as_view(), name='received-networking-requests'),
    path('networking/respond/<int:request_id>/', views.RespondToNetworkingRequestView.as_view(), name='respond-to-networking-request'),
    path('transaction/status/<str:transaction_id>/', views.TransactionStatusView.as_view(), name='transaction-status'),
    path('transaction/mock/', views.MockTransactionView.as_view(), name='mock-transaction'),
    path('networking/health-check/', views.NetworkingHealthCheckView.as_view(), name='networking-health-check'),
    path('wallet/debug/', views.WalletDebugView.as_view(), name='wallet-debug'),
    path('networking/sent-requests/', views.SentNetworkingRequestsView.as_view(), name='sent-networking-requests'),
    path('users/browse/', views.BrowseUsersView.as_view(), name='browse-users'),
    path('networking/spam-reports/', views.SpamReportsView.as_view(), name='spam-reports'),
    path('users/filter/', views.FilterUsersView.as_view(), name='filter-users'),
    path('event/join/<str:code>/', views.JoinEventByCodeView.as_view(), name='join-event-by-code'),
    path('attendees/', views.AttendeesListView.as_view(), name='attendees-list'),
    path('networking/debug/', views.NetworkingRequestDebugView.as_view(), name='networking-debug'),
    path('networking/connections/', views.MyConnectionsView.as_view(), name='my-connections'),
    path('notifications/count/', views.NotificationCountView.as_view(), name='notification-count'),
    path('networking/connections/<int:connection_id>/remove/', views.RemoveConnectionView.as_view(), name='remove-connection'),
]   