from celery import shared_task
import requests
from datetime import datetime

def log_report(customers, orders, revenue):
    with open('/tmp/crm_report_log.txt', 'a') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report: {customers} customers, {orders} orders, {revenue} revenue\n")

@shared_task
def generate_crm_report():
    query = """
    query {
        customersCount
        ordersCount
        totalRevenue
    }
    """

    response = requests.post(
        'http://localhost:8000/graphql',
        json={'query': query}
    )

    if response.status_code == 200:
        data = response.json().get('data', {})
        customers = data.get('customersCount', 0)
        orders = data.get('ordersCount', 0)
        revenue = data.get('totalRevenue', 0)
        log_report(customers, orders, revenue)
    else:
        print(f"Failed to fetch CRM report: {response.status_code}")
