from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import authenticate
from .serializers import PropertySerializer, SearchSerializer, RecommendSerializer, RegisterSerializer
from .pinecone_client import add_property_to_index, search_properties_in_index, recommend_from_profile
from .models import CustomUser, SearchHistory, Property

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'message': 'Please provide both email and password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                'message': 'Login successful',
                'token': {
                    'access': access_token,
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

class SearchHistoryView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # Get token from either header or query parameter
            auth_header = request.headers.get('Authorization')
            token = None
            
            if auth_header:
                token = auth_header.split(' ')[1] if 'Bearer ' in auth_header else auth_header
            elif 'token' in request.query_params:
                token = request.query_params['token']
            
            if token:
                try:
                    # Verify token manually
                    access_token = AccessToken(token)
                    user_id = access_token.payload.get('user_id')
                    user = CustomUser.objects.get(id=user_id)
                    
                    history = SearchHistory.objects.filter(user=user).order_by('-timestamp')
                    
                    # Serialize user data
                    user_data = {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username
                    }
                    
                    return Response([
                        {
                            'id': item.id,  
                            'user': user_data,  # Use serialized user data
                            'query': item.query,
                            'filters': item.filters,
                            'results': item.results,
                            'recommendations': item.recommendations,
                            'search_type': item.search_type,
                            'timestamp': item.timestamp,
                        }
                        for item in history
                    ])
                except Exception as e:
                    return Response({"error": "Invalid token"}, status=401)
            else:
                return Response({"error": "No token provided"}, status=401)
        except Exception as e:
            print(f"Error in SearchHistoryView: {str(e)}")
            return Response({"error": str(e)}, status=500)

class AddPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PropertySerializer(data=request.data)
        if serializer.is_valid():
            prop_id = serializer.validated_data['id']
            if Property.objects.filter(id=prop_id).exists():
                return Response({"error": "A property with this ID already exists."}, status=400)
            property_instance = serializer.save()  # Save to local DB
            add_property_to_index(serializer.data) # Index in Pinecone
            return Response({"message": "Property added and indexed ✅"}, status=201)
        return Response(serializer.errors, status=400)

class SearchPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = SearchSerializer(data=request.query_params)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            filters = serializer.validated_data.get('filters')
            
            results = search_properties_in_index(query, filters)
            
            # Save search history with results
            SearchHistory.objects.create(
                user=request.user,
                query=query,
                filters=filters,
                results=results.get('matches', []),
                search_type='search'
            )
            
            return Response(results.get('matches', []))
        return Response(serializer.errors, status=400)

class RecommendView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = RecommendSerializer(data=request.query_params)
        if serializer.is_valid():
            results = recommend_from_profile(serializer.validated_data)
            
            # Save recommendation history
            SearchHistory.objects.create(
                user=request.user,
                query=serializer.validated_data.get('query', ''),
                filters=serializer.validated_data.get('filters', {}),
                recommendations=results['matches'],
                search_type='recommend'
            )
            
            return Response(results['matches'])
        return Response(serializer.errors, status=400)
