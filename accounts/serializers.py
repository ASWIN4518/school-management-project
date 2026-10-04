from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "role_display",
            "is_superuser",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = ["id", "full_name", "role_display", "date_joined"]

    def get_full_name(self, obj):
        name = obj.get_full_name()
        return name if name else obj.username
