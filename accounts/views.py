from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, ProfileForm
from .models import CustomUser
from core.models import HelpRequest, Offer, Review


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to LocalLink! Your account is ready.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    context = {}
    if user.is_seeker:
        context['my_requests'] = HelpRequest.objects.filter(seeker=user).order_by('-created_at')
        context['open_offers'] = Offer.objects.filter(
            request__seeker=user, status=Offer.STATUS_PENDING)
    if user.is_helper:
        context['my_offers'] = Offer.objects.filter(helper=user).order_by('-created_at')
        context['assigned'] = HelpRequest.objects.filter(helper=user).exclude(
            status=HelpRequest.STATUS_COMPLETED)
        context['available'] = HelpRequest.objects.filter(
            status=HelpRequest.STATUS_OPEN).order_by('-created_at')[:5]
    if user.is_coordinator:
        context['total_requests'] = HelpRequest.objects.count()
        context['open_requests'] = HelpRequest.objects.filter(
            status=HelpRequest.STATUS_OPEN).count()
        context['total_helpers'] = CustomUser.objects.filter(
            role=CustomUser.ROLE_HELPER).count()
        context['unverified'] = CustomUser.objects.filter(
            role=CustomUser.ROLE_HELPER, is_verified=False)
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile(request, username=None):
    if username:
        profile_user = get_object_or_404(CustomUser, username=username)
    else:
        profile_user = request.user
    reviews = Review.objects.filter(reviewee=profile_user).order_by('-created_at')
    editable = profile_user == request.user
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user, 'reviews': reviews, 'editable': editable})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})
