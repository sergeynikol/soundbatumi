from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from django.conf.urls.i18n import i18n_patterns

from search import views as search_views
from home import views as home_views
from home import wagtail_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("login/", home_views.user_login, name="login"),
    path("register/", home_views.user_register, name="register"),
    path("logout/", home_views.user_logout, name="logout"),
    path("api/create-order/", home_views.create_order, name="create_order"),
    path(
        "api/telegram-login/",
        home_views.telegram_login,
        name="telegram_login"
    ),
    path(
        "api/telegram-callback/",
        home_views.telegram_callback,
        name="telegram_callback"
    ),
    # Bulk actions для заказов в Wagtail админ-панели
    path(
        "admin/order/delete-selected/",
        wagtail_views.delete_selected_orders,
        name="wagtail_delete_selected_orders"
    ),
    path(
        "admin/order/delete-all/",
        wagtail_views.delete_all_orders,
        name="wagtail_delete_all_orders"
    ),
    # allauth URLs
    path("accounts/", include("allauth.urls")),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

urlpatterns = urlpatterns + i18n_patterns(
    path("search/", search_views.search, name="search"),
    # For anything not caught by a more specific rule above,
    # hand over to Wagtail's page serving mechanism.
    # This should be the last pattern in the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served
    # from a subpath of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
)
