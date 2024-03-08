from .models import *
from .serializers import *
from django.http import JsonResponse
from django.contrib.auth import authenticate
from knox.models import AuthToken
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from knox.auth import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.db.models import Q


class Register(APIView):
    permission_classes = [AllowAny]
    @csrf_exempt
    def post(self,request):
        user_data = UserProfileSerializer(data=request.data)
        if user_data.is_valid():
            user_data.save()
            return JsonResponse({'success':True},status=200)
        else:
            return JsonResponse({'success':False,'error':user_data.errors},status=400)


@csrf_exempt
def signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_token = AuthToken.objects.create(user)[1]
            return JsonResponse({'success': True, 'auth_token': auth_token}, status=200)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid Credentials'},status=400)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateprofile(request):
    try:
        user_profile = UserProfile.objects.get(userId=str(request.user))
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    user_data = UserProfileSerializer(user_profile,data=request.data)
    if user_data.is_valid():
        user_data.save()
        return JsonResponse({'success':True},status=200)
    else:
        return JsonResponse({'success':False,'error':user_data.errors},status=400)


class Post(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    def post(self,request):
        post_data=request.data
        post_data['userId']=str(request.user)
        post_serializer=PostsSerializer(data=post_data)
        if post_serializer.is_valid():
            post_serializer.save()
            return JsonResponse({'success':True},status=200)
        else:
            return JsonResponse({'success': False, 'error': post_serializer.errors}, status=400)

    def get(self, request):
        try:
            posts_data = Posts.objects.filter(userId=str(request.user))
            serializer = PostsSerializer(posts_data, many=True)
            return JsonResponse({'posts': serializer.data}, status=200)
        except Posts.DoesNotExist:
            return JsonResponse({'posts': []}, status=200)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def likepost(request):
    try:
        liked_obj=Likes.objects.get(userId=str(request.user))
    except Likes.DoesNotExist:
        post_id=request.POST["post_id"]
        like_post_serializer=LikeSerializer(data={'postId':post_id,'userId':str(request.user)})
        if like_post_serializer.is_valid():
            like_post_serializer.save()
            return JsonResponse({'success':True},status=200)
        else:
            return JsonResponse({'success':False,'error':like_post_serializer.errors},status=400)
    return JsonResponse({'success':True},status=200)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def unlike(request):   
    try:
        liked_obj=Likes.objects.get(userId=str(request.user),postId=request.POST['post_id'])
        liked_obj.delete()
        return JsonResponse({'success':True},status=200)
    except Likes.DoesNotExist:
        return JsonResponse({'success':True},status=200)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def connectionrequest(request):
    destination_username=request.POST['username']
    print(destination_username)
    try:
        destination_id=UserProfile.objects.get(username=destination_username).userId
    except UserProfile.DoesNotExist:
        return JsonResponse({'success':False,'error':'User with given username Does not exist!'},status=400)
    try:
        req_data=ConnectionRequest.objects.get(source=str(request.user),destination=destination_id)
    except ConnectionRequest.DoesNotExist:
        try:
            conn_exits=Connections.objects.get(user2=str(request.user),user1=str(destination_id))
        except Connections.DoesNotExist:
            try:
                rev_conn=Connections.objects.get(user1=str(request.user),user2=str(destination_id))
            except Connections.DoesNotExist:
                conn_req={'source':str(request.user),'destination':destination_id}
                conn_req_serializer=ConnectionRequestSerializer(data=conn_req)
                if conn_req_serializer.is_valid():
                    conn_req_serializer.save()
                    return JsonResponse({'success':True},status=200)
                else:
                    return JsonResponse({'success':False,'error':conn_req_serializer.errors},status=400)
            return JsonResponse({'success':True},status=200)
    return JsonResponse({'success':True},status=200)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_connection_request(request):
    request_id = request.POST['request_id']
    choice = request.POST['choice']  
    # Here choice represents whether user accepts or rejects the request so it would be either 0 or 1
    try:
        request_data=ConnectionRequest.objects.get(reqId=request_id)
        print(choice)
        if choice == "1":
            if str(request_data.destination)==str(request.user):
                conn_data={'user2':str(request_data.source),'user1':str(request.user)}
                conn_serializer=ConnectionSerializer(data=conn_data)
                if conn_serializer.is_valid():
                    conn_serializer.save()
                    request_data.delete()
                    return JsonResponse({'success':True},status=200)
                else:
                    return JsonResponse({'success':False,'error':conn_serializer.errors},status=400)     
            else:
                return JsonResponse({'success':False,'error':'Authentication Failed'},status=400)
        else:
            request_data.delete()
            return JsonResponse({'success':True},status=200)
    except ConnectionRequest.DoesNotExist:
        return JsonResponse({'success':False,'error':'Request Does Not Exist'},status=400)


class Recommendations(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    def get(self,request):
        connections = Connections.objects.filter(
            Q(user1=str(request.user)) | Q(user2=str(request.user))
        )

        user_connections = set()
        for connection in connections:
            user_connections.add(str(connection.user2) 
            if str(connection.user1) == str(request.user) 
            else str(connection.user1)
            )
        
        recommendation=set()
        for connection in user_connections:
            followers_connection = Connections.objects.filter(
                Q(user1=str(connection)) | Q(user2=str(connection))
            )

            followers_of_connection=set()
            for follower_of_connection in followers_connection:
                followers_of_connection.add(str(follower_of_connection.user2) 
                if str(follower_of_connection.user1) == str(connection) 
                else str(follower_of_connection.user1)
                )
            
            required_connections=followers_of_connection - user_connections
            required_connections.discard(str(request.user))

            recommendation=recommendation.union(required_connections)
        return JsonResponse({'recommendations':list(recommendation)},status=200)