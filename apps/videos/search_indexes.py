from haystack.indexes import *
from haystack.models import SearchResult
from haystack import site
from models import Video
from auth.models import CustomUser as User
from utils.celery_search_index import CelerySearchIndex
from django.conf import settings
from haystack.query import SearchQuerySet
import datetime

from haystack.exceptions import AlreadyRegistered

SUFFIX = u''

class LanguageField(SearchField):
    """
    This field is cerated for appending SUFFIX for short language code, beucase
    Solr does not want work with short strings properlly

    TODO: fix convering value before saving. Because SerachIndex.prepare return
    values witch are not converted at all with field methods.
    """

    def prepare(self, obj):
        value = super(LanguageField, self).prepare(obj)
        return self.prepare_lang(value)

    @classmethod
    def prepare_lang(cls, lang):
        return u'%s%s' % (lang, SUFFIX)

    @classmethod
    def convert(cls, value):
        if value is None:
            return

        value = unicode(value)

        if SUFFIX and value and value.endswith(SUFFIX):
            value = value[:-len(SUFFIX)]

        return value

class LanguagesField(MultiValueField):
    """
    See LanguageField
    """

    def prepare(self, obj):
        value = SearchField.prepare(self, obj)

        if value is None:
            return value

        value = list(value)

        output = []
        for val in value:
            if isinstance(val, (str, unicode)) and val:
                val = LanguageField.prepare_lang(val)

            output.append(val)

        return output

    def convert(self, value):
        if value is None:
            return

        return [LanguageField.convert(v) for v in list(value)]

class VideoIndex(CelerySearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title_display', boost=2)
    languages = LanguagesField(faceted=True)
    video_language = LanguageField(faceted=True)
    languages_count = IntegerField()
    video_id = CharField(model_attr='video_id', indexed=False)
    thumbnail_url = CharField(model_attr='get_thumbnail', indexed=False)
    small_thumbnail = CharField(model_attr='get_small_thumbnail', indexed=False)
    created = DateTimeField(model_attr='created')
    edited = DateTimeField(model_attr='edited')
    subtitles_fetched_count = IntegerField(model_attr='subtitles_fetched_count')
    widget_views_count = IntegerField(model_attr='widget_views_count')
    comments_count = IntegerField()

    contributors_count = IntegerField()
    activity_count = IntegerField()
    featured = DateTimeField(model_attr='featured', null=True)

    today_views = IntegerField()
    week_views = IntegerField()
    month_views = IntegerField()
    year_views = IntegerField()
    total_views = IntegerField(model_attr='widget_views_count')

    # non public videos won't show up in any of the site's listing
    # not even for the owner
    is_public = BooleanField()

    IN_ROW = getattr(settings, 'VIDEO_IN_ROW', 6)

    def prepare(self, obj):
        self.prepared_data = super(VideoIndex, self).prepare(obj)

        langs = obj.subtitlelanguage_set.exclude(language=u'', subtitle_count__gt=0)
        self.prepared_data['languages_count'] = obj.subtitlelanguage_set.filter(
                subtitle_count__gt=0, has_version=True).count()
        self.prepared_data['video_language'] = obj.language
        #TODO: converting should be in Field
        self.prepared_data['video_language'] = obj.language and LanguageField.prepare_lang(obj.language) or u''
        self.prepared_data['languages'] = [LanguageField.prepare_lang(lang.language) for lang in langs if lang.subtitle_count]
        self.prepared_data['contributors_count'] = User.objects.filter(subtitleversion__language__video=obj).distinct().count()
        self.prepared_data['activity_count'] = obj.action_set.count()
        self.prepared_data['week_views'] = obj.views['week']
        self.prepared_data['month_views'] = obj.views['month']
        self.prepared_data['year_views'] = obj.views['year']
        self.prepared_data['today_views'] = obj.views['today']
        self.prepared_data['title'] = obj.title_display(truncate=False).strip()
        self.prepared_data['is_public'] = obj.is_public

        return self.prepared_data

    def _setup_save(self, model):
        pass


    def _teardown_save(self, model):
        pass

    def index_queryset(self):
        return self.model.objects.order_by('-id')

    @classmethod
    def public(self):
        """
        All regular queries should go through this method, as it makes
        sure we never display videos that should be hidden
        """
        return SearchQuerySet().result_class(VideoSearchResult) \
            .models(Video).filter(is_public=True)

    @classmethod
    def get_featured_videos(cls):
        return  VideoIndex.public().filter(featured__gt=datetime.datetime(datetime.MINYEAR, 1, 1)) \
            .order_by('-featured')

    @classmethod
    def get_popular_videos(cls, sort='-week_views'):
        return  VideoIndex.public().order_by(sort)

    @classmethod
    def get_latest_videos(cls):
        return VideoIndex.public().order_by('-created')

class VideoSearchResult(SearchResult):
    title_for_url = Video.__dict__['title_for_url']
    get_absolute_url = Video.__dict__['_get_absolute_url']

    def __unicode__(self):
        title = self.title

        if len(title) > 60:
            title = title[:60]+'...'

        return title

class SubtitleLanguageIndex(CelerySearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField()
    language = CharField()

    def prepare(self, obj):
        self.prepared_data = super(SubtitleLanguageIndex, self).prepare(obj)
        self.prepared_data['title'] = obj.video.__unicode__().strip()
        self.prepared_data['language'] = obj.language_display()
        return self.prepared_data

try:
    site.register(Video, VideoIndex)
except AlreadyRegistered:
    # i hate python imports with all my will.
    # i hope they die.
    pass
#site.register(SubtitleLanguage, SubtitleLanguageIndex)
