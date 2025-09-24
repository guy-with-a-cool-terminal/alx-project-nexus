from .utils.email_service import EmailService  # Add this import

class UserViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ... your existing validation logic ...
        
        user = serializer.save()
        
        # Send welcome email (non-blocking)
        EmailService.send_welcome_email(user)
        
        return Response(
            {
                "message": "User registered successfully.",
                "user_id": user.id,
                "username": user.username
            },
            status=status.HTTP_201_CREATED
        )