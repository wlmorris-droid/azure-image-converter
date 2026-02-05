import azure.functions as func
from PIL import Image
import requests
from io import BytesIO
from collections import Counter
import colorsys

def main(req: func.HttpRequest) -> func.HttpResponse:
    image_url = req.params.get('url')
    if not image_url:
        return func.HttpResponse("Missing 'url' parameter", status_code=400)
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        
        # Calculate background color based on dominant color
        background_color = get_background_color(image)
        color_hex = f"#{background_color[0]:02x}{background_color[1]:02x}{background_color[2]:02x}"
        
        # Check if already PNG
        if image.format == 'PNG':
            return func.HttpResponse(image_data, mimetype='image/png', headers={'X-Background-Color': color_hex})
        else:
            # Convert to PNG
            png_buffer = BytesIO()
            image.save(png_buffer, format='PNG')
            png_buffer.seek(0)
            return func.HttpResponse(png_buffer.getvalue(), mimetype='image/png', headers={'X-Background-Color': color_hex})
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

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
    
    # Adjust for background: heavily reduce saturation, make darker and more muted
    s = min(s * 0.2, 0.3)  # Heavily reduce saturation for muting
    l = max(min(l * 0.6 + 0.15, 0.4), 0.2)  # Lower lightness range for darker tones
    
    # Convert back to RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))