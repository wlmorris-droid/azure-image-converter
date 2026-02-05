# Azure Image Converter Function

This Azure Function converts a progressive JPEG image from a URL to PNG format.

## Prerequisites

- Azure CLI installed
- Azure Functions Core Tools installed
- Python 3.8 or later

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
GET https://myfunctionapp.azurewebsites.net/api/ConvertImageFunction?url=https://example.com/image.jpg
```

The response will be the PNG image data.