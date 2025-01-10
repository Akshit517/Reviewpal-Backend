from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import mimetypes

class UploadMediaView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # Define allowed file types
    ALLOWED_EXTENSIONS = {
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'pdf': ['application/pdf'],
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
    }

    def get_file_category(self, content_type):
        """Determine the file category based on content type"""
        for category, types in self.ALLOWED_EXTENSIONS.items():
            if content_type in types:
                return category
        return None

    def validate_file(self, file):
        """Validate file type and size"""
        # Get content type
        content_type = file.content_type
        
        file_category = self.get_file_category(content_type)
        if not file_category:
            allowed_types = [t for types in self.ALLOWED_EXTENSIONS.values() for t in types]
            raise ValueError(f'Unsupported file type. Allowed types: {", ".join(allowed_types)}')
        
        if file.size > 10 * 1024 * 1024:
            raise ValueError('File size too large. Maximum size is 10MB')
        
        return file_category

    def get_unique_filename(self, directory, filename):
        """Generate a unique filename if file already exists"""
        base, ext = os.path.splitext(filename)
        counter = 1
        while default_storage.exists(os.path.join(directory, filename)):
            filename = f"{base}_{counter}{ext}"
            counter += 1
        return filename

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES['file']

        try:
            file_category = self.validate_file(uploaded_file)
            
            directory = f'{file_category}'
            
            os.makedirs(directory, exist_ok=True)
            
            filename = self.get_unique_filename(directory, uploaded_file.name)
            
            file_path = default_storage.save(
                f'{directory}/{filename}', 
                ContentFile(uploaded_file.read())
            )
            
            file_url = request.build_absolute_uri(f'/media/{file_category}/{filename}')
            
            return Response(
                {
                    'url': file_url,
                    'file_type': file_category,
                    'filename': filename
                }, 
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to upload file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )