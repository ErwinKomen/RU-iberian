from django.db import models
import datetime
from partial_date import PartialDateField
from django.contrib.auth.models import User

# Create your models here.
from django.db.models import ForeignKey

LONG_TEXT = 256
AVERAGE_TEXT = 100
SHORT_TEXT = 50


# User model
class UserProfileInfo(models.Model):
    # Create relationship (don't inherit from User!)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    # Add any additional attributes you want
    # portfolio_site = models.URLField(blank=True)
    # pip install pillow to use this!
    # Optional: pip install pillow --global-option=”build_ext” --global-option=”--disable-jpeg”
    # profile_pic = models.ImageField(upload_to='profile_pics', blank=True)

    def __str__(self):
        # Built-in attribute of django.contrib.auth.models.User!
        return self.user.username


# ================================ HELPER MODELS =========================================================================


class InstitutionType(models.Model):
    """Type of institution: church, monastery, piggy bank"""

    # [1] The name for the institution type
    name = models.CharField(max_length=AVERAGE_TEXT)

    def __str__(self):
        return self.name


class Bibliography(models.Model):
    short_title = models.CharField(max_length=250, blank=False, default='')
    author = models.CharField(max_length=SHORT_TEXT, blank=True, null=True)
    year = PartialDateField(blank=True, null=True)

    def __str__(self):
        return self.short_title


class SaintType(models.Model):
    name = models.CharField(max_length=AVERAGE_TEXT)  # Just Man, Confessor, Virgin, Virgin Confessor, Apostle, etc

    def __str__(self):
        return self.name


class ObjectType(models.Model):
    name = models.CharField(max_length=AVERAGE_TEXT)  #

    def __str__(self):
        return self.name


class ManuscriptType(models.Model):
    name = models.CharField(max_length=AVERAGE_TEXT)  # calendar, commicus, antiphoner, misticus, liber canticorum, etc

    def __str__(self):
        return self.name


class Rite(models.Model):
    name = models.CharField(max_length=AVERAGE_TEXT)  # old Hispanic, Roman

    def __str__(self):
        return self.name


class Feast(models.Model):
    name = models.CharField(max_length=AVERAGE_TEXT)  #
    date = models.CharField(max_length=AVERAGE_TEXT, blank=True, default='')

    def __str__(self):
        return self.name


# ===================== Location models: City, Region, Museum, Church as a location =================================

class City(models.Model):
    name = models.CharField(max_length=AVERAGE_TEXT, blank=False)
    latitude = models.DecimalField(max_digits=7, decimal_places=5, default=0)
    longitude = models.DecimalField(max_digits=7, decimal_places=5, default=0)

    def __str__(self):
        return self.name


class Region(models.Model):
    region_number = models.PositiveIntegerField(null=True, blank=True)
    extent_shapefile = models.FileField(upload_to='shapefiles/', max_length=SHORT_TEXT, null=True,
                                        blank=True)

    # ============= FK Links to other items ======================
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=False, default='')

    def __str__(self):
        st = self.city.name + ' ' + str(self.region_number)
        return st


class Museum(models.Model):
    name = models.CharField(max_length=AVERAGE_TEXT, blank=False)
    description = models.CharField(max_length=SHORT_TEXT0, default='', blank=True)

    # ============= FK Links to other items ======================
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Church(models.Model):
    """A physical church with a name, situated somewhere.
    
    The church may have existed at some time, and it was in or close to a city inside a region
    """

    # [1] The name of the church
    name = models.CharField(max_length=AVERAGE_TEXT, blank=False, default='')

    # [0-1] Description of this church
    description = models.TextField(default='', blank=True)

    # [0-1] Lower bounds of the church date
    date_lower = PartialDateField(blank=True, null=True)
    # [0-1] Upper bounds of the church date
    date_upper = PartialDateField(blank=True, null=True)
    # [0-1] Location of the church in coordinates
    coordinates_latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True, default=0)
    coordinates_longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True, default=0)

    # [0-1] Whether there is any textual evidence for this church
    TEXTUAL = ( ('Y', 'Yes'), ('N', 'No'), )
    textual_evidence = models.CharField(max_length=1, choices=TEXTUAL, default='Y', blank=True, null=True)

    # [0-1] Whether there is any material evidence for this church
    MATERIAL = ( ('Y', 'Yes'), ('N', 'No'), )
    material_evidence = models.CharField(max_length=1, choices=MATERIAL, default='Y', blank=True, null=True)

    # [1] Status of this entry
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    # ============= FK Links to other items ======================
    # [0-1] location of the church w.r.t. a city in a region
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, default='', null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, default='', null=True)

    # [0-1] Type of institution
    institution_type = models.ForeignKey(InstitutionType, on_delete=models.CASCADE, blank=True, default='', null=True)

    # ======================= Many-to-Many relations ======================================
    # external_link = models.URLField(max_length=LONG_TEXT, default='', blank=True) 
    # NOTE: The above is replaced with ChurchLinkRelation in order to have multiple external links

    # [0-1] FK Link to any bibliographic data
    # NOTE: this will not be used in the future. I
    #       I (=Mojtaba) didn't delete this because there is data saved for some entries on the database.
    # bibliography = models.ForeignKey(Bibliography, on_delete=models.CASCADE, blank=True, default='', null=True)  

    # [0-1] Many to many link to the model [Bibliography]
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies', blank=True, default='')

    def __str__(self):
        return self.name


# ================================ MAIN MODELS =========================================================================


class Saint(models.Model):
    name = models.CharField(max_length=LONG_TEXT)
    feast_day = models.CharField(max_length=LONG_TEXT, blank=True, null=True)
    feast_day_old = PartialDateField(blank=True, null=True)
    death_date = PartialDateField(blank=True, null=True)
    death_place = models.CharField(max_length=LONG_TEXT, blank=True, null=True)
    # external_link = models.URLField(max_length=LONG_TEXT, default='', blank=True) # It is replaced with SaintLinkRElation in order to have multiple external links
    description = models.TextField(default='', blank=True, null=True)
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    # ============= FK Links to other items ======================
    type = models.ForeignKey(SaintType, related_name='saints', on_delete=models.CASCADE, blank=True, default='',
                             null=True)

    def __str__(self):
        return self.name


class Inscription(models.Model):
    reference_no = models.CharField(max_length=AVERAGE_TEXT, blank=False, default='')
    original_location = models.ForeignKey(Church, related_name='originallocationsinscription',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)
    original_location_city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, default='', null=True)
    original_location_region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, default='', null=True)
    current_location = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True, default='', null=True)
    current_location_museum = models.ForeignKey(Museum, on_delete=models.CASCADE, blank=True, default='', null=True)
    date_lower = PartialDateField(blank=True, null=True)
    date_upper = PartialDateField(blank=True, null=True)
    # external_link = models.URLField(max_length=LONG_TEXT, default='', blank=True) # It is replaced with InscriptionLinkRelation in order to have multiple external links
    bibliography = models.ForeignKey(Bibliography, on_delete=models.SET_NULL, blank=True, default='',
                                     null=True)  # this will not be
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies_inscription', blank=True,
                                               default='')
    text = models.TextField(max_length=LONG_TEXT, blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    def __str__(self):
        return self.reference_no


class LiturgicalManuscript(models.Model):
    """A liturgical manuscript"""

    # [1] Where the manuscript is kept
    shelf_no = models.CharField(max_length=AVERAGE_TEXT, blank=False, default='')
    # [0-1] Description
    description = models.TextField(default='', blank=True, null=True)
    # [0-1] Dating
    date_lower = PartialDateField(blank=True, null=True)
    date_upper = PartialDateField(blank=True, null=True)

    status = models.BooleanField("Completed", default=False, help_text="Complete")

    # ============= FK Links to other items ======================
    rite = models.ForeignKey(Rite, on_delete=models.SET_NULL, blank=True, default='', null=True)
    type = models.ForeignKey(ManuscriptType, on_delete=models.SET_NULL, blank=True, default='', null=True)
    original_location = models.ForeignKey(Church, related_name='originallocationslitman',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)
    original_location_city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, default='', null=True)
    original_location_region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, default='', null=True)
    provenance = models.ForeignKey(Church, on_delete=models.SET_NULL, blank=True, default='', null=True)
    provenance_museum = models.ForeignKey(Museum, on_delete=models.SET_NULL, blank=True, default='', null=True)
    feast = models.ForeignKey(Feast, on_delete=models.SET_NULL, blank=True, default='', null=True)

    # external_link = models.URLField(max_length=LONG_TEXT, default='', blank=True) # It is replaced with litmanLinkRelation in order to have multiple external links
    bibliography = models.ForeignKey(Bibliography, on_delete=models.SET_NULL, blank=True, default='',
                                     null=True)  # this will not be

    # ============= MANY-TO-MANY links =============================
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies_litman', blank=True,
                                               default='')

    def __str__(self):
        return self.shelf_no


class TextItem(models.Model):
    """A particular text that is dated, is located somewhere, and may even occur in a bibliography"""

    # [1] The title of this text item
    title = models.CharField(max_length=LONG_TEXT, blank=False, default='')
    # [0-1] Description
    description = models.TextField(default='', blank=True, null=True)
    # [0-1] Dating
    date_lower = PartialDateField(blank=True, null=True)
    date_upper = PartialDateField(blank=True, null=True)

    status = models.BooleanField("Completed", default=False, help_text="Complete")

    # ============= MANY-TO-MANY links =============================
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies_textitem', blank=True,
                                               default='')

    def __str__(self):
        return self.title



class Object(models.Model):
    name = models.CharField(max_length=LONG_TEXT, blank=False, default='')
    date_lower = PartialDateField(blank=True, null=True)
    date_upper = PartialDateField(blank=True, null=True)
    original_location = models.ForeignKey(Church, related_name='originallocations', on_delete=models.CASCADE,
                                          blank=True, default='', null=True)
    original_location_city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, default='', null=True)
    original_location_region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, default='', null=True)
    current_location = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True, default='', null=True)
    current_location_museum = models.ForeignKey(Museum, on_delete=models.CASCADE, blank=True, default='', null=True)
    type = models.ForeignKey(ObjectType, on_delete=models.CASCADE, blank=True, default='', null=True)
    TEXTUAL = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )
    textual_evidence = models.CharField(max_length=1, choices=TEXTUAL, default='Y', blank=True, null=True)
    MATERIAL = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )
    material_evidence = models.CharField(max_length=1, choices=MATERIAL, default='Y', blank=True, null=True)
    # external_link = models.URLField(max_length=LONG_TEXT, default='', blank=True) # It is replaced with ObjectLinkRelation in order to have multiple external links
    bibliography = models.ForeignKey(Bibliography, on_delete=models.CASCADE, blank=True, default='',
                                     null=True)  # this will not be
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies_object', blank=True,
                                               default='')
    description = models.TextField(default='', blank=True, null=True)
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    def __str__(self):
        return self.name


# ================================== RELATIONS ==========================================================================


class ObjectChurchRelation(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE, blank=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    start_date = PartialDateField(blank=True, null=True)
    end_date = PartialDateField(blank=True, null=True)

    def __str__(self):
        message = "{} and {}".format(self.object, self.church)
        return message


class LitManuscriptChurchRelation(models.Model):
    liturgical_manuscript = models.ForeignKey(LiturgicalManuscript, on_delete=models.CASCADE, blank=True, null=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    start_date = PartialDateField(blank=True, null=True)
    end_date = PartialDateField(blank=True, null=True)

    def __str__(self):
        message = "{} and {}".format(self.liturgical_manuscript, self.church)
        return message


class SaintChurchRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = "{} and {}".format(self.saint, self.church)
        return message


class SaintInscriptionRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = "{} and {}".format(self.saint, self.inscription)
        return message


class SaintObjectRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    object = models.ForeignKey(Object, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = "{} and {}".format(self.saint, self.object)
        return message


class SaintLitManuscriptRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    liturgical_manuscript = models.ForeignKey(LiturgicalManuscript, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = "{} and {}".format(self.saint, self.liturgical_manuscript)
        return message


class InscriptionChurchRelation(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, blank=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    start_date = PartialDateField(blank=True, null=True)
    end_date = PartialDateField(blank=True, null=True)

    def __str__(self):
        message = "{} and {}".format(self.inscription, self.church)
        return message


# Multiple external links
class SaintLinkRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=LONG_TEXT, default='', blank=True)

    def __str__(self):
        message = "{} and {}".format(self.saint, self.link)
        return message


class ChurchLinkRelation(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=LONG_TEXT, default='', blank=True)

    def __str__(self):
        message = "{} and {}".format(self.church, self.link)
        return message


class ObjectLinkRelation(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=LONG_TEXT, default='', blank=True)

    def __str__(self):
        message = "{} and {}".format(self.object, self.link)
        return message


class InscriptionLinkRelation(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=LONG_TEXT, default='', blank=True)

    def __str__(self):
        message = "{} and {}".format(self.inscription, self.link)
        return message


class LitManuscriptLinkRelation(models.Model):
    liturgical_manuscript = models.ForeignKey(LiturgicalManuscript, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=LONG_TEXT, default='', blank=True)

    def __str__(self):
        message = "{} and {}".format(self.liturgical_manuscript, self.link)
        return message
