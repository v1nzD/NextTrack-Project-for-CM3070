from rest_framework import serializers

class RecommendPreferencesSerializer(serializers.Serializer):
    genre = serializers.CharField(required=False, allow_blank=True)
    mood = serializers.CharField(required=False, allow_blank=True)
    artist = serializers.CharField(required=False, allow_blank=True)
    randomize = serializers.BooleanField(required=False, default=False)
    # accept int or str seeds; serialize as string for portability
    seed = serializers.CharField(required=False, allow_blank=True)

class RecommendRequestSerializer(serializers.Serializer):
    recent_tracks = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )
    preferences = RecommendPreferencesSerializer(required=False)

class RecommendedTrackSerializer(serializers.Serializer):
    id = serializers.CharField()
    artist = serializers.CharField()
    title = serializers.CharField()
    genre = serializers.CharField()
    mood = serializers.CharField()

class RecommendResponseSerializer(serializers.Serializer):
    recommended_track = RecommendedTrackSerializer()


# For /api/recommend/top/ responses
class RecommendedItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    artist = serializers.CharField()
    mood = serializers.CharField()
    genre_hint = serializers.CharField()
    cover_art = serializers.CharField(required=False, allow_null=True)


class RecommendTopResponseSerializer(serializers.Serializer):
    recommended_tracks = serializers.ListField(child=RecommendedItemSerializer())
