from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from django.db.models import Q
from typing import Any, Dict, List, Optional, Type, Union
from .models import PublicTender, FollowPublicTender, PrivateTender, TenderNote
from .serializers import (
    PublicTenderSerializer,
    FollowPublicTenderSerializer,
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

    def get_queryset(self):
        public_tenders = PublicTender.objects.all()
        return public_tenders

    def get_object(self) -> Union[PublicTender, PrivateTender]:
        uuid = self.kwargs['pk']
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

        tenders = PublicTender.objects.filter(followers__user=user)

        serializer = self.get_serializer(tenders, many=True)

        return Response(serializer.data)


class PrivateTenderViewSet(viewsets.ModelViewSet):
    serializer_class = PrivateTenderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tender_id', 'title', 'description', 'company_name']
    ordering_fields = ['publication_date', 'submission_deadline', 'created_at']
    ordering = ['-publication_date']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self) -> List[PrivateTender]:
        user = self.request.user
        return list(PrivateTender.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct())

    def perform_create(self, serializer: PrivateTenderSerializer) -> None:
        serializer.save(owner=self.request.user)


class TenderNoteViewSet(viewsets.ModelViewSet):
    serializer_class = TenderNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['tender_uuid']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user
        return TenderNote.objects.filter(user=user)

    def perform_create(self, serializer: TenderNoteSerializer) -> None:
        serializer.save(user=self.request.user)

class FollowPublicTenderViewSet(viewsets.ModelViewSet):
    serializer_class = FollowPublicTenderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__id']
    http_method_names = ['post', 'delete']

    def get_queryset(self):
        user = self.request.user
        return FollowPublicTender.objects.filter(user=user)

    def perform_create(self, serializer: TenderNoteSerializer) -> None:
        serializer.save(user=self.request.user)
