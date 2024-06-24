import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpRequest
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import PlaceSerializer, PayloadSerializer,OrderSerializer
from django.http import JsonResponse
from django.test import RequestFactory
from drf_spectacular.utils import extend_schema,OpenApiTypes

factory = RequestFactory()

FLEETBASE_API_URL_PLACES = "https://api.fleetbase.io/v1/places"
FLEETBASE_API_URL_PAYLOAD = "https://api.fleetbase.io/v1/payloads"
FLEETBASE_API_URL_ORDER = "https://api.fleetbase.io/v1/orders"
FLEETBASE_API_KEY = "flb_live_W10lr168i8OimXsWFTpo" 

def status(request):
    return JsonResponse({'status': 'ok'})

@extend_schema(
    request=PlaceSerializer,
    responses={201: PlaceSerializer,  400: OpenApiTypes.OBJECT, 
        500: OpenApiTypes.OBJECT}
)
class CreatePlaceView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PlaceSerializer

    def post(self, request):
        """
        Create a new place.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Prepare the data to send to Fleetbase
            payload = {
                'name': serializer.validated_data['name'],
                'latitude': serializer.validated_data['latitude'],
                'longitude': serializer.validated_data['longitude']
            }
            headers = {
                'Authorization': f'Bearer {FLEETBASE_API_KEY}',
                'Content-Type': 'application/json'
            }
            # Make the request to Fleetbase
            response = requests.post(FLEETBASE_API_URL_PLACES, json=payload, headers=headers)
            if response.status_code == 201:
                place_data = response.json()
                place_id = place_data.get('id')
                request.session['dropoff_id'] = place_id
                return Response({'dropoff_place_id': place_id}, status=status.HTTP_201_CREATED)
            else:
                return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=PayloadSerializer,
    responses={201: PayloadSerializer, 400: OpenApiTypes.OBJECT, 
        500: OpenApiTypes.OBJECT}
)
class CreatePayloadView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PlaceSerializer
    def post(self, request):
        """
        Create a new place.
        """
        serializer = PayloadSerializer(data=request.data)
        if serializer.is_valid():
            # Prepare the data to send to Fleetbase
            payload = {
                'pickup': serializer.validated_data['pickup'],
                'dropoff': serializer.validated_data['dropoff'],
                'return': serializer.validated_data.get('return', ''),
                'customer': serializer.validated_data['customer'],
                'meta': serializer.validated_data.get('meta', {}),
                'cod_amount': serializer.validated_data.get('cod_amount', 0),
                'cod_currency': serializer.validated_data.get('cod_currency', 'USD'),
                'cod_payment_method': serializer.validated_data.get('cod_payment_method', 'cash'),
                'type': serializer.validated_data['type'],
            }
            headers = {
                'Authorization': f'Bearer {FLEETBASE_API_KEY}',
                'Content-Type': 'application/json'
            }
            # Make the request to Fleetbase
            response = requests.post(FLEETBASE_API_URL_PAYLOAD, json=payload, headers=headers)
            if response.status_code == 201:
                payload_data = response.json()
                payload_id = payload_data.get('id')
                request.session['payload_id'] = payload_id
                return Response({'payload_id': payload_id}, status=status.HTTP_201_CREATED)
            else:
                return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=OrderSerializer,
    responses={201: OrderSerializer, 400: OpenApiTypes.OBJECT, 
        500: OpenApiTypes.OBJECT}
)
class CreateOrderView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    def post(self, request):
        """
        Create a new order.
        """
        pickup_data = {
            'name': request.data.get('pickup_name'),
            'latitude': request.data.get('pickup_latitude'),
            'longitude': request.data.get('pickup_longitude')
        }
        
        pickup_response = fn_create_place(pickup_data)
        
        if pickup_response.status_code != 201:
            if pickup_response.status_code == 200:
                pickup_id = pickup_response.data.get('id')
                print(f"---------------PICKUP PLACE ALREADY EXISTS {pickup_id} ---------------")
            else:
                return pickup_response
        else:
            pickup_id = pickup_response.data.get('place_id')
            print(f"---------------PICKUP PLACE CREATED {pickup_id} ---------------")
        
        # Create dropoff place
        dropoff_data = {
            'name': request.data.get('dropoff_name'),
            'latitude': request.data.get('dropoff_latitude'),
            'longitude': request.data.get('dropoff_longitude')
        }
        dropoff_response = fn_create_place(dropoff_data)
        if dropoff_response.status_code != 201:
            if dropoff_response.status_code == 200:
                dropoff_id = pickup_response.data.get('id')
                print(f"--------------- DROPOFF PLACE ALREADY EXISTS {dropoff_id} ---------------")
            else:
                return dropoff_response
        else:    
            dropoff_id = dropoff_response.data.get('place_id')
            print(f"---------------DROPOFF PLACE CREATED {dropoff_id} ---------------")


        # Create payload
        payload_data = {
            'pickup': pickup_id,
            'dropoff': dropoff_id,
            'return':  pickup_id,
            'customer': request.data.get('customer'),
            'meta': request.data.get('meta', {}),
            'cod_amount': request.data.get('cod_amount', 0),
            'cod_currency': request.data.get('cod_currency', 'USD'),
            'cod_payment_method': request.data.get('cod_payment_method', 'cash'),
            'type': request.data.get('type')
        }
        payload_response = fn_create_payload(payload_data)
        if payload_response.status_code != 201:
            return payload_response
        payload_id = payload_response.data.get('payload_id')
        print(f"---------------PAYLOAD CREATED {payload_id}---------------")

        
        # Create order
        order_data = {
            'payload': payload_id,
            'dispatch': request.data.get('dispatch', True),
            'type': request.data.get('order_type'),
            'facilitator': request.data.get('facilitator'),
            'customer': request.data.get('customer'),
            'notes': request.data.get('delivery_notes', ''),
            'driver': request.data.get('driver', '')
        }
        headers = {
            'Authorization': f'Bearer {FLEETBASE_API_KEY}',
            'Content-Type': 'application/json'
        }
        # Make the request to Fleetbase
        response = requests.post(FLEETBASE_API_URL_ORDER, json=order_data, headers=headers)
        if response.status_code == 201:
            order_data = response.json()
            order_id = order_data.get('id')
            print(f"--------------- ORDER SUCCESSFULLY CREATED {order_id}---------------")
            return Response({'order_id': order_id}, status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)



# --------------------------------------
def fn_create_place(place_data):
    serializer = PlaceSerializer(data=place_data)

    if serializer.is_valid():
        payload = {
            'name': serializer.validated_data['name'],
            'latitude': serializer.validated_data['latitude'],
            'longitude': serializer.validated_data['longitude']
        }

        headers = {
            'Authorization': f'Bearer {FLEETBASE_API_KEY}',
            'Content-Type': 'application/json'
        }

        # Make the request to Fleetbase
        response = requests.post(FLEETBASE_API_URL_PLACES, json=payload, headers=headers)

        if response.status_code == 201:
            place_data = response.json()
            place_id = place_data.get('id')
            return Response({'place_id': place_id}, status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def fn_create_payload(payload_data):
    serializer = PayloadSerializer(data=payload_data)
    if serializer.is_valid():
        # Prepare the data to send to Fleetbase
        payload = {
            'pickup': serializer.validated_data['pickup'],
            'dropoff': serializer.validated_data['dropoff'],
            'return': serializer.validated_data.get('return', ''),
            'customer': serializer.validated_data['customer'],
            'meta': serializer.validated_data.get('meta', {}),
            'cod_amount': serializer.validated_data.get('cod_amount', 0),
            'cod_currency': serializer.validated_data.get('cod_currency', 'USD'),
            'cod_payment_method': serializer.validated_data.get('cod_payment_method', 'cash'),
            'type': serializer.validated_data['type'],
        }
        headers = {
            'Authorization': f'Bearer {FLEETBASE_API_KEY}',
            'Content-Type': 'application/json'
        }
        # Make the request to Fleetbase
        response = requests.post(FLEETBASE_API_URL_PAYLOAD, json=payload, headers=headers)
        if response.status_code == 201:
            payload_data = response.json()
            payload_id = payload_data.get('id')
            return Response({'payload_id': payload_id}, status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ------------------ PENDING ------------------
# When a place exists already, the code stops - DONE
# Add the COD aount from the price of delivery + value of the actual item