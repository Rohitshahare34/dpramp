from .counselling_constants import COUNSELLING_WHATSAPP_URL


def counselling(request):
    return {"counselling_whatsapp_url": COUNSELLING_WHATSAPP_URL}
