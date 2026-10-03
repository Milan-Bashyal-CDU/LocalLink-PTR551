from django.contrib import admin
from .models import Category, HelpRequest, Offer, Review, Message


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class OfferInline(admin.TabularInline):
    model = Offer
    extra = 0


@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'seeker', 'category', 'suburb', 'urgency', 'status', 'created_at')
    list_filter = ('status', 'urgency', 'category', 'suburb')
    search_fields = ('title', 'description', 'seeker__username')
    inlines = [OfferInline]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('request', 'helper', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewee', 'reviewer', 'rating', 'request', 'created_at')
    list_filter = ('rating',)


admin.site.register(Message)
admin.site.site_header = 'LocalLink Administration'
admin.site.site_title = 'LocalLink Admin'
