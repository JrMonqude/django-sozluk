from django.contrib import admin
from django.contrib.admin import DateFieldListFilter, SimpleListFilter
from django.db.models import Q
from django.urls import path
from django.utils.translation import gettext, gettext_lazy as _

from dictionary.admin.views.topic import TopicMove
from dictionary.models import Topic
from dictionary.utils.admin import intermediate


class MediaFilter(SimpleListFilter):
    title = _("Media links")
    parameter_name = "has_media"

    def lookups(self, request, model_admin):
        return [("yes", gettext("Yes")), ("no", gettext("No"))]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(Q(media="") | Q(media=None))

        if self.value() == "no":
            return queryset.filter(Q(media="") | Q(media=None))

        return None


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("title", "category", "mirrors")}),
        (
            _("Accessibility settings"),
            {"fields": ("allow_suggestions", "is_pinned", "is_banned", "is_censored", "is_ama")},
        ),
        (_("Metadata"), {"fields": ("created_by", "date_created")}),
        (
            _("Media"),
            {
                "classes": ("collapse",),
                "fields": ("media",),
                "description": _(
                    "<br>You can embed social media content into topics. You need to specify links of the media line"
                    " by line. Available options and example links:<br><br>"
                    "<b>YouTube video: </b>(https://www.youtube.com/embed/qXN15uh4DLU)<br>"
                    "<b>Instagram post: </b>(https://www.instagram.com/p/B4nfnuRg0sp/)<br>"
                    "<b>Spotify song: </b>(https://open.spotify.com/embed/track/1idpc4Pr94WH9GYU5umNfz)<br>"
                    "<b>Spotify album: </b>(https://open.spotify.com/embed/album/1yGbNOtRIgdIiGHOEBaZWf)<br>"
                    "<b>Spotify playlist: </b>"
                    "(https://open.spotify.com/embed/user/spotify/playlist/37i9dQZF1DX1tz6EDao8it)<br>"
                ),
            },
        ),
    )

    list_display = ("title", "created_by", "is_censored", "is_banned", "date_created")
    list_filter = (
        "category",
        "is_pinned",
        "is_censored",
        "is_banned",
        "is_ama",
        MediaFilter,
        ("date_created", DateFieldListFilter),
    )
    search_fields = ("title",)
    ordering = ("-date_created",)
    autocomplete_fields = ("category", "mirrors")
    actions = ("move_topic",)

    def get_readonly_fields(self, request, obj=None):
        readonly = ("created_by", "date_created")
        return readonly + ("title",) if obj else readonly

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path("actions/move/", self.admin_site.admin_view(TopicMove.as_view()), name="topic-move")]
        return custom_urls + urls

    # Custom permissions for action | pylint: disable=R0201
    def has_move_topic_permission(self, request):
        """Does the user have the move_topic permission?"""
        return request.user.has_perm("dictionary.move_topic")

    # Actions
    @intermediate
    def move_topic(self, request, queryset):
        return "admin:topic-move"

    # Short descriptions
    move_topic.short_description = _("Move entries from selected topics")

    # Permissions
    move_topic.allowed_permissions = ["move_topic"]
