from django.contrib.auth.models import User
from rest_framework import serializers, validators


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer.
    """
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'confirm_password')
        extra_kwargs = {'password': {'write_only': True}}

    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    confirm_password = serializers.ReadOnlyField()

    def validate(self, attrs):
        if self.initial_data.get('password') != self.initial_data.get('confirm_password'):
            raise serializers.ValidationError('Passwords must match.')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
