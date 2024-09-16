from rest_framework import serializers

import re

def RequestMethodValidator(value):
    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
    allowed_methods = [method.upper() for method in allowed_methods]
    
    if value.upper() not in allowed_methods:
        raise serializers.ValidationError(f"{value} is not a valid request method")
    return True


def validate_url(url):
    # Regular expression pattern for URL validation
    pattern = re.compile(
        r'^(https?://)?'  # optional http or https scheme
        r'([a-zA-Z0-9-_]+\.)+[a-zA-Z]{2,6}'  # domain name
        r'(:\d{1,5})?'  # optional port
        r'(/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?$'  # path and query string
    )

    if pattern.match(url):
        return True
    else:
        return False


def validate_single_word(value):
    # Regular expression to check if the string contains only alphabetic characters and is a single word
    if re.match(r'^[A-Za-z]+$', value):
        return True
    return False

def validateListOfObjects(value):
        # Check if the value is a list
        if not isinstance(value, list):
            raise serializers.ValidationError("the value must be a list of objects")
        
        # Check if each item in the list is a dictionary
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("the dictionary/object inside the list is not set in a proper way or does not exist at all.")
                

        return True
    
