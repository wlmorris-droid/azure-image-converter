import azure.functions as func
from PIL import Image
import requests
from io import BytesIO
from collections import Counter
import colorsys
import urllib.parse
import mimetypes

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Validate request method
    if req.method != 'GET':
        return func.HttpResponse("Method not allowed", status_code=405)
    
    image_url = req.params.get('url')
    if not image_url:
        return func.HttpResponse("Missing 'url' parameter", status_code=400)
    
    # Get optional size parameter
    size_param = req.params.get('size')
    max_size = 320  # default
    if size_param:
        try:
            max_size = int(size_param)
            if max_size <= 0 or max_size > 2000:  # reasonable limits
                return func.HttpResponse("Invalid 'size' parameter (must be 1-2000)", status_code=400)
        except ValueError:
            return func.HttpResponse("Invalid 'size' parameter (must be integer)", status_code=400)
    
    # Validate URL format
    try:
        parsed_url = urllib.parse.urlparse(image_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return func.HttpResponse("Invalid URL format", status_code=400)
        if parsed_url.scheme.lower() not in ['http', 'https']:
            return func.HttpResponse("Only HTTP and HTTPS URLs are allowed", status_code=400)
    except Exception:
        return func.HttpResponse("Invalid URL", status_code=400)
    
    try:
        # Add headers for security and identification
        headers = {
            'User-Agent': 'Azure-Function-Image-Converter/1.0'
        }
        
        response = requests.get(image_url, timeout=10, headers=headers, stream=True)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            return func.HttpResponse("URL does not point to an image", status_code=400)
        
        # Check content length (limit to 10MB)
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 10 * 1024 * 1024:
            return func.HttpResponse("Image too large (max 10MB)", status_code=413)
        
        # Read image data with size limit
        image_data = b''
        for chunk in response.iter_content(chunk_size=8192):
            image_data += chunk
            if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
                return func.HttpResponse("Image too large (max 10MB)", status_code=413)
        
        # Validate image
        try:
            image = Image.open(BytesIO(image_data))
            image.verify()  # Verify it's a valid image
            image.close()
            image = Image.open(BytesIO(image_data))  # Reopen after verify
        except Exception:
            return func.HttpResponse("Invalid image file", status_code=400)
        
        # Resize image if necessary (max dimension should be max_size px)
        image = resize_image_to_max(image, max_size)
        
        # Calculate background color based on dominant color
        background_color = get_background_color(image)
        color_hex = f"#{background_color[0]:02x}{background_color[1]:02x}{background_color[2]:02x}"
        
        # Convert resized image to PNG
        png_buffer = BytesIO()
        image.save(png_buffer, format='PNG')
        png_buffer.seek(0)
        return func.HttpResponse(png_buffer.getvalue(), mimetype='image/png', headers={'X-Background-Color': color_hex})
    except requests.exceptions.RequestException as e:
        return func.HttpResponse("Failed to fetch image", status_code=400)
    except Exception as e:
        # Log the error but don't expose details
        return func.HttpResponse("Internal server error", status_code=500)

def get_background_color(image):
    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize to 100x100 for faster processing
    image = image.resize((100, 100))
    
    # Get pixels
    pixels = list(image.getdata())
    
    # Find most common color
    most_common = Counter(pixels).most_common(1)[0][0]
    
    # Convert RGB to HSL
    r, g, b = [x / 255.0 for x in most_common]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    # Adjust for background: reduce saturation to 90%, make darker and more muted
    s = min(s * 0.9, 0.9)  # Reduce saturation to 90% for muting
    l = max(min(l * 0.5 + 0.05, 0.25), 0.05)  # Lower lightness range for darker tones
    
    # Convert back to RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def resize_image_to_max(image, max_dimension):
    """
    Resize image proportionally so that the maximum dimension is max_dimension px.
    If both dimensions are already <= max_dimension, return the original image.
    """
    width, height = image.size
    
    # Check if resizing is needed
    if max(width, height) <= max_dimension:
        return image
    
    # Calculate scale factor
    scale_factor = max_dimension / max(width, height)
    
    # Calculate new dimensions
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    # Ensure minimum size of 1 pixel
    new_width = max(1, new_width)
    new_height = max(1, new_height)
    
    # Resize the image using high-quality resampling
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return resized_image