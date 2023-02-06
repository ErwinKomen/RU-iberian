from django.db import models
import datetime
from partial_date import PartialDateField
from django.contrib.auth.models import User

# Create your models here.
from django.db.models import ForeignKey


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


# Location models: City, Region, Museum, Church as a location
class City(models.Model):
    name = models.CharField(max_length=100, blank=False)
    latitude = models.DecimalField(max_digits=7, decimal_places=5, default=0)
    longitude = models.DecimalField(max_digits=7, decimal_places=5, default=0)

    def __str__(self):
        return self.name


class Region(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=False, default='')
    region_number = models.PositiveIntegerField(null=True, blank=True)
    extent_shapefile = models.FileField(upload_to='shapefiles/', max_length=50, null=True,
                                        blank=True)

    def __str__(self):
        st = self.city.name + ' ' + str(self.region_number)
        return st


class Museum(models.Model):
    name = models.CharField(max_length=100, blank=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=500, default='', blank=True)

    def __str__(self):
        return self.name


class InstitutionType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Bibliography(models.Model):
    short_title = models.CharField(max_length=250, blank=False, default='')
    author = models.CharField(max_length=50, blank=True, null=True)
    year = PartialDateField(blank=True, null=True)

    def __str__(self):
        return self.short_title


class Church(models.Model):
    name = models.CharField(max_length=100, blank=False, default='')
    date_lower = PartialDateField(blank=True, null=True)
    date_upper = PartialDateField(blank=True, null=True)
    coordinates_latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True, default=0)
    coordinates_longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True, default=0)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, default='', null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, default='', null=True)
    institution_type = models.ForeignKey(InstitutionType, on_delete=models.CASCADE, blank=True, default='', null=True)
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
    # external_link = models.URLField(max_length=256, default='', blank=True) # It is replaced with ChurchLinkRelation in order to have multiple external links
    bibliography = models.ForeignKey(Bibliography, on_delete=models.CASCADE, blank=True, default='',
                                     null=True)  # this will not be
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies', blank=True, default='')
    description = models.TextField(default='', blank=True)
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    def __str__(self):
        return self.name


class Inscription(models.Model):
    reference_no = models.CharField(max_length=100, blank=False, default='')
    original_location = models.ForeignKey(Church, related_name='originallocationsinscription',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)
    original_location_city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, default='', null=True)
    original_location_region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, default='', null=True)
    current_location = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True, default='', null=True)
    current_location_museum = models.ForeignKey(Museum, on_delete=models.CASCADE, blank=True, default='', null=True)
    date_lower = PartialDateField(blank=True, null=True)
    date_upper = PartialDateField(blank=True, null=True)
    # external_link = models.URLField(max_length=256, default='', blank=True) # It is replaced with InscriptionLinkRelation in order to have multiple external links
    bibliography = models.ForeignKey(Bibliography, on_delete=models.SET_NULL, blank=True, default='',
                                     null=True)  # this will not be
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies_inscription', blank=True,
                                               default='')
    text = models.TextField(max_length=256, blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    def __str__(self):
        return self.reference_no


class SaintType(models.Model):
    name = models.CharField(max_length=100)  # Just Man, Confessor, Virgin, Virgin Confessor, Apostle, etc

    def __str__(self):
        return self.name


class Saint(models.Model):
    name = models.CharField(max_length=256)
    feast_day = models.CharField(max_length=256, blank=True, null=True)
    feast_day_old = PartialDateField(blank=True, null=True)
    death_date = PartialDateField(blank=True, null=True)
    death_place = models.CharField(max_length=256, blank=True, null=True)
    type = models.ForeignKey(SaintType, related_name='saints', on_delete=models.CASCADE, blank=True, default='',
                             null=True)
    # external_link = models.URLField(max_length=256, default='', blank=True) # It is replaced with SaintLinkRElation in order to have multiple external links
    description = models.TextField(default='', blank=True, null=True)
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    def __str__(self):
        return self.name


class ObjectType(models.Model):
    name = models.CharField(max_length=100)  #

    def __str__(self):
        return self.name


class Object(models.Model):
    name = models.CharField(max_length=256, blank=False, default='')
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
    # external_link = models.URLField(max_length=256, default='', blank=True) # It is replaced with ObjectLinkRelation in order to have multiple external links
    bibliography = models.ForeignKey(Bibliography, on_delete=models.CASCADE, blank=True, default='',
                                     null=True)  # this will not be
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies_object', blank=True,
                                               default='')
    description = models.TextField(default='', blank=True, null=True)
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    def __str__(self):
        return self.name


class ManuscriptType(models.Model):
    name = models.CharField(max_length=100)  # calendar, commicus, antiphoner, misticus, liber canticorum, etc

    def __str__(self):
        return self.name


class Rite(models.Model):
    name = models.CharField(max_length=100)  # old Hispanic, Roman

    def __str__(self):
        return self.name


class Feast(models.Model):
    name = models.CharField(max_length=100)  #
    date = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return self.name


class LiturgicalManuscript(models.Model):
    shelf_no = models.CharField(max_length=100, blank=False, default='')
    rite = models.ForeignKey(Rite, on_delete=models.SET_NULL, blank=True, default='', null=True)
    type = models.ForeignKey(ManuscriptType, on_delete=models.SET_NULL, blank=True, default='', null=True)
    date_lower = PartialDateField(blank=True, null=True)
    date_upper = PartialDateField(blank=True, null=True)
    original_location = models.ForeignKey(Church, related_name='originallocationslitman',
                                          on_delete=models.SET_NULL, blank=True, default='', null=True)
    original_location_city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, default='', null=True)
    original_location_region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, default='', null=True)
    provenance = models.ForeignKey(Church, on_delete=models.SET_NULL, blank=True, default='', null=True)
    provenance_museum = models.ForeignKey(Museum, on_delete=models.SET_NULL, blank=True, default='', null=True)
    feast = models.ForeignKey(Feast, on_delete=models.SET_NULL, blank=True, default='', null=True)
    # external_link = models.URLField(max_length=256, default='', blank=True) # It is replaced with litmanLinkRelation in order to have multiple external links
    bibliography = models.ForeignKey(Bibliography, on_delete=models.SET_NULL, blank=True, default='',
                                     null=True)  # this will not be
    # used in the future. I didn't delete this because there is data saved for some entries on the database.
    bibliography_many = models.ManyToManyField(Bibliography, related_name='bibliographies_litman', blank=True,
                                               default='')
    description = models.TextField(default='', blank=True, null=True)
    status = models.BooleanField("Completed", default=False, help_text="Complete")

    def __str__(self):
        return self.shelf_no


# RELATIONS
class ObjectChurchRelation(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE, blank=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    start_date = PartialDateField(blank=True, null=True)
    end_date = PartialDateField(blank=True, null=True)

    def __str__(self):
        message = self.object + "and" + self.church
        return message


class LitManuscriptChurchRelation(models.Model):
    liturgical_manuscript = models.ForeignKey(LiturgicalManuscript, on_delete=models.CASCADE, blank=True, null=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    start_date = PartialDateField(blank=True, null=True)
    end_date = PartialDateField(blank=True, null=True)

    def __str__(self):
        message = self.liturgical_manuscript + "and" + self.church
        return message


class SaintChurchRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = self.saint + "and" + self.church
        return message


class SaintInscriptionRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = self.saint + "and" + self.inscription
        return message


class SaintObjectRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    object = models.ForeignKey(Object, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = self.saint + "and" + self.object
        return message


class SaintLitManuscriptRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    liturgical_manuscript = models.ForeignKey(LiturgicalManuscript, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        message = self.saint + "and" + self.liturgical_manuscript
        return message


class InscriptionChurchRelation(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, blank=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    start_date = PartialDateField(blank=True, null=True)
    end_date = PartialDateField(blank=True, null=True)

    def __str__(self):
        message = self.inscription + "and" + self.church
        return message


# class ChurchObjectRelation(models.Model):
#     church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
#     object = models.ForeignKey(Object, on_delete=models.CASCADE, blank=True)
#
#     def __str__(self):
#         message = self.church + "and" + self.object
#         return message
#
#
# class ChurchLitManuscriptRelation(models.Model):
#     church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
#     liturgical_manuscript = models.ForeignKey(LiturgicalManuscript, on_delete=models.CASCADE, blank=True)
#
#     def __str__(self):
#         message = self.church + "and" + self.liturgical_manuscript
#         return message


# Multiple external links
class SaintLinkRelation(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=256, default='', blank=True)

    def __str__(self):
        message = self.saint + "and" + self.link
        return message


class ChurchLinkRelation(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=256, default='', blank=True)

    def __str__(self):
        message = self.church + "and" + self.link
        return message


class ObjectLinkRelation(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=256, default='', blank=True)

    def __str__(self):
        message = self.object + "and" + self.link
        return message


class InscriptionLinkRelation(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=256, default='', blank=True)

    def __str__(self):
        message = self.inscription + "and" + self.link
        return message


class LitManuscriptLinkRelation(models.Model):
    liturgical_manuscript = models.ForeignKey(LiturgicalManuscript, on_delete=models.CASCADE, blank=True)
    link = models.URLField(max_length=256, default='', blank=True)

    def __str__(self):
        message = self.liturgical_manuscript + "and" + self.link
        return message
