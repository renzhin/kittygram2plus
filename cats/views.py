from rest_framework import viewsets
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


from .models import Achievement, Cat, User
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .throttling import WorkingHoursRateThrottle


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    permission_classes = (OwnerOrReadOnly,)
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    throttle_scope = 'low_request'
    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    # Временно отключим пагинацию на уровне вьюсета, 
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')
    # поля поиска + поле из связанной модели
    search_fields = ('name', 'achievements__name')
    ordering_fields = ('name', 'birth_year')
    # явно указанный вариант возможности сортировки по всем полям модели
    # ordering_fields = '__all__'
    # сортировка по умолчанию для класса
    ordering = ('birth_year',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернем обновленный перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень
        # #пермишенов без изменений
        return super().get_permissions()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
