#!/bin/bash
# Script to delete customers with no orders in the past year and log the result

cd "$(dirname "${BASH_SOURCE[0]}")/../.."

cwd=$(pwd)

if [ -d "$cwd" ]; then
    count=$(python manage.py shell -c "from crm.models import Customer, Order; from django.utils import timezone; from datetime import timedelta; one_year_ago = timezone.now() - timedelta(days=365); to_delete = Customer.objects.exclude(order__created_at__gte=one_year_ago); deleted, _ = to_delete.delete(); print(deleted)")
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $count inactive customers" >> /tmp/customer_cleanup_log.txt
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to determine working directory" >> /tmp/customer_cleanup_log.txt
fi
