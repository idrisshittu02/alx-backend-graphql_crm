from datetime import datetime
import graphene
from crm.schema import schema
from crm.models import Product

def update_low_stock_graphql():
    """
    Update low stock products using GraphQL mutation directly.
    This approach uses the GraphQL schema without HTTP requests.
    """
    try:
        # Define the GraphQL mutation
        mutation = """
        mutation {
            updateLowStockProducts {
                success
                updatedProducts
            }
        }
        """
        
        # Execute the mutation directly using the schema
        result = schema.execute(mutation)
        
        if result.errors:
            print(f"GraphQL errors: {result.errors}")
            return {
                'success': f'GraphQL errors: {result.errors}',
                'updated_products': []
            }
        
        data = result.data['updateLowStockProducts']
        
        # Log updated product names and new stock levels to low_stock_updates_log.txt with a timestamp
        with open('low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%d/%m/%Y-%H:%M:%S')} - {data['success']}\n")
            for product in data['updatedProducts']:
                log_file.write(f"{product}\n")

        print("Low stock products updated successfully via GraphQL!")
        return data
        
    except Exception as e:
        print(f"Error updating low stock products: {e}")
        return {
            'success': f'Error: {str(e)}',
            'updated_products': []
        }

def update_low_stock():
    """
    Main function that can be called by cron.
    Uses the direct GraphQL approach.
    """
    return update_low_stock_graphql() 