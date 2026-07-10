from django.urls import path
try:
    import views
except ImportError:
    from . import views

urlpatterns = [
    # User Module
    path('users/register/', views.register_user, name='register_user'),
    path('users/login/', views.login_user, name='login_user'),
    path('users/', views.list_users, name='list_users'),
    path('users/update/<str:user_id>/', views.update_user, name='update_user'),
    path('users/delete/<str:user_id>/', views.delete_user, name='delete_user'),

    # Chat Module
    path('chats/send/', views.send_message, name='send_message'),
    path('chats/', views.list_chats, name='list_chats'),
    path('chats/update/<str:chat_id>/', views.update_message, name='update_message'),
    path('chats/delete/<str:chat_id>/', views.delete_message, name='delete_message'),

    # Conversation Module
    path('conversation/', views.list_conversations, name='list_conversations'),
    path('conversation/<str:username>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<str:sender>/<str:receiver>/', views.conversation_detail_two_users, name='conversation_detail_two_users'),
]

