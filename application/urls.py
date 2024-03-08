from .views import *
from django.urls import path

urlpatterns = [
    path('register/',Register.as_view()),
    path('login/',signin),
    path('updateprofile/',updateprofile),

    #For adding a post send a "POST" req with appropriate data and for retreiving list of posts of user "GET" request
    path('post/',Post.as_view()),

    path("like/",likepost),
    path('unlike/',unlike),

    path('connreq/',connectionrequest),
    path('handleconn/',handle_connection_request),

    path('recommendations/',Recommendations.as_view())
]