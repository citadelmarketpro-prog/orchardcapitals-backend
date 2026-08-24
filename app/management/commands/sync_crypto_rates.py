from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand

from app.models import Stock
from app.fmp_client import get_quotes

# Kept in sync with views.py's _CRYPTO_TO_STOCK mapping.
CRYPTO_SYMBOLS = {
    'BTCUSD': 'Bitcoin',
    'ETHUSD': 'Ethereum',
    'SOLUSD': 'Solana',
    'BNBUSD': 'Binance Coin',
    'XRPUSD': 'XRP',
    'TRXUSD': 'Tron',
}


def _to_decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


class Command(BaseCommand):
    help = (
        "Refresh crypto USD rates from FMP into the Stock table (fast, small "
        "symbol set — used by the deposit modal's live rate lookup). Rows are "
        "created inactive so they never show up on the public /stocks page."
    )

    def handle(self, *args, **options):
        symbols = list(CRYPTO_SYMBOLS.keys())
        self.stdout.write(f"Fetching live crypto quotes for {len(symbols)} symbol(s) from FMP...")
        quotes = get_quotes(symbols)
        quote_map = {q["symbol"].upper(): q for q in quotes if q.get("symbol")}

        updated, created, skipped = 0, 0, []

        for sym, name in CRYPTO_SYMBOLS.items():
            q = quote_map.get(sym)
            if not q:
                skipped.append(sym)
                continue

            price = _to_decimal(q.get("price"))
            change = _to_decimal(q.get("change"))
            change_percent = _to_decimal(
                q.get("changePercentage") if q.get("changePercentage") is not None else q.get("changesPercentage")
            )

            stock, was_created = Stock.objects.get_or_create(
                symbol=sym,
                defaults={
                    "name": name,
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                    "volume": int(q.get("volume") or 0),
                    "market_cap": int(q.get("marketCap") or 0),
                    "sector": "Cryptocurrency",
                    "is_active": False,
                    "is_featured": False,
                },
            )
            if was_created:
                created += 1
            else:
                stock.price = price
                stock.change = change
                stock.change_percent = change_percent
                stock.volume = int(q.get("volume") or 0)
                stock.market_cap = int(q.get("marketCap") or 0)
                stock.save(update_fields=["price", "change", "change_percent", "volume", "market_cap", "updated_at"])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Crypto rates synced: {created} created, {updated} updated."))
        if skipped:
            self.stdout.write(self.style.WARNING(f"No quote returned for: {', '.join(skipped)}"))
