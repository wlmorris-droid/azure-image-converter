import azure.functions as func
from PIL import Image
import requests
from io import BytesIO

def main(req: func.HttpRequest) -> func.HttpResponse:
    image_url = req.params.get('url')
    if not image_url:
        return func.HttpResponse("Missing 'url' parameter", status_code=400)
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        png_buffer = BytesIO()
        image.save(png_buffer, format='PNG')
        png_buffer.seek(0)
        return func.HttpResponse(png_buffer.getvalue(), mimetype='image/png')
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)