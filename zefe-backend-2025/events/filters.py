import django_filters
from events.models import UserNetwork,UserEvent
from user.models import UserProfile,UserField

class UserNetworkFilter(django_filters.FilterSet):
    position = django_filters.CharFilter(method='filter_by_position')
    field = django_filters.CharFilter(method='filter_by_field')
    event = django_filters.CharFilter(method='filter_by_event')
    city = django_filters.CharFilter(method='filter_by_city')

    def filter_by_position(self, queryset, name, value):
        return queryset.filter(scanned__user_profile__position__iexact=value)

    def filter_by_field(self, queryset, name, value):
        return queryset.filter(scanned__user_fields__field__name__iexact=value)

    def filter_by_event(self, queryset, name, value):
        return queryset.filter(base_event__user_events__title__iexact=value, base_event__user_events__user=self.request.user)

    def filter_by_city(self, queryset, name, value):
        return queryset.filter(scanned__user_profile__city__iexact=value)

    class Meta:
        model = UserNetwork
        fields = []
