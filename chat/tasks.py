from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from api.models import Booking
from .models import ChatGroup, ChatMessage


@shared_task
def soft_delete_confirmed_bookings_after_1_month():

    one_month_ago = timezone.now() - timedelta(days=30)

    with transaction.atomic():

        # 1. Get served bookings older than 30 days
        bookings = Booking.objects.filter(
            created_at__lte=one_month_ago,
            status=Booking.STATUS.SERVED
        )

        booking_count = bookings.count()

        # 2. Get related chat groups
        chatgroups = ChatGroup.objects.filter(
            booking__in=bookings
        )

        chatgroup_count = chatgroups.count()

        # 3. Get chat group IDs
        chatgroup_ids = chatgroups.values_list("id", flat=True)

        # 4. Archive associated messages
        messages = ChatMessage.objects.filter(
            group_id__in=chatgroup_ids,
            is_archived=False
        )

        message_count = messages.count()

        messages.update(
            is_archived=True,
            archived_at=timezone.now()
        )

        # 5. Deactivate chat groups
        chatgroups.update(
            is_active=False
        )

    print(
        f"Soft deleted {booking_count} bookings, "
        f"deactivated {chatgroup_count} chat groups, "
        f"and archived {message_count} messages."
    )

    return {
        "bookings": booking_count,
        "chatgroups": chatgroup_count,
        "messages": message_count
    }