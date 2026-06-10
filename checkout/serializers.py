from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32)
    address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    province = serializers.CharField(max_length=100)
    zip = serializers.CharField(max_length=20)
    region = serializers.CharField(max_length=100, required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=("cod", "gcash", "card"))
