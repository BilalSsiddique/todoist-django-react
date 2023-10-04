from api.serializers import UserSerializer,ListSerializer,TaskSerializer
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import *
from rest_framework.authtoken.models import Token
from rest_framework.response import Response 
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes,permission_classes
from rest_framework.authentication import SessionAuthentication,TokenAuthentication
from django.core.paginator import Paginator,EmptyPage


User= get_user_model()




@api_view(['POST'])
def login(request):
    try:
        user = User.objects.get(email=request.data['email'])
    except User.DoesNotExist:
        return Response({"detail": "User Not found"}, status=status.HTTP_404_NOT_FOUND)

    if not user.check_password(request.data['password']):
        return Response({"detail": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})




@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        print('successfull')
        return Response("Successfully Registered")
    
    # print('vali',error_response)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    user_token = request.auth

    if user_token:
        user_token.delete()
        return Response({"detail": "Logout successful","logout":True}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "No valid token found","logout":False}, status=status.HTTP_400_BAD_REQUEST)



# ################################### Task Views #################################################

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_list(request):
    serializer = ListSerializer(data= request.data,context={'request': request})

    if serializer.is_valid():
        try:
                serializer.save() # invokes create method
                return Response({'message': 'List created successfully.'}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_list(request):
    try:
        user_list = List.objects.filter(user_id=request.user)
        serializer = ListSerializer(user_list, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except List.DoesNotExist:
        return JsonResponse({'error': 'No list exists for the user'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_task(request):
    try:
        user_tasks = Task.objects.select_related('list_id__user_id').filter(list_id__user_id=request.user)
        p = Paginator(user_tasks,per_page=6)
        page_number =request.GET.get('page',1)
        user_task = p.get_page(page_number)
        serializer = TaskSerializer(user_task,many=True)

        # Pagination information
        total_pages = p.num_pages
        total_items = p.count
        items_on_page = len(serializer.data)
        # Generate a list of all available page numbers
        all_pages = list(range(1, total_pages + 1))

        
        # Build pagination links
        current_page= user_task.number
        next_page = p.page(page_number).next_page_number() if user_task.has_next() else None
        prev_page = p.page(page_number).previous_page_number() if user_task.has_previous() else None
        

        # Create a dictionary to hold the response data
        response_data = {
            'current_page':current_page,
            'total_pages': total_pages,
            'total_items': total_items,
            'items_on_page': items_on_page,
            'next_page': next_page,
            'prev_page': prev_page,
            'all_pages': all_pages,
            'data': serializer.data
        }
        
        return Response(response_data,status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'No Task exists for the user'}, status=status.HTTP_404_NOT_FOUND)
    except EmptyPage:
        return Response({'error': 'That page contains no results'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_task_by_id(request,id):
    try:
        user_task = Task.objects.select_related('list_id__user_id').get(id=id, list_id__user_id=request.user)
        serializer = TaskSerializer(user_task)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'No Task exists for the user'}, status=status.HTTP_404_NOT_FOUND)




@api_view(['POST'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_task(request):
    serializer = TaskSerializer(data=request.data,context={'request': request,'format_dates': False})
    if serializer.is_valid():
        try:
            serializer.save() 
            return Response({'message': 'Task created successfully.'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def partial_update_task(request,id):
    try:
        task = Task.objects.select_related('list_id__user_id').get(id=id,list_id__user_id=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({f'{serializer.data["title"]} status updated successfully '}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_task(request,id):
    try:
        task = Task.objects.select_related('list_id__user_id').get(id=id,list_id__user_id=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TaskSerializer(task, data=request.data,)
    if serializer.is_valid():
        serializer.save()
        return Response({f'{serializer.data["title"]} status updated successfully '}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_task(request,id):
    try:
        task =  Task.objects.filter(id=id, list_id__user_id=request.user)
        if task.exists():
            user_task = Task.objects.get(id=id, list_id__user_id=request.user)
            task_title = user_task.title
            user_task.delete()
            return Response({f"Task '{task_title}' deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({f'Task not found '}, status=status.HTTP_404_NOT_FOUND)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_performance(request):
    try:
        un_completed= Task.objects.filter(is_Completed=False,list_id__user_id=request.user).count()
        completed= Task.objects.filter(is_Completed=True,list_id__user_id=request.user).count()
        task_counts = {
        'completed': completed,
        'uncompleted': un_completed
        }
        
        return Response(task_counts, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
























# class ListViewSet(viewsets.ModelViewSet):
#     queryset = List.objects.all()
#     serializer_class = ListSerializer

#     authentication_classes = [TokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
        
#         # mutable_data = request.data.copy()  # Create a mutable copy
#         # print('sss',mutable_data)
#         # mutable_data['user'] = request.user.id 
#         # Create the list using the serializer
#         print("sssssssss",request.data)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# class TaskViewSet(viewsets.ModelViewSet):
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer

#     authentication_classes = [TokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAuthenticated]



# class UsersViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]


# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = [IsAuthenticated]
