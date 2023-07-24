"""Models for the SEEKER app.

"""
from django.apps.config import AppConfig
from django.apps import apps
from django.db import models, transaction
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
import os
import pytz


# From own application
from iberian.basic.utils import ErrHandle
from iberian.settings import MEDIA_ROOT, TIME_ZONE

# constants
STANDARD_LENGTH=100
LONG_STRING=255



# ============================ Supporting code =========================================

def get_current_datetime():
    """Get the current time"""
    return timezone.now()

def get_crpp_date(dtThis, readable=False):
    """Convert datetime to string"""

    if readable:
        # Convert the computer-stored timezone...
        dtThis = dtThis.astimezone(pytz.timezone(TIME_ZONE))
        # Model: yyyy-MM-dd'T'HH:mm:ss
        sDate = dtThis.strftime("%d/%B/%Y (%H:%M)")
    else:
        # Model: yyyy-MM-dd'T'HH:mm:ss
        sDate = dtThis.strftime("%Y-%m-%dT%H:%M:%S")
    return sDate

def upload_path(instance, filename=None):
    """Upload a (JSON/??) file to the right place,and remove old file if existing
    
    NOTE: this must be the relative path w.r.t. MEDIA_ROOT
    """

    oErr = ErrHandle()
    sBack = ""
    sSubdir = "upload"
    try:
        # Adapt the filename for storage
        # sAdapted = "{}_{:08d}_{}".format(sType, instance.id, filename.replace(" ", "_"))
        sAdapted = filename.replace(" ", "_")

        # The stuff that we return
        sBack = os.path.join(sSubdir, sAdapted)

        # Add the subdir [wordlist]
        fullsubdir = os.path.abspath(os.path.join(MEDIA_ROOT, sSubdir))
        if not os.path.exists(fullsubdir):
            os.mkdir(fullsubdir)

        # Add the actual filename to form an absolute path
        sAbsPath = os.path.abspath(os.path.join(fullsubdir, sAdapted))

        ## Add the actual filename to form an absolute path
        if os.path.exists(sAbsPath):
            # Remove it
            os.remove(sAbsPath)

    except:
        msg = oErr.get_error_message()
        oErr.DoError("upload_path")
    return sBack




# ============================= My models ===============================================


class Upload(models.Model):
    """An upload contains the details of an upload created by a user"""

    # [1] The short name of the file that has been uploaded
    name = models.CharField("File name", max_length=LONG_STRING)
    # [0-1] The link to the file that has been / can be uploaded to the server
    upfile = models.FileField("Uploaded file", null=True, blank=True, upload_to=upload_path)

    # [0-1] Room to save the contents of the file as stringified JSON
    fullinfo = models.TextField("Full file info", null=True, blank=True)

    # [1] Any upload belongs to a particular user
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="useruploads")

    # [1] Be sure to keep track of when this one was created and saved last
    created = models.DateTimeField(default=get_current_datetime)
    saved = models.DateTimeField(default=get_current_datetime)

    def __str__(self):
        return self.name

    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):

        # Adapt the save date
        self.saved = get_current_datetime()

        response = super(Upload, self).save(force_insert, force_update, using, update_fields)
        return response

    def get_saved(self):
        """REturn the saved date in a readable form"""

        # sDate = self.saved.strftime("%d/%b/%Y %H:%M")
        sDate = get_crpp_date(self.saved, True)
        return sDate

    def get_upload_file(self):
        """If file has been filled in, get the file name"""

        sBack = "-"
        if not self.upfile is None:
            sBack = self.upfile
        return sBack

