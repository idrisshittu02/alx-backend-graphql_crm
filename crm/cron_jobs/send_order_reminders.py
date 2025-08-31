import requests
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Define the GraphQL query
query = gql("""
query ($startDate: String!, $endDate: String!) {
  orders(orderDate_Gte: $startDate, orderDate_Lte: $endDate) {
    id
    customer {
      email
    }
  }
}
""")

# Calculate the date range for the last 7 days
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

# Set up the GraphQL client
transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
client = Client(transport=transport, fetch_schema_from_transport=True)

# Execute the query
params = {"startDate": start_date, "endDate": end_date}
response = client.execute(query, variable_values=params)

# Log the orders
with open('/tmp/order_reminders_log.txt', 'a') as log_file:
    for order in response.get('orders', []):
        order_id = order['id']
        customer_email = order['customer']['email']
        log_file.write(f"{datetime.now()} - Order ID: {order_id}, Customer Email: {customer_email}\n")

print("Order reminders processed!")
