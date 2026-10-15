from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Count, F, Q
from django.db.models.functions import (
    TruncDay,
    TruncWeek,
    TruncMonth,
    TruncYear,
)
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from purchases.models import Purchase, SupplierReturn
from inventory.models import StockMovement
from sales.models import Sale, SaleItem
from product.models import Product
from payments.models import Payment
from purchases.permissions import IsAdminOrManager

from .serializers import (
    ReportFilterSerializer,
    SalesTrendSerializer,
    ProductPerformanceSerializer,
    InventoryReportSerializer,
    PaymentMethodReportSerializer,
)


def get_report_range(request):
    """
    Date range না দিলে period অনুযায়ী সাম্প্রতিক সময়ের রিপোর্ট:
    daily   -> গত 30 দিন
    weekly  -> গত 12 সপ্তাহ
    monthly -> গত 12 মাস
    yearly  -> গত 5 বছর
    """
    serializer = ReportFilterSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    today = timezone.localdate()
    period = data.get("period", "monthly")

    if data.get("start_date") and data.get("end_date"):
        start_date = data["start_date"]
        end_date = data["end_date"]
    elif period == "daily":
        start_date = today - timedelta(days=29)
        end_date = today
    elif period == "weekly":
        start_date = today - timedelta(weeks=11)
        end_date = today
    elif period == "monthly":
        start_date = today - timedelta(days=365)
        end_date = today
    else:
        start_date = today.replace(year=today.year - 4)
        end_date = today

    return period, start_date, end_date


def completed_sales(start_date, end_date):
    return Sale.objects.filter(
        status="completed",
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    )


def get_sales_summary(start_date, end_date):
    sales = completed_sales(start_date, end_date)

    totals = sales.aggregate(
        invoice_count=Count("id"),
        sales_amount=Sum("final_amount"),
        discount_amount=Sum("discount_amount"),
        tax_amount=Sum("tax_amount"),
    )

    sales_amount = totals["sales_amount"] or Decimal("0.00")

    paid_total = (
        Payment.objects.filter(sale__in=sales)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "invoice_count": totals["invoice_count"] or 0,
        "sales_amount": sales_amount,
        "discount_amount": totals["discount_amount"] or Decimal("0.00"),
        "tax_amount": totals["tax_amount"] or Decimal("0.00"),
        "paid_total": paid_total,
        "remaining_due": max(sales_amount - paid_total, Decimal("0.00")),
    }


class ReportViewSet(ViewSet):
    permission_classes = [IsAdminOrManager]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        periods = {
            "today": (today, today),
            "this_week": (week_start, today),
            "this_month": (month_start, today),
            "this_year": (year_start, today),
        }

        result = {
            name: get_sales_summary(start, end)
            for name, (start, end) in periods.items()
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def sales(self, request):
        period, start_date, end_date = get_report_range(request)
        sales = completed_sales(start_date, end_date)

        truncation = {
            "daily": TruncDay,
            "weekly": TruncWeek,
            "monthly": TruncMonth,
            "yearly": TruncYear,
        }[period]

        rows = (
            sales.annotate(period_start=truncation("created_at"))
            .values("period_start")
            .annotate(
                invoice_count=Count("id"),
                sales_amount=Sum("final_amount"),
            )
            .order_by("period_start")
        )

        return Response({
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "results": SalesTrendSerializer(rows, many=True).data,
        })

    @action(detail=False, methods=["get"])
    def products(self, request):
        period, start_date, end_date = get_report_range(request)

        rows = (
            SaleItem.objects.filter(
                sale__status="completed",
                sale__created_at__date__gte=start_date,
                sale__created_at__date__lte=end_date,
            )
            .values(
                "product_id",
                product_name=F("product__name"),
                sku=F("product__sku"),
                category_name=F("product__category__name"),
            )
            .annotate(
                quantity_sold=Sum("quantity"),
                sales_amount=Sum("subtotal"),
                invoice_count=Count("sale_id", distinct=True),
            )
            .order_by("-quantity_sold", "-sales_amount")
        )

        return Response({
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "results": ProductPerformanceSerializer(rows, many=True).data,
        })

    @action(detail=False, methods=["get"], url_path="products/top-selling")
    def top_selling(self, request):
        period, start_date, end_date = get_report_range(request)

        rows = (
            SaleItem.objects.filter(
                sale__status="completed",
                sale__created_at__date__gte=start_date,
                sale__created_at__date__lte=end_date,
            )
            .values(
                "product_id",
                product_name=F("product__name"),
                sku=F("product__sku"),
                category_name=F("product__category__name"),
            )
            .annotate(
                quantity_sold=Sum("quantity"),
                sales_amount=Sum("subtotal"),
                invoice_count=Count("sale_id", distinct=True),
            )
            .order_by("-quantity_sold", "-sales_amount")[:10]
        )

        return Response({
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "results": ProductPerformanceSerializer(rows, many=True).data,
        })

    @action(detail=False, methods=["get"])
    def inventory(self, request):
        products = Product.objects.select_related("category").annotate(
            stock_status=F("stock")
        ).order_by("name")

        rows = []
        for product in products:
            if product.stock <= 0:
                stock_status = "out_of_stock"
            elif product.stock <= product.low_stock_threshold:
                stock_status = "low_stock"
            else:
                stock_status = "in_stock"

            rows.append({
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "category_name": (
                    product.category.name if product.category else None
                ),
                "stock": product.stock,
                "low_stock_threshold": product.low_stock_threshold,
                "cost_price": product.cost_price,
                "selling_price": product.selling_price,
                "stock_status": stock_status,
            })

        return Response({
            "total_products": len(rows),
            "out_of_stock": sum(
                item["stock_status"] == "out_of_stock" for item in rows
            ),
            "low_stock": sum(
                item["stock_status"] == "low_stock" for item in rows
            ),
            "results": InventoryReportSerializer(rows, many=True).data,
        })

    @action(detail=False, methods=["get"])
    def payments(self, request):
        period, start_date, end_date = get_report_range(request)

        rows = (
            Payment.objects.filter(
                sale__status="completed",
                paid_at__date__gte=start_date,
                paid_at__date__lte=end_date,
            )
            .values("method")
            .annotate(
                payment_count=Count("id"),
                total_amount=Sum("amount"),
            )
            .order_by("method")
        )

        return Response({
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "results": PaymentMethodReportSerializer(rows, many=True).data,
        })

    @action(detail=False, methods=["get"])
    def purchases(self, request):
        period, start_date, end_date = get_report_range(request)

        purchases = Purchase.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )

        returns = SupplierReturn.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )

        purchase_total = (
            purchases.aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0.00")
        )
        return_total = (
            returns.aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0.00")
        )

        return Response({
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "purchase_count": purchases.count(),
            "purchase_amount": purchase_total,
            "supplier_return_count": returns.count(),
            "supplier_return_amount": return_total,
            "net_purchase_amount": purchase_total - return_total,
        })

    @action(detail=False, methods=["get"], url_path="stock-movements")
    def stock_movements(self, request):
        period, start_date, end_date = get_report_range(request)

        movements = StockMovement.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )

        rows = (
            movements.values("movement_type")
            .annotate(
                movement_count=Count("id"),
                total_quantity=Sum("quantity"),
            )
            .order_by("movement_type")
        )

        return Response({
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "results": list(rows),
        })