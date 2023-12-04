from django.db import models
import datetime
from partial_date import PartialDateField
from django.contrib.auth.models import User

# Create your models here.
from django.db.models import ForeignKey, IntegerField

SUPER_LONG_TEXT = 500
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
    """The type of Saint that is being defined (e.g. man, confessor, virgin)"""

    name = models.CharField(max_length=AVERAGE_TEXT)  # Just Man, Confessor, Virgin, Virgin Confessor, Apostle, etc

    def __str__(self):
        return self.name


class LiturgicalType(models.Model):
    """This is different from SaintType, but still is used in the description of a Saint"""

    # [1] The name of this liturgical type
    name = models.CharField(max_length=AVERAGE_TEXT)

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


class AuthorAncient(models.Model):
    """Medieval author of literary text, like Braulio"""

    name = models.CharField(max_length=AVERAGE_TEXT)  #

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
    """A region is an area with a name and a shape"""

    # [1] Each saint is known by a name
    name = models.CharField(max_length=LONG_TEXT)
    # [0-1] Optional number for the region
    region_number = models.PositiveIntegerField(null=True, blank=True)
    # [0-1] Optional shapefile for the region
    extent_shapefile = models.FileField(upload_to='shapefiles/', max_length=SHORT_TEXT, null=True,
                                        blank=True)

    # ============= FK Links to other items ======================
    # issue #17: remove the link to city
    # city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=False, default='')

    def __str__(self):
        # issue #17: region is no longer marked by city and region number
        # OLD st = self.city.name + ' ' + str(self.region_number)
        # Instead: region is just marked by name
        st = self.name
        return st


class Museum(models.Model):
    name = models.CharField(max_length=AVERAGE_TEXT, blank=False)
    description = models.CharField(max_length=SUPER_LONG_TEXT, default='', blank=True)

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
    """Someone who has been recognized as 'saint' by a particular group of people"""

    # [1] Each saint is known by a name
    name = models.CharField(max_length=LONG_TEXT)
    # [0-1] SEMM Name
    semm_name = models.CharField(max_length=LONG_TEXT, blank=True, null=True)
    # [0-1] Feast day associated with this saint
    feast_day = models.CharField(max_length=LONG_TEXT, blank=True, null=True)
    feast_day_old = PartialDateField(blank=True, null=True)
    # [0-1] Date and place where this saint has died
    death_date = PartialDateField(blank=True, null=True)
    death_date_last = PartialDateField(blank=True, null=True)
    death_place = models.CharField(max_length=LONG_TEXT, blank=True, null=True)

    # OBSOLETE
    # external_link = models.URLField(max_length=LONG_TEXT, default='', blank=True) # It is replaced with SaintLinkRElation in order to have multiple external links

    # [0-1] Description
    description = models.TextField(default='', blank=True, null=True)

    status = models.BooleanField("Completed", default=False, help_text="Complete")

    # ============= FK Links to other items ======================
    # [0-1] Optional link to a Saint Type (or is it not optional??)
    type = models.ForeignKey(SaintType, related_name='saints', on_delete=models.CASCADE, blank=True, default='',
                             null=True)
    # [0-1] Optional link to Liturgical Type
    ltype = models.ForeignKey(LiturgicalType, related_name='ltypesaints', on_delete=models.CASCADE, blank=True, default='',
                             null=True)
    # [0-1] Optional link to a region
    location_region = models.ForeignKey(Region, related_name='loc_region_saints',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)
    # [0-1] Optional link to a city: this is the city, where the saint has died (death_city)
    death_city = models.ForeignKey(City, related_name='cities', on_delete=models.SET_NULL, blank=True, null=True)

    # ============= MANY-TO-MANY links =============================

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


class LiteraryText(models.Model):
    """A literary text is the assumed original of a text that later occurs in manuscripts.
    
    - Dating: a literary text is dated by a lower and upper date
    - Location: it originates from somewhere [City, Region, Museum or Church]
    - Bibliography: references to this literary text may occur in a bibliography"""

    # [1] The title of this text item
    title = models.CharField(max_length=LONG_TEXT, blank=False, default='')
    # [0-1] Optionally (if known) the actual text
    text = models.TextField(default='', blank=True, null=True)
    # [0-1] Description
    description = models.TextField(default='', blank=True, null=True)
    # [0-1] Dating
    date_lower = PartialDateField(blank=True, null=True)
    date_upper = PartialDateField(blank=True, null=True)

    status = models.BooleanField("Completed", default=False, help_text="Complete")

    # ============= Foreign Key links =================================

    # [0-1] The author (a medieval author, like Braulio)
    author = models.ForeignKey(AuthorAncient, related_name='author_literarytexts',
                                          on_delete=models.SET_NULL, blank=True, null=True)
    # [0-1] Location links
    location_church = models.ForeignKey(Church, related_name='loc_church_literarytexts',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)
    location_city = models.ForeignKey(City, related_name='loc_city_literarytexts',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)
    location_region = models.ForeignKey(Region, related_name='loc_region_literarytexts',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)
    location_museum = models.ForeignKey(Museum, related_name='loc_museum_literarytexts',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)

    # ============= MANY-TO-MANY links =============================
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies_literarytext', blank=True,
                                               default='')

    def __str__(self):
        return self.title

    def get_daterange(self):
        sBack = "-"
        if self.date_lower is None:
            if not self.date_upper is None:
                sBack = self.date_upper
        else:
            if self.date_upper is None:
                sBack = self.date_lower
            else:
                sBack = "{} - {}".format(self.date_lower, self.date_upper)
        return sBack

    def get_text(self):
        sBack = ""
        if not self.text is None and self.text != "":
            sBack = self.text
        return sBack

    def get_description(self):
        sBack = ""
        if not self.description is None and self.description != "":
            sBack = self.description
        return sBack

    def get_location_church(self):
        sBack = ""
        if not self.location_church is None and self.location_church != "":
            sBack = self.location_church
        return sBack

    def get_location_city(self):
        sBack = ""
        if not self.location_city is None and self.location_city != "":
            sBack = self.location_city
        return sBack

    def get_location_region(self):
        sBack = ""
        if not self.location_region is None and self.location_region != "":
            sBack = self.location_region
        return sBack

    def get_location_museum(self):
        sBack = ""
        if not self.location_museum is None and self.location_museum != "":
            sBack = self.location_museum
        return sBack


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

    def get_dates(self):
        """Show the date range"""

        sBack = ""
        lHtml = []
        if not self.start_date is None:
            lHtml.append(str(self.start_date))
        if not self.end_date is None:
            lHtml.append(str(self.end_date))
        sBack = "-".join(lHtml)
        return sBack


class LitManuscriptChurchRelation(models.Model):
    liturgical_manuscript = models.ForeignKey(LiturgicalManuscript, on_delete=models.CASCADE, blank=True, null=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    start_date = PartialDateField(blank=True, null=True)
    end_date = PartialDateField(blank=True, null=True)

    def __str__(self):
        message = "{} and {}".format(self.liturgical_manuscript, self.church)
        return message

    def get_dates(self):
        """Show the date range"""

        sBack = ""
        lHtml = []
        if not self.start_date is None:
            lHtml.append(str(self.start_date))
        if not self.end_date is None:
            lHtml.append(str(self.end_date))
        sBack = "-".join(lHtml)
        return sBack


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
        if self.saint_id is None:
            message = "NONE and {}".format(self.liturgical_manuscript)
        else:
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

    def get_dates(self):
        """Show the date range"""

        sBack = ""
        lHtml = []
        if not self.start_date is None:
            lHtml.append(str(self.start_date))
        if not self.end_date is None:
            lHtml.append(str(self.end_date))
        sBack = "-".join(lHtml)
        return sBack


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


# ------------------- related to LiteraryText ------------------------------------------

class LiteraryTextLinkRelation(models.Model):
    ltext = models.ForeignKey(LiteraryText, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=LONG_TEXT, default='', blank=True)

    def __str__(self):
        message = "{} and {}".format(self.ltext, self.link)
        return message


class LiteraryTextBibliographyRelation(models.Model):
    ltext = models.ForeignKey(LiteraryText, on_delete=models.CASCADE, blank=True)
    bibliography = models.ForeignKey(Bibliography, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = self.id
        if not self.ltext is None and not self.bibliography is None:
            message = "{} and {}".format(self.ltext, self.bibliography)
        return message



