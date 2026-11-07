from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import AttachmentUploadSerializer

# Create your views here.
class AttachmentUploadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request):

        uploaded_file = request.FILES.get("file")

        serializer = AttachmentUploadSerializer(
            data=request.data,
            context={
                "request": request,
            }
        )

        if serializer.is_valid():

            attachment = serializer.save()

            # Preserve original upload metadata in this response.
            serializer.context["uploaded_file_name"] = uploaded_file.name
            serializer.context["uploaded_content_type"] = (
                uploaded_file.content_type
            )

            return Response(
                {
                    "success": True,
                    "message": "Attachment uploaded successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "message": "Attachment upload failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )