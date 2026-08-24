import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import News
from app import fmp_client

TECH_KEYWORDS = [
    "tech", "software", "ai ", "artificial intelligence", "semiconductor",
    "chip", "cloud", "cybersecurity", "apple", "microsoft", "google",
    "nvidia", "meta", "amazon",
]
COMMODITY_KEYWORDS = [
    "oil", "gold", "silver", "copper", "wheat", "corn", "commodity",
    "crude", "natural gas", "platinum", "palladium", "energy", "brent",
]

FEEDS = [
    {"type": "stock",  "category": "Stocks",          "limit": 30},
    {"type": "forex",  "category": "Forex",           "limit": 15},
    {"type": "crypto", "category": "Cryptocurrency",  "limit": 15},
]


def _classify(title, text):
    combined = (title + " " + (text or "")).lower()
    for kw in TECH_KEYWORDS:
        if kw in combined:
            return "Technology"
    for kw in COMMODITY_KEYWORDS:
        if kw in combined:
            return "Commodities"
    return "Economy"


def _parse_date(date_str):
    if not date_str:
        return timezone.now()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        except ValueError:
            continue
    return timezone.now()


class Command(BaseCommand):
    help = "Fetch latest financial news from FMP and store in the News model."

    def _fetch_feed(self, feed):
        """Fetch one feed. Returns (feed, articles_or_error)."""
        try:
            articles = fmp_client.get_news(feed_type=feed["type"], limit=feed["limit"])
            if not isinstance(articles, list):
                return feed, Exception(f"Unexpected response: {articles}")
            return feed, articles
        except Exception as exc:
            return feed, exc

    def handle(self, *args, **options):
        created = skipped = errors = 0

        # Fetch all feeds in parallel — stays well within a short cron timeout
        feed_results = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(self._fetch_feed, feed): feed for feed in FEEDS}
            for future in as_completed(futures):
                feed_results.append(future.result())

        for feed, articles in feed_results:
            if isinstance(articles, Exception):
                self.stderr.write(f"  Error fetching {feed['type']} news: {articles}")
                errors += 1
                continue

            for article in articles:
                title = (article.get("title") or "").strip()[:255]
                if not title:
                    continue

                # Orchard's News model has no source_url field, so dedupe by title alone.
                if News.objects.filter(title=title).exists():
                    skipped += 1
                    continue

                text      = article.get("text") or article.get("content") or ""
                category  = feed["category"] or _classify(title, text)
                published_at = _parse_date(article.get("publishedDate", ""))
                symbol    = article.get("symbol") or ""
                publisher = article.get("publisher") or article.get("site") or ""

                # Note: FMP's article image is a hotlinked external URL, but the
                # `image` field here is a CloudinaryField (expects an uploaded
                # asset, not an arbitrary external URL) — left blank; the API
                # already returns `image_url: null` gracefully in that case.
                News.objects.create(
                    title=title,
                    summary=text[:400] if text else title,
                    content=text or title,
                    category=category,
                    source=article.get("site") or publisher or "FMP",
                    author=publisher or "Staff Writer",
                    published_at=published_at,
                    tags=[symbol] if symbol else [],
                    is_featured=False,
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"News sync complete: {created} created, {skipped} skipped, {errors} feed error(s)"
            )
        )
