from rest_framework import serializers
from typing import Dict, Any, List
from django.contrib.auth import get_user_model
from .models import PublicTender, FollowTender, PrivateTender, TenderNote

User = get_user_model()

class PublicTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicTender
        fields = '__all__'
        read_only_fields = ['uuid']

class PrivateTenderSerializer(serializers.ModelSerializer):
    shared_with_usernames = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = PrivateTender
        fields = [
            'uuid', 'title', 'description', 'company_name',
            'city', 'region', 'publication_date', 'submission_deadline',
            'details_url', 'created_at', 'updated_at', 'owner',
            'shared_with_usernames'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'owner']

    def create(self, validated_data: Dict[str, Any]) -> PrivateTender:
        shared_with_usernames = validated_data.pop('shared_with_usernames', [])

        validated_data['owner'] = self.context['request'].user

        instance = super().create(validated_data)

        if shared_with_usernames:
            users_to_share_with = User.objects.filter(username__in=shared_with_usernames)
            instance.shared_with.add(*users_to_share_with)

        return instance

    def update(self, instance: PrivateTender, validated_data: Dict[str, Any]) -> PrivateTender:
        shared_with_usernames = validated_data.pop('shared_with_usernames', None)

        instance = super().update(instance, validated_data)

        if shared_with_usernames is not None:
            instance.shared_with.clear()
            users_to_share_with = User.objects.filter(username__in=shared_with_usernames)
            instance.shared_with.add(*users_to_share_with)

        return instance


class TenderNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderNote
        fields = ['id', 'tender_uuid', 'tender_type', 'user', 'note', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        tender_uuid = attrs.get('tender_uuid')
        tender_type = attrs.get('tender_type')
        user = self.context['request'].user

        try:
            if tender_type == 'public':
                tender = PublicTender.objects.get(uuid=tender_uuid)
            elif tender_type == 'private':
                tender = PrivateTender.objects.get(uuid=tender_uuid)
                if tender.owner != user and user not in tender.shared_with.all():
                    raise serializers.ValidationError(
                        "Nie masz uprawnień do dodawania notatek do tego przetargu prywatnego."
                    )
            else:
                raise serializers.ValidationError("Nieprawidłowy typ przetargu.")
        except (PublicTender.DoesNotExist, PrivateTender.DoesNotExist):
            raise serializers.ValidationError("Przetarg o podanym UUID nie istnieje.")

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> TenderNote:
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FollowTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowTender
        fields = ['id', 'tender_uuid', 'tender_type', 'followed_at', 'user']
        read_only_fields = ['id', 'user']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        tender_uuid = attrs.get('tender_uuid')
        tender_type = attrs.get('tender_type')
        user = self.context['request'].user

        try:
            if tender_type == 'public':
                tender = PublicTender.objects.get(uuid=tender_uuid)
            elif tender_type == 'private':
                tender = PrivateTender.objects.get(uuid=tender_uuid)
                if tender.owner != user and user not in tender.shared_with.all():
                    raise serializers.ValidationError(
                        "Nie masz uprawnień do dodawania notatek do tego przetargu prywatnego."
                    )
            else:
                raise serializers.ValidationError("Nieprawidłowy typ przetargu.")

            if FollowTender.objects.filter(user=user, tender_uuid=tender_uuid).exists():
                raise serializers.ValidationError("Obserwujesz już ten przetarg.")

        except (PublicTender.DoesNotExist, PrivateTender.DoesNotExist):
            raise serializers.ValidationError("Przetarg o podanym UUID nie istnieje.")

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> FollowTender:
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
