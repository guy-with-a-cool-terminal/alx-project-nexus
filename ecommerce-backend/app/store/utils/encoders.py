import json
from cloudinary import CloudinaryResource

class CloudinaryAwareEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, CloudinaryResource):
            return str(obj)
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

from rest_framework.utils.encoders import JSONEncoder as DRFEncoder

class DRFCloudinaryEncoder(DRFEncoder):
    """DRF-specific version that handles CloudinaryResource"""
    def default(self, obj):
        if isinstance(obj, CloudinaryResource):
            return str(obj)
        return super().default(obj)

# Replace DRF's default encoder with our patched version
import rest_framework.utils.encoders
rest_framework.utils.encoders.JSONEncoder = DRFCloudinaryEncoder
