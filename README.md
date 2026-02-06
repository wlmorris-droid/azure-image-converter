# Azure Image Converter Function

This Azure Function processes album art images (JPEG or PNG) and returns them as PNG format. It also calculates the dominant color from the image and includes it in the response header for UI theming (similar to Sonos app).

## Security Features

- **Authentication Required**: Function key authentication is enforced
- **HTTPS Only**: All requests must use HTTPS
- **Input Validation**: URL validation and image format verification
- **Size Limits**: Maximum image size of 10MB
- **Content Type Validation**: Only image content types accepted
- **Security Headers**: XSS protection, content type options, and frame options headers

## Features

- Accepts JPEG and PNG images
- Converts JPEG to PNG; returns PNG as-is
- **Automatically resizes images**: If either width or height exceeds 400px, proportionally scales down until the larger dimension reaches 400px
- Calculates a complementary background color from album art (heavily desaturated, darker, muted tones like deep grey, dark brown, or charcoal)
- Returns background color in `X-Background-Color` header (hex format, e.g., #RRGGBB)

## Security & Secrets Management

⚠️ **Important**: Never commit secrets, API keys, or sensitive data to version control.

### Best Practices:
- Use environment variables for sensitive configuration
- Store secrets in Azure Key Vault for production
- Use function keys for authentication (automatically managed by Azure)
- Keep `local.settings.json` out of version control (already in .gitignore)

### Environment Variables:
Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

### Getting Function Keys:
After deployment, retrieve your function key securely:
```bash
az functionapp function keys list --name myfunctionapp --resource-group myResourceGroup --function-name ConvertImageFunction
```

Or use the Azure Portal: Function App → Functions → ConvertImageFunction → Function Keys

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
   
   **Note**: Authentication is not required when running locally, but is enforced in production (see deployment section above).

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
   az functionapp create --resource-group myResourceGroup --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4 --name myfunctionapp --storage-account mystorageaccount --os-type Linux
   ```

5. Deploy the function:
   ```
   func azure functionapp publish myfunctionapp
   ```

**Note**: Never commit function keys, connection strings, or other secrets to version control. Use environment variables or Azure Key Vault for sensitive data.

## Usage

Send a GET request to the function URL with a `url` parameter containing the image URL and include the function key.

### Getting the Function Key

After deployment, get the function key:
```
az functionapp function keys list --name myfunctionapp --resource-group myResourceGroup --function-name ConvertImageFunction
```

Or in the Azure Portal: Function App → Functions → ConvertImageFunction → Function Keys

### Example Request

```
GET https://myfunctionapp.azurewebsites.net/api/ConvertImageFunction?url=https://example.com/album-art.jpg&code=YOUR_FUNCTION_KEY
```

### cURL Example

```bash
curl "https://myfunctionapp.azurewebsites.net/api/ConvertImageFunction?url=https://example.com/album-art.jpg&code=YOUR_FUNCTION_KEY"
```

The response will be the PNG image data with a custom header containing the dominant color.

**Response Headers:**
- `X-Background-Color`: Hex color code (e.g., `#4A4A4A`) representing a heavily muted, darker background color derived from the album art
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY
- `X-XSS-Protection`: 1; mode=block