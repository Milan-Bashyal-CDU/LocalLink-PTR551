from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import HelpRequestForm, OfferForm, ReviewForm, MessageForm
from .models import Category, HelpRequest, Offer, Review


def home(request):
    categories = Category.objects.all()
    recent = HelpRequest.objects.filter(status=HelpRequest.STATUS_OPEN)[:6]
    stats = {
        'open_requests': HelpRequest.objects.filter(status=HelpRequest.STATUS_OPEN).count(),
        'completed': HelpRequest.objects.filter(status=HelpRequest.STATUS_COMPLETED).count(),
        'categories': categories.count(),
    }
    return render(request, 'home.html',
                  {'categories': categories, 'recent': recent, 'stats': stats})


def request_list(request):
    qs = HelpRequest.objects.filter(status=HelpRequest.STATUS_OPEN)
    category = request.GET.get('category')
    suburb = request.GET.get('suburb')
    query = request.GET.get('q')
    if category:
        qs = qs.filter(category__slug=category)
    if suburb:
        qs = qs.filter(suburb__icontains=suburb)
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return render(request, 'core/request_list.html', {
        'requests': qs, 'categories': Category.objects.all(),
        'selected_category': category, 'suburb': suburb or '', 'query': query or ''})


def request_detail(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk)
    user = request.user
    user_offer = None
    can_offer = False
    if user.is_authenticated and user.is_helper and user != help_request.seeker:
        user_offer = help_request.offers.filter(helper=user).first()
        can_offer = (help_request.status == HelpRequest.STATUS_OPEN and user_offer is None)
    is_party = user.is_authenticated and user in (help_request.seeker, help_request.helper)
    thread = help_request.messages.select_related('sender') if is_party else None
    can_review = (is_party and help_request.status == HelpRequest.STATUS_COMPLETED
                  and not help_request.has_review_from(user))
    return render(request, 'core/request_detail.html', {
        'req': help_request, 'user_offer': user_offer, 'can_offer': can_offer,
        'offer_form': OfferForm(), 'message_form': MessageForm(),
        'thread': thread, 'can_review': can_review})


@login_required
def request_create(request):
    if not request.user.is_seeker:
        messages.warning(request, 'Only Support Seeker accounts can post requests.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.seeker = request.user
            obj.save()
            messages.success(request, 'Your request has been posted.')
            return redirect(obj.get_absolute_url())
    else:
        form = HelpRequestForm(initial={'suburb': request.user.suburb})
    return render(request, 'core/request_form.html', {'form': form})


@login_required
def offer_create(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk)
    if not request.user.is_helper:
        messages.warning(request, 'Only Helper accounts can make offers.')
        return redirect(help_request.get_absolute_url())
    if help_request.status != HelpRequest.STATUS_OPEN:
        messages.warning(request, 'This request is no longer open.')
        return redirect(help_request.get_absolute_url())
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer, created = Offer.objects.get_or_create(
                request=help_request, helper=request.user,
                defaults={'message': form.cleaned_data['message']})
            if created:
                messages.success(request, 'Your offer has been sent to the seeker.')
            else:
                messages.info(request, 'You have already offered to help with this request.')
    return redirect(help_request.get_absolute_url())


@login_required
def offer_accept(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    help_request = offer.request
    if request.user != help_request.seeker:
        raise PermissionDenied
    offer.status = Offer.STATUS_ACCEPTED
    offer.save()
    help_request.helper = offer.helper
    help_request.status = HelpRequest.STATUS_IN_PROGRESS
    help_request.save()
    # decline the rest
    help_request.offers.exclude(pk=offer.pk).update(status=Offer.STATUS_DECLINED)
    messages.success(request, f'{offer.helper.get_full_name() or offer.helper.username} is now helping you.')
    return redirect(help_request.get_absolute_url())


@login_required
def request_complete(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk)
    if request.user not in (help_request.seeker, help_request.helper):
        raise PermissionDenied
    help_request.status = HelpRequest.STATUS_COMPLETED
    help_request.save()
    messages.success(request, 'Request marked as completed. You can now leave a review.')
    return redirect(help_request.get_absolute_url())


@login_required
def request_cancel(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk)
    if request.user != help_request.seeker:
        raise PermissionDenied
    help_request.status = HelpRequest.STATUS_CANCELLED
    help_request.save()
    messages.info(request, 'Request cancelled.')
    return redirect('dashboard')


@login_required
def review_create(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk)
    if request.user not in (help_request.seeker, help_request.helper):
        raise PermissionDenied
    if help_request.status != HelpRequest.STATUS_COMPLETED:
        messages.warning(request, 'You can only review a completed request.')
        return redirect(help_request.get_absolute_url())
    reviewee = help_request.helper if request.user == help_request.seeker else help_request.seeker
    if help_request.has_review_from(request.user):
        messages.info(request, 'You have already left a review for this request.')
        return redirect(help_request.get_absolute_url())
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.request = help_request
            review.reviewer = request.user
            review.reviewee = reviewee
            review.save()
            messages.success(request, 'Thank you for your feedback.')
            return redirect(help_request.get_absolute_url())
    else:
        form = ReviewForm()
    return render(request, 'core/review_form.html',
                  {'form': form, 'req': help_request, 'reviewee': reviewee})


@login_required
def message_create(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk)
    if request.user not in (help_request.seeker, help_request.helper):
        raise PermissionDenied
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.request = help_request
            msg.sender = request.user
            msg.save()
    return redirect(help_request.get_absolute_url())
