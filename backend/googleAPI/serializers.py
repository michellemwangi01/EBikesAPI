from rest_framework import serializers

class DistanceSerializer(serializers.Serializer):
    origin_lat = serializers.FloatField()
    origin_long = serializers.FloatField()
    destination_lat = serializers.FloatField()
    destination_long = serializers.FloatField()