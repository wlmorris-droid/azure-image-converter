# Azure Image Converter Function

This Azure Function processes album art images (JPEG or PNG) and returns them as PNG format. It also calculates the dominant color from the image and includes it in the response header for UI theming (similar to Sonos app).

## Features

- Accepts JPEG and PNG images
- Converts JPEG to PNG; returns PNG as-is
- Calculates a complementary background color from album art (desaturated, mood-based tones like grey, brown, or burnt orange)
- Returns background color in `X-Background-Color` header (hex format, e.g., #RRGGBB)

## Prerequisites

- Azure CLI installed
- Azure Functions Core Tools installed
- Python 3.11 or later

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the function locally:
   ```
   func start
   ```

3. Test the function:
   ```
   curl "http://localhost:7071/api/ConvertImageFunction?url=https://example.com/image.jpg"
   ```

## Deployment

1. Login to Azure:
   ```
   az login
   ```

2. Create a resource group:
   ```
   az group create --name myResourceGroup --location eastus
   ```

3. Create a storage account:
   ```
   az storage account create --name mystorageaccount --location eastus --resource-group myResourceGroup --sku Standard_LRS
   ```

4. Create the function app:
   ```
   az functionapp create --resource-group myResourceGroup --consumption-plan-location eastus --runtime python --runtime-version 3.8 --functions-version 4 --name myfunctionapp --storage-account mystorageaccount
   ```

5. Deploy the function:
   ```
   func azure functionapp publish myfunctionapp
   ```

## Usage

Send a GET or POST request to the function URL with a `url` parameter containing the image URL.

Example:
```
GET https://image-converter-func.azurewebsites.net/api/convertimagefunction?url=https://example.com/album-art.jpg
```

The response will be the PNG image data with a custom header containing the dominant color.

**Response Headers:**
- `X-Background-Color`: Hex color code (e.g., `#8B7355`) representing a complementary background color derived from the album art, adjusted for subtle, mood-based theming