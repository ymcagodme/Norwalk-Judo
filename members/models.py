from django.db import models
from django import forms

class Member(models.Model):
    GENDER_CHOICE = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    GRADE_CHOICE = (
        ('1', '1st'),        
        ('2', '2nd'),        
        ('3', '3rd'),        
        ('4', '4th'),        
        ('5', '5th'),        
        ('6', '6th'),        
        ('7', '7th'),        
        ('8', '8th'),        
        ('9', '9th'),        
        ('10', '10th'),        
        ('11', '11th'),        
        ('12', '12th'),        
        ('college', 'College'),        
        ('adult', 'Adult'),        
    )
    avatar_img = models.ImageField(upload_to='avatar/', blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    birthday = models.DateField()
    grade = models.CharField(max_length=10, choices=GRADE_CHOICE, blank=True)
    email = models.EmailField(blank=True, null=True)
    joined_date = models.DateField('date joined', blank=True, null=True)
    emergency_number = models.CharField(max_length=20)
    activation = models.BooleanField()
    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

class Parent(models.Model):
    RELATIONSHIP_CHOICE = (
        ('mother', 'Mother'),        
        ('father', 'Father'),        
        ('grandmother', 'Grandmother'),        
        ('grandfather', 'Grandfather'),        
        ('sister', 'Sister'),        
        ('brother', 'Brother'),        
        ('uncle', 'Uncle'),        
        ('aunt', 'Aunt'),        
        ('cousin', 'Cousin'),        
        ('other', 'Other'),        
    )
    member = models.ForeignKey(Member)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=15, choices=RELATIONSHIP_CHOICE)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

class Tournament(models.Model):
    SCORE_CHOICE = (
        ('3', '1st'),        
        ('2', '2nd'),        
        ('1', '3rd'),        
        ('0.5', 'Other'),        
    )
    
    LEVEL_CHOICE = (
        ('local', 'Local'),        
        ('city', 'City'),        
        ('state', 'State'),        
        ('national', 'National'),
        ('international', 'International'),        
    )

    BELT_COLOR_CHOICE = (
        ('white', 'White'),        
        ('yellow', 'Yellow'),        
        ('orange', 'Orange'),        
        ('green', 'Green'),        
        ('blue', 'Blue'),        
        ('purple', 'Purple'),        
        ('brown', 'Brown'),        
        ('black', 'Black'),        
    )
    member = models.ForeignKey(Member)
    title = models.CharField(max_length=50)
    score = models.CharField(max_length=10, choices=SCORE_CHOICE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICE)
    hosted_date = models.DateField('date hosted')
    belt_color = models.CharField(max_length=15, choices=BELT_COLOR_CHOICE)

class Membership_fee(models.Model):
    member = models.ForeignKey(Member)
    amount = models.IntegerField()
    paid_date = models.DateField('date paid', blank=True, null=True)
    due_date = models.DateField('date due')
    status = models.BooleanField()

class USJF_membership(models.Model):
    member = models.ForeignKey(Member)
    number = models.CharField(max_length=30)
    expired_date = models.DateField('date expired')
    renew_status = models.BooleanField()

class Last_modify_ip(models.Model):
    member = models.ForeignKey(Member)
    pub_date = models.DateTimeField('date modified')
    ip = models.IPAddressField()

class Address(models.Model):
    STATES_CHOICE = (
        ('AK', 'Alaska'),        
        ('AL', 'Alabama'),        
        ('AR', 'Arkansas'),        
        ('AS', 'American Samoa'),        
        ('AZ', 'Arizona'),        
        ('CA', 'California'),        
        ('CO', 'Colorado'),        
        ('CT', 'Connecticut'),        
        ('DC', 'District of Columbia'),        
        ('DE', 'Delaware'),        
        ('FL', 'Florida'),        
        ('GA', 'Georgia'),        
        ('GU', 'Guam'),        
        ('HI', 'Hawaii'),        
        ('IA', 'IOWA'),        
        ('ID', 'IDAHO'),        
        ('IL', 'Illinois'),        
        ('IN', 'Indiana'),        
        ('KS', 'Kansas'),        
        ('KY', 'Kentucky'),        
        ('LA', 'Louisiana'),        
        ('MA', 'Massachusetts'),        
        ('MD', 'Maryland'),        
        ('ME', 'Maine'),        
        ('MI', 'Michigan'),        
        ('MN', 'Minnesota'),        
        ('MO', 'Missouri'),        
        ('MP', 'Northern Mariana Islands'),        
        ('MS', 'Mississippi'),        
        ('MT', 'Montana'),        
        ('NC', 'North Carolina'),        
        ('ND', 'North Dakota'),        
        ('NE', 'Nebraska'),        
        ('NH', 'New Hampshire'),        
        ('NJ', 'New Jersey'),        
        ('NM', 'New Mexico'),        
        ('NV', 'Nevada'),        
        ('NY', 'New York'),        
        ('OH', 'Ohio'),        
        ('OK', 'Oklahoma'),        
        ('OR', 'Oregon'),        
        ('PA', 'Pennsylvania'),        
        ('PR', 'Puerto Rico'),        
        ('RI', 'Rhode Island'),        
        ('SC', 'South Carolina'),        
        ('SD', 'South Dakota'),        
        ('TN', 'Tennessee'),        
        ('TX', 'Texas'),        
        ('UT', 'Utah'),        
        ('VA', 'Virginia'),        
        ('VI', 'Virgin Islans'),        
        ('VT', 'Vermont'),        
        ('WA', 'Washington'),        
        ('WI', 'Wisconsin'),        
        ('WV', 'West Virginia'),        
        ('WY', 'Wyoming'),        
    )

    COUNTRIES_CHOICE = (
        ('USA', 'United States'),
    )
    member = models.ForeignKey(Member)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=25)
    state = models.CharField(max_length=5, choices=STATES_CHOICE)
    postal = models.CharField(max_length=10)
    country = models.CharField(max_length=20, choices=COUNTRIES_CHOICE)

class Phone(models.Model):
    PHONE_TYPE_CHOICE = (
        ('home', 'Home'), 
        ('mobile', 'Mobile'), 
        ('office', 'Office'), 
        ('other', 'Other'), 
    )
    member = models.ForeignKey(Member)
    phone_type = models.CharField(max_length=10, choices=PHONE_TYPE_CHOICE,blank=True)
    phone_number = models.CharField(max_length=15)
    ext = models.CharField(max_length=10, blank=True, null=True)
    preferred = models.BooleanField(blank=True)

class Belt(models.Model):
    BELT_COLOR_CHOICE = (
        ('white', 'White'),        
        ('yellow', 'Yellow'),        
        ('orange', 'Orange'),        
        ('green', 'Green'),        
        ('blue', 'Blue'),        
        ('purple', 'Purple'),        
        ('brown', 'Brown'),        
        ('black', 'Black'),        
    )
    member = models.ForeignKey(Member)
    color = models.CharField(max_length=15, choices=BELT_COLOR_CHOICE)
    completed_date = models.DateField('date completed')


class Announce(models.Model):
    pub_date = models.DateTimeField('Publish Date')
    ip = models.IPAddressField()
    subject = models.CharField(max_length=50)
    body = models.TextField()
    def __unicode__(self):
        return '%s' % (self.subject, )

class Notification(models.Model):
    NOTIFICATION_CHOICE = (
        ('usjf', 'USJF Membership'),
        ('m_fee', 'Membership Fee'),
    )
    event = models.CharField(max_length=20, choices=NOTIFICATION_CHOICE)
    days = models.PositiveIntegerField()
    repetitive = models.BooleanField()
    def __unicode__(self):
        return '%s' % (self.event, )
