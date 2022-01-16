from datetime import date
from django.contrib import admin
from django.apps import apps
from . import models
from django.db.models import F, ExpressionWrapper, DecimalField
# Register your models here.

# ------------------------ 1. 'User' model -----------------------------------

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    # Enable seaching by first and last name.
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

#------------------------------------------------------------------------------

# ------------------------- 2. 'Party' model ----------------------------------

# a. Custom Filtering : to filter parties which have been expired but not changed status.
class PartyFilter(admin.SimpleListFilter):
    title = 'expiration date'
    parameter_name = 'expiration-date'

    # Filter list UI
    def lookups(self, request, model_admin):
        return [
            ('gtcurrent', 'Past')
        ]
    
    # Implimentation of the filter, returns queryset to be displayed after filter.
    def queryset(self, request, queryset):
        if self.value() == 'gtcurrent':
            today = date.today()
            qs = queryset.filter(end_date__lt=today).exclude(status='P')
            return qs
            
# b. Register model
@admin.register(models.Party)
class PartyAdmin(admin.ModelAdmin):
    # For more option go to django adminModel > model options.

    actions = ['change_status_past']    # add your custom action function in the form of string here.
    exclude = ['total_cost', 'total_contribution', 'total_purchase', 'status']  # Exlude these attribute fields while adding a new party.
    fields = ['name', 'theme', 'venue', 'start_date', 'end_date', 'description', 'host'] # Include these attribute fields while adding a new party.
    list_display = ['name', 'theme', 'start_date', 'status']
    list_editable = ['theme']
    list_per_page = 10
    list_filter = ['start_date', 'status', 'theme', PartyFilter] # you can also create custom filtering class which are added to this list.. [Refer Pt.1 Admin > 10]
    search_fields = ['name__istartswith']     #searching with look up types

    # Custom action : perform custom action on selected parties.
    @admin.action(description='Change status to PAST')
    def change_status_past(self, request, queryset):
        updated_count = queryset.update(status='P')
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.'
        )

# -----------------------------------------------------------------------

# ------------------------- 3. 'Participant' model ----------------------

@admin.register(models.Participant)
class ParticipantAdmin(admin.ModelAdmin):
    autocomplete_fields = ['end_user']  # auto complete drop down (only works with forgein key relationships)
    list_display = ['user_name', 'end_user', 'party']    # computed column to view name of refered object
    list_per_page = 10
    list_select_related = ['end_user']  # prefetch related items to avoid iterative querying

    # defining a computed column where for each participant go to the related 'end_user' and fetch its first and last name.
    def user_name(self, participant):
        return participant.end_user.first_name + " " + participant.end_user.last_name

# ---------------------------------------------------------------------------

# -------------------------- 4. 'Item' model --------------------------------
    
@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'total_cost', 'category', 'party', 'for_all']
    list_editable = ['price', 'quantity', 'category']
    list_per_page = 10

    # Computed column while displaying a list of items. When sort depends on single column
    # @admin.display(ordering='price')
    # def total_cost(self, item):
    #     return item.price * item.quantity

    #Computed column with the feature to sort. when sort depend on multiple column
    @admin.display(ordering='total_cost')
    def total_cost(self, item):
        return item.total_cost

    #Overriding the queryset of the list page
    def get_queryset(self, request):
        qs = super().get_queryset(request)  #default queryset
        qs = qs.annotate(total_cost=ExpressionWrapper(F('price')*F('quantity'), output_field=DecimalField())) # annotate new column in existing queryset
        return qs

# --------------------------------------------------------------------------


# register all the models in the admin which are part of graphql auth.
app = apps.get_app_config('graphql_auth')

for model_name, model in app.models.items():
    admin.site.register(model)
