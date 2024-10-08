from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from app.models import Event, Application


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'photo', 'status',
                  'blockchain_event_id', 'blockchain_transaction_hash']

    def create(self, validated_data):
        # Ensure the creator is set manually in the view
        return Event.objects.create(**validated_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    serializer = EventCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(creator=request.user)
        return Response({'message': 'Event created successfully.'}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_events_noauth(request):
    events = Event.objects.all()
    serializer = EventCreateSerializer(
        events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_events_admin(request):
    user = request.user
    events = Event.objects.filter(
        creator=user, creator__chain_of_address=user.chain_of_address)
    serializer = EventCreateSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_events_with_status(request):
    user = request.user
    events = Event.objects.filter(
        creator__chain_of_address=user.chain_of_address)
    events_data = []

    for event in events:
        is_applied = Application.objects.filter(
            user=user, event=event).exists()
        status1 = "applied" if is_applied else "not_applied"
        event_serializer = EventCreateSerializer(event)
        event_data = event_serializer.data
        event_data['status'] = status1
        events_data.append(event_data)

    return Response(events_data, status=status.HTTP_200_OK)


class EventStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['status']


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_event_status(request, pk):
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user != event.creator:
        raise PermissionDenied(
            "You do not have permission to update this event.")

    serializer = EventStatusUpdateSerializer(event, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
