from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand

from app.models import Stock
from app.fmp_client import get_quotes


def _to_decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


class Command(BaseCommand):
    help = "Refresh Stock.price/change/change_percent/volume/market_cap from the FMP API"

    def handle(self, *args, **options):
        symbols = list(Stock.objects.values_list("symbol", flat=True))

        if not symbols:
            self.stdout.write(self.style.WARNING("No stocks in the database — nothing to sync."))
            return

        self.stdout.write(f"Fetching live quotes for {len(symbols)} symbol(s) from FMP...")
        quotes = get_quotes(symbols)
        quote_map = {q["symbol"].upper(): q for q in quotes if q.get("symbol")}

        updated, skipped = 0, []

        for stock in Stock.objects.filter(symbol__in=symbols):
            q = quote_map.get(stock.symbol.upper())
            if not q:
                skipped.append(stock.symbol)
                continue

            stock.price = _to_decimal(q.get("price"))
            stock.change = _to_decimal(q.get("change"))
            stock.change_percent = _to_decimal(
                q.get("changePercentage") if q.get("changePercentage") is not None else q.get("changesPercentage")
            )
            stock.volume = int(q.get("volume") or 0)
            stock.market_cap = int(q.get("marketCap") or 0)
            stock.save(update_fields=["price", "change", "change_percent", "volume", "market_cap", "updated_at"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} stock(s)."))
        if skipped:
            self.stdout.write(self.style.WARNING(f"No quote returned for: {', '.join(skipped)}"))
