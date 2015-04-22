import io

from django.conf import settings
from django.utils import timezone
from django.core.files.storage import Storage
from django.core.files import File
from django.utils.encoding import filepath_to_uri

from django.utils.six.moves.urllib.parse import urljoin
from .models import DbFile


class DatabaseStorage(Storage):
    def _open(self, name, mode='rb'):
        file = self._getfile(name)
        file.accessed = timezone.now()
        file.save()

        iofile = io.BytesIO(file.blob)
        iofile.name = file.name
        iofile.mode = mode

        return File(iofile)

    def _save(self, name, content):
        name = name.replace('\\', '/')
        blob = content.read()
        size = len(blob)

        file = DbFile(name=name, blob=blob, size=size)
        file.save()
        return name

    def get_valid_name(self, name):
        return super(DatabaseStorage, self).get_valid_name(name.replace('\\', '/'))

    def exists(self, name):
        try:
            self._getfile(name)
            return True
        except FileNotFoundError:
            return False

    def delete(self, name):
        self._getfile(name).delete()

    def url(self, name):
        return urljoin(settings.MEDIA_URL, filepath_to_uri(name))

    def size(self, name):
        return self._getfile(name).size

    def path(self, name):
        return name

    def modified_time(self, name):
        return self._getfile(name).modified

    def created_time(self, name):
        return self._getfile(name).created

    def accessed_time(self, name):
        return self._getfile(name).accessed


    def _getfile(self, name):
        try:
            return DbFile.objects.defer('blob').get(name=name)
        except DbFile.DoesNotExist:
            raise FileNotFoundError(name)

