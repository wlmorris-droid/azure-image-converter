import azure.functions as func
from PIL import Image
import requests
from io import BytesIO
from collections import Counter

def main(req: func.HttpRequest) -> func.HttpResponse:
    image_url = req.params.get('url')
    if not image_url:
        return func.HttpResponse("Missing 'url' parameter", status_code=400)
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        
        # Calculate dominant color
        dominant_color = get_dominant_color(image)
        color_hex = f"#{dominant_color[0]:02x}{dominant_color[1]:02x}{dominant_color[2]:02x}"
        
        # Check if already PNG
        if image.format == 'PNG':
            return func.HttpResponse(image_data, mimetype='image/png', headers={'X-Dominant-Color': color_hex})
        else:
            # Convert to PNG
            png_buffer = BytesIO()
            image.save(png_buffer, format='PNG')
            png_buffer.seek(0)
            return func.HttpResponse(png_buffer.getvalue(), mimetype='image/png', headers={'X-Dominant-Color': color_hex})
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

def get_dominant_color(image):
    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize to 100x100 for faster processing
    image = image.resize((100, 100))
    
    # Get pixels
    pixels = list(image.getdata())
    
    # Find most common color
    most_common = Counter(pixels).most_common(1)[0][0]
    
    return most_common