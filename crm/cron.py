from datetime import datetime
from crm.models import Product
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Log a CRM heartbeat message and optionally query the GraphQL hello field.
    """
    # Log the heartbeat message
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(f"{datetime.now().strftime('%d/%m/%Y-%H:%M:%S')} CRM is alive\n")

    # Optionally query the GraphQL hello field
    try:
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            verify=True,
            retries=3
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("query { hello }")
        response = client.execute(query)
        print("GraphQL endpoint response:", response)
    except Exception as e:
        print(f"Error querying GraphQL endpoint: {e}")


def updateLowStockProducts():
    """
    Update low stock products by incrementing their stock by 10.
    This function simulates the GraphQL mutation behavior directly.
    """
    try:
        # Query products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        # Increment their stock by 10 (simulating restocking)
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_products.append(f"{product.name} (Stock: {product.stock})")

        # Log updates with a timestamp
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%d/%m/%Y-%H:%M:%S')} - Low stock products updated successfully!\n")
            for product in updated_products:
                log_file.write(f"{product}\n")

        print("Low stock products updated successfully!")
        return {
            'success': 'Low stock products updated successfully!',
            'updated_products': updated_products
        }

    except Exception as e:
        print(f"Error updating low stock products: {e}")
        return {
            'success': f'Error: {str(e)}',
            'updated_products': []
        }
