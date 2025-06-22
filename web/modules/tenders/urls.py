from django.urls import path, include
from rest_framework.routers import DefaultRouter
from typing import List
from .views import TenderViewSet, PrivateTenderViewSet, TenderNoteViewSet, FollowTenderViewSet

router = DefaultRouter()
router.register(r'tenders', TenderViewSet, basename='tender')
router.register(r'private-tenders', PrivateTenderViewSet, basename='private-tender')
router.register(r'tender-notes', TenderNoteViewSet, basename='tender-note')
router.register(r'tender-follows', FollowTenderViewSet, basename='tender-follow')

urlpatterns: List[path] = [
    path('', include(router.urls)),
]
