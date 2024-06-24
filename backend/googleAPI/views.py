import requests
from rest_framework.generics import GenericAPIView
from django.http import JsonResponse  # Consider using Response from rest_framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from .serializers import DistanceSerializer
from drf_spectacular.utils import extend_schema,OpenApiTypes

def status(request):
    return JsonResponse({'status': 'ok'})

@extend_schema(
    request=DistanceSerializer,
    responses={201: DistanceSerializer,  400: OpenApiTypes.OBJECT, 
        500: OpenApiTypes.OBJECT}
)
class calculateDistanceView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = DistanceSerializer

    def post(self,request):
        '''
        Calculate distance between two points
        '''

        origin_lat = request.data.get('origin_lat')
        origin_long = request.data.get('origin_long')
        destination_lat = request.data.get('destination_lat')
        destination_long = request.data.get('destination_long')

        if not all([origin_lat, origin_long, destination_lat, destination_long]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

    #    api_key = settings.GOOGLE_API_KEY
        api_key = 'AIzaSyCN-0aWhXvbLH4e62-UQWLp2eNKA8dP--4'
        origin = f"{origin_lat},{origin_long}"
        destination = f"{destination_lat},{destination_long}"

        url = (
            "https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origin}&destinations={destination}&key={api_key}"
        )

        response = requests.get(url)
        data = response.json()

        if data['status'] != 'OK':
            error_message = data.get('error_message', 'Unknown error')
            return JsonResponse({'error': 'Error from Google API', 'message': error_message}, status=500)

        try:
            distance_text = data['rows'][0]['elements'][0]['distance']['text']
            distance_value = data['rows'][0]['elements'][0]['distance']['value']
            distance_km = distance_value / 1000  # Convert meters to kilometers
        except (IndexError, KeyError):
            return JsonResponse({'error': 'Invalid response from Google API'}, status=500)

        delivery_price = calculate_delivery_price(distance_km)

        return JsonResponse({'delivery_price': delivery_price})





def calculate_delivery_price(distance_km):
  """
  Calculates the delivery price based on distance in kilometers.

  Args:
      distance_km: The distance in kilometers (float).

  Returns:
      The delivery price in Kenyan Shilling (KSH) (float).
  """


  base_price = 200  # KSH

  if distance_km > 25:
      return {'message': "Sorry, E-Bikes rider unable to deliver to that location"}

  if distance_km <= 10:
      return base_price
  else:
      # Price for exceeding 10 KMs: 25 KSH per additional KM
      additional_distance = distance_km - 10
      additional_price = additional_distance * 25
      total_price = base_price + additional_price
      return total_price


# http://127.0.0.1:8000/google_api/calculate-distance/?origin_lat=37.7749&origin_long=-122.4194&destination_lat=34.0522&destination_long=-118.2437
# Galleria Mall: -1.3433182103402546, 36.76600758309724
# The Ten Villas: -1.3913519108241854, 36.76051708309745

