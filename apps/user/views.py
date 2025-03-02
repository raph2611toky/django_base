from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import TokenError
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.user.serializers import UserSerializer, LoginSerializer, RegisterSerializer
from apps.user.models import User

from dotenv import load_dotenv
import traceback

load_dotenv()


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupérer le profil de l'utilisateur connecté",
        responses={
            200: openapi.Response(
                description="Profil récupéré avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                        "name": openapi.Schema(type=openapi.TYPE_STRING, example="John Doe"),
                        "email": openapi.Schema(type=openapi.TYPE_STRING, example="user@example.com"),
                        "sexe": openapi.Schema(type=openapi.TYPE_STRING, example="M"),
                        "birth_date": openapi.Schema(type=openapi.TYPE_STRING, format="date", example="1990-01-01"),
                        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                    },
                ),
            ),
            403: openapi.Response(
                description="Accès refusé: votre compte doit être actif.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, example="Accès refusé: votre compte doit être actif. Veuillez vous connecter pour continuer."),
                    },
                ),
            ),
        },
        security=[{'Bearer': []}],
    )
    
    def get(self, request:Request):
        serializer = UserSerializer(request.user, context={'request': request})
        user = serializer.data
        if not user['is_active']:
            return Response({'error': 'Accès refusé: votre compte doit être actif. Veuillez vous connecter pour continuer.'}, status=403)
        return Response(user, status=200)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Déconnexion de l'utilisateur",
        responses={
            200: openapi.Response(
                description="Utilisateur déconnecté",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Utilisateur déconnecté avec succès.")
                    },
                ),
            ),
            404: openapi.Response(
                description="Utilisateur non trouvé",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "erreur": openapi.Schema(type=openapi.TYPE_STRING, example="Utilisateur non trouvé")
                    },
                ),
            ),
        },
        security=[{'Bearer': []}],
    )

    def put(self, request:Request):
        try:
            user = User.objects.get(id=request.user.id)
            user.is_active = False
            user.save()
            return Response({'message':'Utilisateur déconnecté avec succès.'}, status=200)
        except User.DoesNotExist:
            return Response({'erreur':"Utilisateur non trouvé"}, status=404)

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    @swagger_auto_schema(
        operation_description="Connexion de l'utilisateur",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Connexion réussie",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING, example="eyJhbGciOiJIUzI1..."),
                        "name": openapi.Schema(type=openapi.TYPE_STRING, example="John Doe"),
                        "sexe": openapi.Schema(type=openapi.TYPE_STRING, example="M"),
                    },
                ),
            ),
            400: openapi.Response(
                description="Erreur de validation des identifiants",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "erreur": openapi.Schema(type=openapi.TYPE_STRING, example="Identifiants invalides"),
                    },
                ),
            ),
        },
    )

    def post(self, request):
        # request.data.keys = ['email', 'password']
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer 
    
    
    def check_if_user_exist(self, email):
        return User.objects.filter(email=email).exists()
    
    def validate_data(self, data):
        try:
            keys = ['name','email','password','sexe', 'birth_date']
            if any(key not in data.keys() for key in keys):
                return False
            return True
        except Exception as e:
            return False
    
    
    @swagger_auto_schema(
        operation_description="Inscription d'un nouvel utilisateur",
        request_body=RegisterSerializer,
        
        responses={
            201: openapi.Response(
                description="Utilisateur créé",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "email": openapi.Schema(type=openapi.TYPE_STRING, example="user@example.com"),
                    },
                ),
            ),
            400: openapi.Response(
                description="Données invalides",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "erreur": openapi.Schema(type=openapi.TYPE_STRING, example="email existant"),
                    },
                ),
            ),
        },
    )
    def post(self, request):
        # request.data.keys = ['name','email','password','sexe', 'proffession_domaine', 'birth_date']
        try:
            user_data = request.data
            print(request.data)
            if not self.validate_data(user_data):
                return Response({'erreur':'Tous les attributs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            birth_date = request.data['birth_date'].replace('/','-')
            user_data['birth_date'] = birth_date
            if self.check_if_user_exist(request.data['email']):
                return Response({'erreur':'email existant'},status=400)
            if "profession_domaine"not in user_data:
                user_data["profession_domaine"]="Inconu"
            if user_data.get('sexe', 'I').lower() not in ['masculin', 'feminin']: user_data['sexe'] = 'I'
            else: user_data['sexe'] = user_data['sexe'].strip()[0].upper()
            
            serializer = RegisterSerializer(data=user_data)
            if serializer.is_valid(raise_exception=True):
                return Response({"email":serializer.validated_data["email"]}, status=status.HTTP_201_CREATED)
            else:
                return Response({'erreur':'erreur de serialisation'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        