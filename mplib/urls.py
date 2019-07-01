from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from mplib import views, tmpview

router = DefaultRouter()
router.root_view_name = 'API List'
router.register(r'user', views.UserViewSet, base_name='user')
router.register(r'libuser', views.LibUserViewSet, base_name='libuser')
router.register(r'notice', views.NoticeViewSet, base_name='notice')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'schema', views.schema_view),
    url(r'test', tmpview.test),
    # url(r'rank', tmpview.rank),
    # url(r'detail', tmpview.rank),
    # url(r'search_lib', tmpview.search_lib),
    # url(r'notice', tmpview.notice)
]
