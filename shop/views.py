from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsVendor
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsVendor])
def create_product(request):
    return Response({"message": "Product created"})
