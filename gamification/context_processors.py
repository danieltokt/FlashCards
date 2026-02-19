def game_profile(request):
    if request.user.is_authenticated:
        from .models import GameProfile
        profile, _ = GameProfile.objects.get_or_create(user=request.user)
        return {'game_profile': profile}
    return {'game_profile': None}