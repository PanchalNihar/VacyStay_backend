from django.http import JsonResponse
from rest_framework.decorators import api_view,authentication_classes ,permission_classes 
from .models import Property,Reservation
from .forms import PropertyForm
from .serializers import PropertyListSerializers,PropertiesDetailSerializers,ReservationsListSerializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from useraccount.models import User
from rest_framework_simplejwt.tokens import AccessToken
@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def properties_list(request):

    #auth 
    try:
        token=request.META['HTTP_AUHORIZATION'].split('Bearer ')[1]
        token=AccessToken(token)
        user_id=token.payload('user_id')
        user=User.objects.get(pk=user_id)
    except Exception as e:
        user=None
    print('user:',user)

    favourites=[]
    properties = Property.objects.all()
    is_favourite=request.GET.get('is_favourite','')
    landlord_id=request.GET.get('landlord_id','')
    country=request.GET.get('country','')
    category=request.GET.get('category','')
    checkin_date=request.GET.get('checkIn','')
    checkout_date=request.GET.get('checkOut','')
    guests=request.GET.get('numGuests','')
    bathrooms=request.GET.get('numBathrooms','')
    bedrooms=request.GET.get('numBedrooms','')
    if checkin_date and checkout_date:
        excat_matches=Reservation.objects.filter(start_date=checkin_date) | Reservation.objects.filter(end_date=checkout_date)
        overlap_matches=Reservation.objects.filter(start_date__lte=checkout_date,end_date__gte=checkin_date)
        all_matches=[]
        for Reservation in excat_matches | overlap_matches:
            all_matches.append(reservation.property_id)
        properties=properties.exclude(id__in=all_matches)
    if landlord_id:
        properties = properties.filter(landlord_id=landlord_id)
    if is_favourite:
        properties=properties.filter(favorited__in=[user])
    if guests:
        properties = properties.filter(guests__gte=guests)
    if bedrooms:
        properties = properties.filter(bedrooms__gte=bedrooms)
    if bathrooms:
        properties = properties.filter(bathrooms__gte=bathrooms)
    if country:
        properties = properties.filter(country=country)
    if category and category!='undefined':
        properties = properties.filter(category=category)
    # favourites
    if user:
        for property in properties:
            if user in property.favorited.all():
                favourites.append(property.id)
    serializer = PropertyListSerializers(properties, many=True)

    return JsonResponse({
        'data':serializer.data,
        'favourites':favourites
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
    

@api_view(['POST'])
def toggle_favorite(request, pk):
    property = Property.objects.get(pk=pk)

    if request.user in property.favorited.all():
        property.favorited.remove(request.user)

        return JsonResponse({'is_favorite': False})
    else:
        property.favorited.add(request.user)

        return JsonResponse({'is_favorite': True})