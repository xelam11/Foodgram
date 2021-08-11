from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets, filters, mixins
from django.shortcuts import get_object_or_404
from rest_framework import status

from djoser.views import UserViewSet

from .models import Follow, CustomUser
from .serializers import FollowSerializer


class FollowViewSet(UserViewSet):

    # filter_backends = [filters.SearchFilter]
    # search_fields = ['user__username', 'following__username']

    def get_queryset(self):
        if self.action in ('subscribe', 'subscriptions'):
            username = self.request.user.username
            user = get_object_or_404(CustomUser, username=username)
            return Follow.objects.filter(user=user)

        return super().get_queryset()

    def get_serializer_class(self):
        if self.action in ('subscribe', 'subscriptions'):
            return FollowSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ('subscriptions', 'subscribe'):
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    # /subscriptions
    @action(detail=False)
    def subscriptions(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    # /id/subscribe
    @action(detail=True, methods=['get', 'delete'])
    def subscribe(self, request, *args, **kwargs):
        if request.method == 'GET':
            data = {
                'user': self.request.user.pk,
                'following': self.kwargs.get('id'),
            }

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            queryset = self.filter_queryset(self.get_queryset())

            instance = get_object_or_404(queryset,
                                         following=self.kwargs.get('id'))
            self.check_object_permissions(self.request, instance)
            instance.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        raise AssertionError("This should never happen. Unexpected method.")

