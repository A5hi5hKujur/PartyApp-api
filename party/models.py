from django.db import models
from django.contrib.auth.models import AbstractUser # inherit your new user schema from the existing user schema provided by django
from datetime import date

# End User Model (Inherited user model)
class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    image = models.CharField(max_length=255, null=True, blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.username


# Party Model
class Party(models.Model):
    PAST_STATUS = 'P'
    ONGOING_STATUS = 'O'
    UPCOMING_STATUS = 'U'
    STATUS_CHOICES = [
        (PAST_STATUS, 'Past'),
        (ONGOING_STATUS, 'Ongoing'),
        (UPCOMING_STATUS, 'Upcoming')
    ]

    THEME_CHOICES = [
        ('Anniversary', 'Anniversary'),
        ('Birthday', 'Birthday'),
        ('Casual', 'Casual'),
        ('Formal','Formal')
    ]
    name = models.CharField(max_length=50)
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default=THEME_CHOICES[2][0])
    venue = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    total_cost = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    total_contribution = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    total_purchase = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True)
    host = models.ForeignKey('Participant', on_delete=models.PROTECT, blank=True, null=True, related_name='host_of')    # One party can have 1 host which would be a participant.
    #participant_set : Django will automatically make to connect participants with party.
    #item_set : Django will automatically make to connect items with party.

    def __str__(self):
        return self.name

    #Override the save() to check the event date and then update the status of the event.
    def save(self, *args, **kwargs):
        today = date.today()
        if(self.end_date == None):
            self.end_date = self.start_date

        if(today < self.start_date):
            self.status = self.UPCOMING_STATUS
        elif(today >= self.start_date and today <= self.end_date):
            self.status = self.ONGOING_STATUS
        else:
            self.status = self.PAST_STATUS

        super(Party, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name']     # Orders this model in the super admin panel by name.

# Party Participant Model
class Participant(models.Model):
    end_user = models.ForeignKey(User, on_delete=models.PROTECT) #This participant will prevent the mapped user from begin deleted
    contribution = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=7, decimal_places=2, default=0)    
    party = models.ForeignKey(Party, on_delete=models.PROTECT) # One instance of participant can only participate in one Party (there can exist multiple instances of a participant)
    
    def __str__(self):
        return self.end_user.first_name + " " + self.end_user.last_name


# Item Model 
class Item(models.Model):
    CATEGORY_CHOICES = [
        ('beer', 'Beer'),
        ('board-game', 'Board Game'),
        ('cake', 'Cake'),
        ('card', 'Cards'),
        ('cup', 'Cups'),
        ('decoration', 'Decorations'),
        ('food', 'Food'), 
        ('fruit-vegetable','Fruits and Vegetables'),
        ('celebration-item', 'Celebration Aid'),
        ('pizza', 'Pizza'),
        ('soft-drink', 'Soft Drink'),
        ('video-game','Video Game'),
        ('water', 'Water'),
        ('wine', 'Wine')
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    priority = models.PositiveSmallIntegerField(blank=True, null=True)
    purchased = models.BooleanField(blank=True, default=False)
    essential = models.BooleanField(blank=True, default=False)
    for_all = models.BooleanField(blank=True, default=True)
    party = models.ForeignKey(Party, on_delete=models.PROTECT) # An instance of an item can only exist in a single party.
    consumers = models.ManyToManyField(Participant) # MANY participants can consume a single instance of item

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']