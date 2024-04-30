from django.urls import path, include
from . import views

urlpatterns = [
    path("create_chat/", views.CreateChat.as_view(), name="index"),
    path("create_character/", views.CreateCharacter.as_view(), name="index"),
    path("create_world/", views.CreateWorld.as_view(), name="index"),
    path("update_character/", views.UpdateCharacter.as_view(), name="index"),
    path("update_world/", views.UpdateWorld.as_view(), name="index"),
    path("update_chat/", views.UpdateChat.as_view(), name="index"),
    path("get_characters/", views.GetCharacters.as_view(), name="index"),
    path("get_worlds/", views.GetWorlds.as_view(), name="index"),
    path("get_chats/", views.GetChats.as_view(), name="index"),
    path("delete_message/", views.DeleteMessage.as_view(), name="index"),
    path("get_character/", views.GetCharacter.as_view(), name="index"),
    path("get_chat/", views.GetChat.as_view(), name="index"),
    path("delete_chat/", views.DeleteChat.as_view(), name="index"),
    path("update_chat_nsfw/", views.UpdateChatNSFW.as_view(), name="index"),
    path("delete_character/", views.DeleteCharacter.as_view(), name="index"),
    path("delete_world/", views.DeleteWorld.as_view(), name="index"),
    path("checkout/", views.GetCheckout.as_view(), name="index"),
    path("get_customer_portal/", views.GetCustomerPortal.as_view(), name="index"),
    path("webhook/", views.StripeWebhooks.as_view(), name="index"),
    path("get_subscription/", views.GetSubscription.as_view(), name="index"),
    path("get_subscription_is_active/", views.GetSubscriptionIsActive.as_view(), name="index"),
    path("cancel_subscription/", views.CancelSubscription.as_view(), name="index"),
]





