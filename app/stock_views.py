from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.utils.crypto import get_random_string
from .models import Stock, UserStockPosition, TradeHistory, Notification


@api_view(["GET"])
@permission_classes([AllowAny])
def list_stocks(request):
    """
    List all stocks with optional featured filter
    """
    featured = request.GET.get('featured', '').lower() == 'true'

    if featured:
        stocks = Stock.objects.filter(is_active=True, is_featured=True).order_by('symbol')
    else:
        stocks = Stock.objects.filter(is_active=True).order_by('-is_featured', 'symbol')

    stocks_list = []
    for stock in stocks:
        stocks_list.append({
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "logo_url": stock.logo_url,
            "price": str(stock.price),
            "change": str(stock.change),
            "change_percent": str(stock.change_percent),
            "is_positive_change": stock.is_positive_change,
            "is_featured": stock.is_featured,
        })

    return Response({
        "success": True,
        "stocks": stocks_list,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_detail(request, symbol):
    """
    Get stock details and user's position if they own it
    """
    user = request.user

    try:
        stock = Stock.objects.get(symbol=symbol.upper(), is_active=True)
    except Stock.DoesNotExist:
        return Response({
            "success": False,
            "error": "Stock not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Get user's position if exists
    user_position = None
    try:
        position = UserStockPosition.objects.get(user=user, stock=stock, is_active=True)
        user_position = {
            "id": position.id,
            "shares": str(position.shares),
            "average_buy_price": str(position.average_buy_price),
            "total_invested": str(position.total_invested),
            "current_value": str(position.current_value),
            "profit_loss": str(position.profit_loss),
            "profit_loss_percent": str(position.profit_loss_percent),
        }
    except UserStockPosition.DoesNotExist:
        pass

    return Response({
        "success": True,
        "stock": {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "logo_url": stock.logo_url,
            "price": str(stock.price),
            "change": str(stock.change),
            "change_percent": str(stock.change_percent),
            "volume": stock.volume,
            "market_cap": stock.market_cap,
            "formatted_market_cap": stock.formatted_market_cap,
            "sector": stock.sector,
            "is_positive_change": stock.is_positive_change,
        },
        "user_position": user_position,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def buy_stock(request):
    """
    Buy stock shares
    """
    user = request.user
    symbol = request.data.get('symbol', '').strip().upper()
    shares = request.data.get('shares', '0')

    # Validate inputs
    try:
        shares = Decimal(shares)
        if shares <= 0:
            return Response({
                "success": False,
                "error": "Shares must be greater than 0"
            }, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({
            "success": False,
            "error": "Invalid shares amount"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get stock
    try:
        stock = Stock.objects.get(symbol=symbol, is_active=True)
    except Stock.DoesNotExist:
        return Response({
            "success": False,
            "error": "Stock not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Calculate total cost
    total_cost = shares * stock.price

    # Check user balance
    if user.balance < total_cost:
        return Response({
            "success": False,
            "error": f"Insufficient balance. You need ${total_cost} but only have ${user.balance}",
            "required": str(total_cost),
            "current_balance": str(user.balance),
        }, status=status.HTTP_400_BAD_REQUEST)

    # Deduct from balance
    user.balance -= total_cost
    user.save(update_fields=['balance'])

    # Get or create position
    position, created = UserStockPosition.objects.get_or_create(
        user=user,
        stock=stock,
        is_active=True,
        defaults={
            'shares': shares,
            'average_buy_price': stock.price,
            'total_invested': total_cost,
        }
    )

    if not created:
        # Update existing position
        total_shares = position.shares + shares
        total_invested = position.total_invested + total_cost
        position.average_buy_price = total_invested / total_shares
        position.shares = total_shares
        position.total_invested = total_invested
        position.save(update_fields=['shares', 'average_buy_price', 'total_invested'])

    # Create trade history
    reference = f"BUY-{get_random_string(12).upper()}"
    TradeHistory.objects.create(
        user=user,
        stock=stock,
        trade_type='buy',
        shares=shares,
        price_per_share=stock.price,
        total_amount=total_cost,
        reference=reference,
    )

    # Create notification
    Notification.objects.create(
        user=user,
        type="trade",
        title="Stock Purchase Successful",
        message=f"You bought {shares} shares of {stock.symbol} for ${total_cost}",
        full_details=f"Your purchase of {shares} shares of {stock.name} ({stock.symbol}) at ${stock.price} per share has been completed. Total cost: ${total_cost}. Reference: {reference}",
        metadata={
            "stock": stock.symbol,
            "amount": f"${total_cost}",
            "shares": str(shares),
            "reference": reference,
        }
    )

    return Response({
        "success": True,
        "message": f"Successfully bought {shares} shares of {stock.symbol}",
        "reference": reference,
        "new_balance": str(user.balance),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sell_stock(request):
    """
    Sell stock shares
    """
    user = request.user
    symbol = request.data.get('symbol', '').strip().upper()
    shares = request.data.get('shares', '0')

    # Validate inputs
    try:
        shares = Decimal(shares)
        if shares <= 0:
            return Response({
                "success": False,
                "error": "Shares must be greater than 0"
            }, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({
            "success": False,
            "error": "Invalid shares amount"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get stock
    try:
        stock = Stock.objects.get(symbol=symbol, is_active=True)
    except Stock.DoesNotExist:
        return Response({
            "success": False,
            "error": "Stock not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Get user position
    try:
        position = UserStockPosition.objects.get(user=user, stock=stock, is_active=True)
    except UserStockPosition.DoesNotExist:
        return Response({
            "success": False,
            "error": "You don't own any shares of this stock"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if user has enough shares
    if position.shares < shares:
        return Response({
            "success": False,
            "error": f"You only have {position.shares} shares available",
            "available_shares": str(position.shares),
        }, status=status.HTTP_400_BAD_REQUEST)

    # Calculate sale proceeds
    sale_proceeds = shares * stock.price

    # Calculate profit/loss for this sale
    cost_basis = (position.total_invested / position.shares) * shares
    profit_loss = sale_proceeds - cost_basis

    # Add proceeds to balance
    user.balance += sale_proceeds
    user.save(update_fields=['balance'])

    # Update position
    remaining_shares = position.shares - shares
    if remaining_shares == 0:
        # Close position
        position.is_active = False
        position.save(update_fields=['is_active'])
    else:
        # Update position
        remaining_investment = position.total_invested - cost_basis
        position.shares = remaining_shares
        position.total_invested = remaining_investment
        position.save(update_fields=['shares', 'total_invested'])

    # Create trade history
    reference = f"SELL-{get_random_string(12).upper()}"
    TradeHistory.objects.create(
        user=user,
        stock=stock,
        trade_type='sell',
        shares=shares,
        price_per_share=stock.price,
        total_amount=sale_proceeds,
        profit_loss=profit_loss,
        reference=reference,
    )

    # Create notification
    profit_loss_text = f"profit of ${profit_loss}" if profit_loss >= 0 else f"loss of ${abs(profit_loss)}"
    Notification.objects.create(
        user=user,
        type="trade",
        title="Stock Sale Successful",
        message=f"You sold {shares} shares of {stock.symbol} for ${sale_proceeds} ({profit_loss_text})",
        full_details=f"Your sale of {shares} shares of {stock.name} ({stock.symbol}) at ${stock.price} per share has been completed. Sale proceeds: ${sale_proceeds}. {profit_loss_text.capitalize()}. Reference: {reference}",
        metadata={
            "stock": stock.symbol,
            "amount": f"${sale_proceeds}",
            "shares": str(shares),
            "profit_loss": str(profit_loss),
            "reference": reference,
        }
    )

    return Response({
        "success": True,
        "message": f"Successfully sold {shares} shares of {stock.symbol}",
        "reference": reference,
        "sale_proceeds": str(sale_proceeds),
        "profit_loss": str(profit_loss),
        "new_balance": str(user.balance),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_positions(request):
    """
    Get all user's active stock positions
    """
    user = request.user

    positions = UserStockPosition.objects.filter(user=user, is_active=True).select_related('stock')

    positions_list = []
    for position in positions:
        stock = position.stock
        positions_list.append({
            "id": position.id,
            "stock": {
                "symbol": stock.symbol,
                "name": stock.name,
                "logo_url": stock.logo_url,
                "current_price": str(stock.price),
            },
            "shares": str(position.shares),
            "average_buy_price": str(position.average_buy_price),
            "total_invested": str(position.total_invested),
            "current_value": str(position.current_value),
            "profit_loss": str(position.profit_loss),
            "profit_loss_percent": str(position.profit_loss_percent),
            "is_positive": position.profit_loss >= 0,
        })

    return Response({
        "success": True,
        "positions": positions_list,
    })
