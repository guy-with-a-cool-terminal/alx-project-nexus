def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    validated_data = serializer.validated_data.copy()
    
    # Handle seller registration with validation
    if request.data.get('role') == 'SELLER':
        if not request.data.get('store_name'):
            return Response(
                {"store_name": "Store name is required for seller registration!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        validated_data['role'] = 'SELLER'
    else:
        # Force CONSUMER for all other cases (including empty role)
        validated_data['role'] = 'CONSUMER'
    
    # Create user
    user = serializer.save(**validated_data)
    EmailService.send_welcome_email(user)
    
    return Response({
        "message": "User registered successfully.",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }, status=status.HTTP_201_CREATED)