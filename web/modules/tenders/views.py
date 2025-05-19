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

    def get_queryset(self) -> List[Union[PublicTender, PrivateTender]]:
        user = self.request.user

        public_tenders = PublicTender.objects.all()

        private_tenders = PrivateTender.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct()

        return list(public_tenders) + list(private_tenders)

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

    @action(detail=True, methods=['post'])
    def observe(self, request: Request, pk: str = None) -> Response:
        tender = self.get_object()
        user = request.user

        if not isinstance(tender, PublicTender):
            return Response(
                {"detail": "Tylko przetargi publiczne mogą być obserwowane."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if FollowPublicTender.objects.filter(tender=tender, user=user).exists():
            return Response(
                {"detail": "Już obserwujesz ten przetarg."},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow = FollowPublicTender(tender=tender, user=user)
        follow.save()

        return Response(
            {"detail": "Przetarg został dodany do obserwowanych."},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def notes(self, request: Request, pk: str = None) -> Response:
        tender = self.get_object()
        user = request.user

        if isinstance(tender, PublicTender):
            tender_type = 'public'
        else:
            tender_type = 'private'

        serializer = TenderNoteSerializer(
            data={
                'tender_uuid': tender.uuid,
                'tender_type': tender_type,
                'note': request.data.get('note', '')
            },
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrivateTenderViewSet(viewsets.ModelViewSet):
    serializer_class = PrivateTenderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tender_id', 'title', 'description', 'company_name']
    ordering_fields = ['publication_date', 'submission_deadline', 'created_at']
    ordering = ['-publication_date']

    def get_queryset(self) -> List[PrivateTender]:
        user = self.request.user
        return PrivateTender.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct()

    def perform_create(self, serializer: PrivateTenderSerializer) -> None:
        serializer.save(owner=self.request.user)


class TenderNoteViewSet(viewsets.ModelViewSet):
    serializer_class = TenderNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> List[TenderNote]:
        user = self.request.user
        return TenderNote.objects.filter(user=user)

    def perform_create(self, serializer: TenderNoteSerializer) -> None:
        serializer.save(user=self.request.user)
