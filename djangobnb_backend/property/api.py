from django.http import JsonResponse
from rest_framework.decorators import api_view,authentication_classes ,permission_classes 
from .models import Property,Reservation
from .forms import PropertyForm
from .serializers import PropertyListSerializers,PropertiesDetailSerializers,ReservationsListSerializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def properties_list(request):
    properties = Property.objects.all()
    serializer = PropertyListSerializers(properties, many=True)

    return JsonResponse({
        'data':serializer.data
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def properties_detail(request, pk):
    try:
        property_instance = Property.objects.get(pk=pk)
    except Property.DoesNotExist:
        return JsonResponse({'error': 'Property not found'}, status=404)

    serializer = PropertiesDetailSerializers(property_instance)  # No many=True
    return JsonResponse(serializer.data)



@api_view(['POST','FILES'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_property(request):
    print("Received POST data:", request.POST)
    print("Received FILE data:", request.FILES)

    form = PropertyForm(request.POST, request.FILES)
    if form.is_valid():
        property = form.save(commit=False)
        property.landlord = request.user
        property.save()
        return JsonResponse({'success': True})
    else:
        print("Form errors:", form.errors)  # Debugging line
        return JsonResponse({'errors': form.errors.as_json()}, status=400)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def property_reservations(request,pk):
    try:
        property= Property.objects.get(pk=pk)
        reservations=property.reservations.all()
        serializer=ReservationsListSerializers(reservations,many=True)
        return JsonResponse({'data':serializer.data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@api_view(["POST"])
def book_property(request, pk):
    try:
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        number_of_nights = request.POST.get('number_of_nights')
        total_price = request.POST.get('total_price')
        guests = request.POST.get('guests')

        property = Property.objects.get(pk=pk)
        
        # Assuming `request.user` is available and authenticated
        Reservation.objects.create(
            property=property,
            start_date=(start_date),
            end_date=(end_date),
            number_of_nights=int(number_of_nights),
            total_price=float(total_price),
            guests=int(guests),
            created_by=request.user
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)