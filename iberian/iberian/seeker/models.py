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
import json
import pytz
import openpyxl


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

def excel_to_list(filename, lExcel = None):
    """Read an excel file into a list of objects

    This assumes that the first row contains column headers
    """

    oErr = ErrHandle()
    bResult = True
    lData = []
    msg = ""
    try:

        # Read string file
        wb = openpyxl.load_workbook(filename, read_only=True)
        ws = wb.active

        # Iterate through rows
        bFirst = True
        
        lHeader = []
        if lExcel is None:
            # Cannot handle this
            msg = "Please specify lExcel"
            return False, [], msg

        # Iterate
        for row in ws.iter_rows(min_row=1, min_col=1):
            if bFirst:
                # Expect header
                for cell in row:
                    sValue = cell.value.strip("\t").lower()                    
                    sKey = ""
                    for idx, oItem in enumerate(lExcel):
                        item = oItem['xfield'].lower()
                        if item in sValue:
                            sKey = oItem['field']
                            break
                    # Check if it's okay
                    if sKey == "":
                        # Cannot read this
                        msg = "Don't understand column header [{}]".format(sValue)
                        return False, [], msg
                    lHeader.append(sKey)
                bFirst = False
            elif row[0].value != None:
                oRow = {}
                for idx, key in enumerate(lHeader):
                    cell = row[idx]
                    # Get the value as a string
                    cv = "" if cell.value == None else "{}".format(cell.value).strip()
                    oRow[key] = cv
                # Also add the row number (as string)
                oRow['row_number'] = "{}".format(row[0].row)
                lData.append(oRow)
        # Close the workbook
        wb.close()

        # Return positively
        bResult = True
    except:
        # Note the error here
        msg = oErr.get_error_message()
        bResult = False
        oErr.DoError("excel_to_list")

    # Return what we have found
    return bResult, lData, msg




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

    # [0-1] Any status message from processing this upload
    status = models.TextField("Status", null=True, blank=True)

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

    def do_process(self):
        """Process the upload"""

        bResult = True
        oErr = ErrHandle()
        try:
            sText = self.fullinfo
            if not sText is None and sText != "":
                # It has been read: is this valid json?
                oText = json.loads(sText)
                # Getting here means that we have loaded a valid JSON

                # Indicate we have read it
                self.set_status("Processed information at: {}".format(get_crpp_date(get_current_datetime(), True)))
        except:
            msg = oErr.get_error_message()
            oErr.DoError("do_process")
            bResult = False

        return bResult

    def get_info(self):
        """Get information"""

        sBack = "-"
        if not self.fullinfo is None and self.fullinfo != "":
            try:
                oInfo = json.loads(self.fullinfo)
                num_items = len(oInfo)
                sBack = "{} item(s)".format(num_items)
            except:
                sBack = "Sorry, get_info() cannot decypher what is in @fullinfo"
        return sBack

    def get_saved(self):
        """REturn the saved date in a readable form"""

        # sDate = self.saved.strftime("%d/%b/%Y %H:%M")
        sDate = get_crpp_date(self.saved, True)
        return sDate

    def get_status(self):
        sBack = "-"
        if not self.status is None:
            sBack = self.status
        return sBack

    def get_upload_file(self):
        """If file has been filled in, get the file name"""

        sBack = "-"
        oErr = ErrHandle()
        try:
            if not self.upfile is None and not self.upfile.name is None and self.upfile.name != "":
                sBack = "<code>{}</code>".format(os.path.basename( self.upfile.name) )
        except:
            msg = oErr.get_error_message()
            oErr.DoError("get_upload_file")
        return sBack

    def read_fullinfo(self, lExcel = None):
        sBack = ""
        bResult = True
        oErr = ErrHandle()
        try:
            if not self.upfile is None and not self.upfile.name is None and self.upfile.name != "":
                # Okay, a file has been uploaded
                # Check if there is any contents
                if self.fullinfo is None or self.fullinfo == "":
                    # Try to read the file as text
                    sBasename = os.path.basename(self.upfile.name)
                    sFilename = os.path.abspath(os.path.join(MEDIA_ROOT, "upload", sBasename))
                    # Check existence
                    if os.path.exists(sFilename):
                        # Try read it as JSON or as EXCEL
                        try:
                            sBase, sExt = os.path.splitext(sBasename)
                            sExt = sExt.lower()

                            if sExt == "json":
                                with open(sFilename, "r", encoding="utf-8") as f:
                                    oResult = json.load(f)
                                sBack = json.dumps(oResult, indent=2)
                            elif sExt == "xlsx" and not lExcel is None:
                                bResult, lst_row, msg = excel_to_list(sFilename, lExcel)

                                if bResult:
                                    sBack = json.dumps(lst_row, indent=2)
                            else:
                                # We do not know the file extension
                                sBack = "Sorry, cannot read file. Is it in UTF-8? [{}]".format(sBasename)
                                bResult = False
                                return bResult, sBack

                            # Getting here means all is well
                            self.fullinfo = sBack
                            self.save()
                            self.set_status("Uploaded info from file at: {}".format(get_crpp_date(get_current_datetime(), True)))
                        except:
                            sBack = "Sorry, cannot read file. Is it in UTF-8? [{}]".format(sBasename)
                            bResult = False
                            return bResult, sBack
                else:
                    sBack = self.fullinfo

        except:
            msg = oErr.get_error_message()
            oErr.DoError("do_process")
            bResult = False
        return bResult, sBack

    def set_status(self, msg):
        self.status = msg
        self.save()

