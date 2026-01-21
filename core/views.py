from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    return Response({"status": "API is working"})

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_ping(request):
    return Response({
        "message": "JWT authentication successful",
        "user": request.user.email,
        "role": request.user.role,
    })
