from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import News


@api_view(["GET"])
@permission_classes([AllowAny])
def list_news(request):
    """
    Get list of news articles with optional filtering by category and search
    """
    # Get query parameters
    category = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()

    # Start with all news
    news_query = News.objects.filter().order_by('-is_featured', '-published_at')

    # Apply category filter
    if category:
        news_query = news_query.filter(category=category)

    # Apply search filter
    if search_query:
        news_query = news_query.filter(
            title__icontains=search_query
        ) | news_query.filter(
            summary__icontains=search_query
        ) | news_query.filter(
            content__icontains=search_query
        )

    # Serialize news articles
    news_list = []
    for article in news_query:
        # Get image URL from Cloudinary field
        image_url = None
        if article.image:
            image_url = article.image.url

        news_list.append({
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "content": article.content,
            "category": article.category,
            "source": article.source,
            "author": article.author,
            "published_at": article.published_at.isoformat(),
            "image_url": image_url,
            "tags": article.tags,
            "is_featured": article.is_featured,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat(),
        })

    return Response(news_list)


@api_view(["GET"])
@permission_classes([AllowAny])
def news_detail(request, news_id):
    """
    Get detailed information about a specific news article
    """
    try:
        article = News.objects.get(id=news_id)
    except News.DoesNotExist:
        return Response({
            "success": False,
            "error": "News article not found"
        }, status=404)

    # Get image URL from Cloudinary field
    image_url = None
    if article.image:
        image_url = article.image.url

    return Response({
        "success": True,
        "article": {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "content": article.content,
            "category": article.category,
            "source": article.source,
            "author": article.author,
            "published_at": article.published_at.isoformat(),
            "image_url": image_url,
            "tags": article.tags,
            "is_featured": article.is_featured,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat(),
        }
    })
