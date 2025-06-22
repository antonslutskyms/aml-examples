import os
from sp_api.api import ListingsItem
from sp_api.base import Marketplaces, SellingApiException


def create_listing(sku: str, listing_data: dict, marketplace: Marketplaces = Marketplaces.US):
    """Create or update an Amazon listing for the given SKU.

    Parameters
    ----------
    sku : str
        The stock keeping unit for the product.
    listing_data : dict
        Listing attributes as defined by Amazon's Selling Partner API.
    marketplace : Marketplaces, optional
        Target marketplace, by default Marketplaces.US
    """
    credentials = {
        "refresh_token": os.environ.get("SP_API_REFRESH_TOKEN"),
        "lwa_app_id": os.environ.get("SP_API_CLIENT_ID"),
        "lwa_client_secret": os.environ.get("SP_API_CLIENT_SECRET"),
        "aws_access_key": os.environ.get("SP_API_AWS_ACCESS_KEY"),
        "aws_secret_key": os.environ.get("SP_API_AWS_SECRET_KEY"),
        "role_arn": os.environ.get("SP_API_ROLE_ARN"),
    }

    try:
        listings_api = ListingsItem(marketplace=marketplace, credentials=credentials)
        result = listings_api.put_listings_item(sku=sku, body=listing_data)
        print("Listing created", result.payload)
    except SellingApiException as exc:
        print(f"Failed to create listing: {exc}")


def example_usage():
    sku = "TESTSKU001"
    listing_data = {
        "productType": "PRODUCT",
        "requirements": "LISTING",
        "attributes": {
            "merchantShippingGroupName": ["MyShipping"],
            "itemName": ["Example Product"],
            "brand": ["DemoBrand"],
        },
    }

    create_listing(sku, listing_data)


if __name__ == "__main__":
    example_usage()
