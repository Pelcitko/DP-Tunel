from django.contrib import admin
from django.urls import reverse


class DefaultFilterAdmin(admin.ModelAdmin):
    def changelist_view(self, request, *args, **kwargs):
        try:
            test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
            if test and test[-1] and not test[-1].startswith('?'):
                url = reverse('admin:%s_%s_changelist' % (self.opts.app_label, self.opts.model_name))
                filters = []
                for filter in self.default_filters:
                    key = filter.split('=')[0]
                    if not key in request.GET:
                        filters.append(filter)
                if filters:
                    from django.http import HttpResponseRedirect
                    return HttpResponseRedirect("%s?%s" % (url, "&".join(filters)))
        except:
            pass
        return super(DefaultFilterAdmin, self).changelist_view(request, *args, **kwargs)

