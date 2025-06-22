from typing import Any, Dict, List, Optional, Type, Union
from rest_framework import viewsets, status, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.viewsets import GenericViewSet

from .models import PublicTender, FollowTender, PrivateTender, TenderNote
from .serializers import (
    PublicTenderSerializer,
    FollowTenderSerializer,
    PrivateTenderSerializer,
    TenderNoteSerializer
)

class TenderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tender_id', 'order_name', 'title', 'description', 'contracting_authority', 'company_name']
    ordering_fields = ['publication_date', 'submission_deadline', 'created_at']
    ordering = ['-publication_date']
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'uuid'

    def get_queryset(self):
        public_tenders = PublicTender.objects.all()
        return public_tenders

    def get_object(self) -> Union[PublicTender, PrivateTender]:
        uuid = self.kwargs['uuid']
        user = self.request.user

        try:
            return PublicTender.objects.get(uuid=uuid)
        except PublicTender.DoesNotExist:
            pass

        try:
            return PrivateTender.objects.get(
                Q(uuid=uuid) & (Q(owner=user) | Q(shared_with=user))
            )
        except PrivateTender.DoesNotExist:
            from django.http import Http404
            raise Http404("Tender not found or you don't have access to it.")

    def get_serializer_class(self) -> Type[Union[PublicTenderSerializer, PrivateTenderSerializer]]:
        if self.action == 'retrieve':
            obj = self.get_object()
            if isinstance(obj, PublicTender):
                return PublicTenderSerializer
            else:
                return PrivateTenderSerializer
        return PublicTenderSerializer

    @action(detail=False, methods=['get'])
    def observed(self, request: Request) -> Response:
        user = request.user

        followed_tender_uuids = FollowTender.objects.filter(user=user,).values_list('tender_uuid', flat=True)

        public_tenders = PublicTender.objects.filter(uuid__in=followed_tender_uuids)
        private_tenders = PrivateTender.objects.filter(uuid__in=followed_tender_uuids)

        public_serializer = PublicTenderSerializer(public_tenders, many=True)
        private_serializer = PrivateTenderSerializer(private_tenders, many=True)

        public_data = public_serializer.data
        private_data = private_serializer.data

        for item in public_data:
            item['app_tender_type'] = 'public'

        for item in private_data:
            item['app_tender_type'] = 'private'

        return Response(public_data + private_data)


class PrivateTenderViewSet(viewsets.ModelViewSet):
    serializer_class = PrivateTenderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company_name', 'shared_with__username']
    ordering_fields = ['publication_date', 'submission_deadline', 'created_at']
    ordering = ['-publication_date']
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'uuid'

    def get_queryset(self):
        user = self.request.user
        return PrivateTender.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct()

    def perform_create(self, serializer: PrivateTenderSerializer) -> None:
        serializer.save(owner=self.request.user)


class TenderNoteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = TenderNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['tender_uuid']

    def get_queryset(self):
        user = self.request.user
        return TenderNote.objects.filter(user=user)

    def perform_create(self, serializer: TenderNoteSerializer) -> None:
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='tender_uuid',
                description='UUID przetargu',
                required=True,
                type=str
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def get_for_tender(self, request: Request) -> Response:
        user = self.request.user
        tender_uuid = request.query_params.get('tender_uuid')

        if not tender_uuid:
            return Response({"error": "Brak parametru tender_uuid"}, status=status.HTTP_400_BAD_REQUEST)

        notes = TenderNote.objects.filter(user=user, tender_uuid=tender_uuid)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)


class FollowTenderViewSet(viewsets.ModelViewSet):
    serializer_class = FollowTenderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__id']
    http_method_names = ['post', 'delete']

    def get_queryset(self):
        user = self.request.user
        return FollowTender.objects.filter(user=user)

    def perform_create(self, serializer: TenderNoteSerializer) -> None:
        serializer.save(user=self.request.user)
