from django.core.exceptions import PermissionDenied


class ModuleResultPermissionMixin(object):

    def get_object(self, *args, **kwargs):
        obj = super(ModuleResultPermissionMixin, self).get_object(*args, **kwargs)
        # Make sure using requesting ModuleResult is the user who owns it.
        if not obj.user == self.request.user:
            raise PermissionDenied()
        else:
            return obj