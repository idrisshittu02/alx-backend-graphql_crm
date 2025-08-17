import graphene
from graphene_django import DjangoObjectType
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphene_django.filter import DjangoFilterConnectionField


# ==== TYPES ====
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter



# ==== INPUT TYPES ====
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False, default_value=0)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# ==== MUTATIONS ====
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        # Optional phone validation
        if input.phone:
            validator = RegexValidator(
                regex=r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$',
                message="Phone must be in format +1234567890 or 123-456-7890"
            )
            validator(input.phone)

        customer = Customer(name=input.name, email=input.email, phone=input.phone)
        customer.full_clean()
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, data in enumerate(input, start=1):
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        errors.append(f"Row {idx}: Email already exists")
                        continue

                    if data.phone:
                        validator = RegexValidator(
                            regex=r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$',
                            message="Phone must be in format +1234567890 or 123-456-7890"
                        )
                        validator(data.phone)

                    customer = Customer(name=data.name, email=data.email, phone=data.phone)
                    customer.full_clean()
                    customer.save()
                    created_customers.append(customer)
                except ValidationError as e:
                    errors.append(f"Row {idx}: {e}")
                except Exception as e:
                    errors.append(f"Row {idx}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(name=input.name, price=input.price, stock=input.stock or 0)
        product.full_clean()
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not input.product_ids:
            raise Exception("At least one product must be selected")

        products = Product.objects.filter(id__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise Exception("One or more product IDs are invalid")

        total_amount = products.aggregate(total=Sum('price'))['total'] or 0

        order = Order(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date or timezone.now()
        )
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)


# ==== QUERY & MUTATION ROOT ====
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        return qs.order_by(*order_by) if order_by else qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        return qs.order_by(*order_by) if order_by else qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        return qs.order_by(*order_by) if order_by else qs


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
