"""
Deposit & Withdrawal Views
HTTPOnly Cookie-based Token Authentication
"""

import random
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import AdminWallet, Transaction, PaymentMethod, Notification
from .email_service import send_admin_payment_intent_notification


# ============================================================
# DEPOSIT VIEWS
# ============================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def get_deposit_options(request):
    """
    Get all active admin wallets (deposit payment methods).
    Public endpoint - no auth required.
    """
    wallets = AdminWallet.objects.filter(is_active=True)

    wallet_list = []
    for w in wallets:
        qr_code_url = None
        if w.qr_code:
            try:
                qr_code_url = w.qr_code.url
            except Exception:
                qr_code_url = None

        wallet_list.append({
            "id": w.id,
            "currency": w.currency,
            "currency_display": w.get_currency_display(),
            "amount": str(w.amount),
            "wallet_address": w.wallet_address,
            "qr_code_url": qr_code_url,
            "is_active": w.is_active,
        })

    return Response({
        "success": True,
        "wallets": wallet_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_deposit(request):
    """
    Create a new deposit transaction.
    Does NOT touch user balance - admin will approve later.
    """
    user = request.user
    currency = request.data.get("currency")
    dollar_amount = request.data.get("dollar_amount")
    currency_unit = request.data.get("currency_unit", "0")
    receipt = request.FILES.get("receipt")

    if not currency or not dollar_amount:
        return Response({
            "success": False,
            "error": "Currency and amount are required.",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = float(dollar_amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return Response({
            "success": False,
            "error": "Please enter a valid amount.",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create transaction (status=pending, balance NOT touched)
    reference = f"DEP-{random.randint(100000, 999999)}-{user.id}"

    transaction = Transaction.objects.create(
        user=user,
        transaction_type="deposit",
        amount=amount,
        currency=currency,
        unit=float(currency_unit) if currency_unit else 0,
        status="pending",
        reference=reference,
        description=f"Deposit of ${amount} via {currency}",
        receipt=receipt,
    )

    # Create notification
    Notification.objects.create(
        user=user,
        type="deposit",
        title="Deposit Request Submitted",
        message=f"Your deposit of ${amount:.2f} via {currency} is pending approval.",
        full_details=f"Deposit reference: {reference}. Amount: ${amount:.2f}. Currency: {currency}. Unit: {currency_unit}. This deposit is pending admin approval.",
        metadata={
            "amount": str(amount),
            "currency": currency,
            "reference": reference,
        },
    )

    return Response({
        "success": True,
        "message": "Deposit request submitted successfully!",
        "transaction": {
            "id": transaction.id,
            "reference": transaction.reference,
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status,
            "created_at": transaction.created_at.isoformat(),
        },
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deposit_payment_intent(request):
    """
    Notify admin that a user intends to make a deposit.
    Sends an email so staff can follow up if the deposit is not completed.
    """
    user = request.user
    currency = request.data.get("currency")
    dollar_amount = request.data.get("dollar_amount")
    currency_unit = request.data.get("currency_unit", "0")

    if not currency or not dollar_amount:
        return Response({
            "success": False,
            "error": "Currency and amount are required.",
        }, status=status.HTTP_400_BAD_REQUEST)

    send_admin_payment_intent_notification(user, currency, dollar_amount, currency_unit)

    return Response({
        "success": True,
        "message": "Payment intent recorded.",
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_deposit_history(request):
    """Get user's deposit transaction history."""
    user = request.user
    limit = int(request.GET.get("limit", 10))

    transactions = Transaction.objects.filter(
        user=user,
        transaction_type="deposit",
    ).order_by("-created_at")[:limit]

    transaction_list = []
    for t in transactions:
        receipt_url = None
        if t.receipt:
            try:
                receipt_url = t.receipt.url
            except Exception:
                receipt_url = None

        transaction_list.append({
            "id": t.id,
            "reference": t.reference,
            "transaction_type": t.transaction_type,
            "transaction_type_display": t.get_transaction_type_display(),
            "amount": str(t.amount),
            "currency": t.currency,
            "unit": str(t.unit),
            "status": t.status,
            "status_display": t.get_status_display(),
            "created_at": t.created_at.isoformat(),
            "receipt_url": receipt_url,
        })

    return Response({
        "success": True,
        "transactions": transaction_list,
    })


# ============================================================
# WITHDRAWAL VIEWS
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_withdrawal_profile(request):
    """Get user profile info for withdrawal page."""
    user = request.user

    return Response({
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
            "account_id": user.account_id or "",
            "balance": str(user.balance),
            "formatted_balance": f"${user.balance:,.2f}",
            "is_verified": user.is_verified,
        },
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_withdrawal_methods(request):
    """Get user's saved payment/withdrawal methods."""
    user = request.user

    methods = PaymentMethod.objects.filter(user=user)

    method_list = []
    for m in methods:
        # Determine address based on method type
        address = ""
        if m.method_type in ("ETH", "BTC", "SOL", "USDT_ERC20", "USDT_TRC20"):
            address = m.address or ""
        elif m.method_type == "BANK":
            address = m.bank_account_number or ""
        elif m.method_type == "CASHAPP":
            address = m.cashapp_id or ""
        elif m.method_type == "PAYPAL":
            address = m.paypal_email or ""

        method_list.append({
            "id": m.id,
            "method_type": m.method_type,
            "display_name": m.get_method_type_display(),
            "address": address,
        })

    return Response({
        "success": True,
        "methods": method_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_withdrawal(request):
    """
    Create a new withdrawal transaction.
    Does NOT touch user balance - admin will approve later.
    """
    user = request.user
    method_type = request.data.get("method_type")
    amount = request.data.get("amount")
    withdrawal_address = request.data.get("withdrawal_address", "")

    if not method_type or not amount:
        return Response({
            "success": False,
            "error": "Method and amount are required.",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return Response({
            "success": False,
            "error": "Please enter a valid amount.",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check balance
    if amount_val > float(user.balance):
        return Response({
            "success": False,
            "error": f"Insufficient balance. Your balance is ${user.balance:,.2f}",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create transaction (status=pending, balance NOT touched)
    reference = f"WDR-{random.randint(100000, 999999)}-{user.id}"

    transaction = Transaction.objects.create(
        user=user,
        transaction_type="withdrawal",
        amount=amount_val,
        currency=method_type,
        status="pending",
        reference=reference,
        description=f"Withdrawal of ${amount_val} via {method_type} to {withdrawal_address}",
    )

    # Create notification
    Notification.objects.create(
        user=user,
        type="withdrawal",
        title="Withdrawal Request Submitted",
        message=f"Your withdrawal of ${amount_val:.2f} via {method_type} is pending approval.",
        full_details=f"Withdrawal reference: {reference}. Amount: ${amount_val:.2f}. Method: {method_type}. Address: {withdrawal_address}. This withdrawal is pending admin approval.",
        metadata={
            "amount": str(amount_val),
            "method": method_type,
            "reference": reference,
            "address": withdrawal_address,
        },
    )

    return Response({
        "success": True,
        "message": "Withdrawal request submitted successfully!",
        "transaction": {
            "id": transaction.id,
            "reference": transaction.reference,
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status,
            "new_balance": str(user.balance),
            "formatted_new_balance": f"${user.balance:,.2f}",
            "created_at": transaction.created_at.isoformat(),
        },
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_withdrawal_history(request):
    """Get user's withdrawal transaction history."""
    user = request.user
    limit = int(request.GET.get("limit", 10))

    transactions = Transaction.objects.filter(
        user=user,
        transaction_type="withdrawal",
    ).order_by("-created_at")[:limit]

    transaction_list = []
    for t in transactions:
        transaction_list.append({
            "id": t.id,
            "reference": t.reference,
            "transaction_type": t.transaction_type,
            "transaction_type_display": t.get_transaction_type_display(),
            "amount": str(t.amount),
            "currency": t.currency,
            "unit": str(t.unit),
            "status": t.status,
            "status_display": t.get_status_display(),
            "created_at": t.created_at.isoformat(),
        })

    return Response({
        "success": True,
        "transactions": transaction_list,
    })


# ============================================================
# COMBINED TRANSACTION HISTORY
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_transaction_history(request):
    """Get all user transactions (both deposits and withdrawals)."""
    user = request.user
    limit = int(request.GET.get("limit", 20))
    tx_type = request.GET.get("type", "all")

    transactions = Transaction.objects.filter(user=user)

    if tx_type == "deposit":
        transactions = transactions.filter(transaction_type="deposit")
    elif tx_type == "withdrawal":
        transactions = transactions.filter(transaction_type="withdrawal")

    transactions = transactions.order_by("-created_at")[:limit]

    transaction_list = []
    for t in transactions:
        receipt_url = None
        if t.receipt:
            try:
                receipt_url = t.receipt.url
            except Exception:
                receipt_url = None

        transaction_list.append({
            "id": t.id,
            "reference": t.reference,
            "transaction_type": t.transaction_type,
            "transaction_type_display": t.get_transaction_type_display(),
            "amount": str(t.amount),
            "currency": t.currency,
            "unit": str(t.unit),
            "status": t.status,
            "status_display": t.get_status_display(),
            "created_at": t.created_at.isoformat(),
            "receipt_url": receipt_url,
        })

    return Response({
        "success": True,
        "transactions": transaction_list,
    })
