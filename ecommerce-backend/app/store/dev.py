def perform_create(self, serializer):
    """
    Automatically set the seller to the current user
    """
    from rest_framework.exceptions import PermissionDenied  # Add this line
    
    # Ensure only sellers can create products
    if not self.request.user.is_seller:
        raise PermissionDenied("Only sellers can create products!")  # Remove 'permissions.'
    
    serializer.save(seller=self.request.user)