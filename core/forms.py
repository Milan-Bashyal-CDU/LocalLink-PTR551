from django import forms
from .models import HelpRequest, Offer, Review, Message


class _BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs['class'] = (widget.attrs.get('class', '') + ' form-check-input').strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = (widget.attrs.get('class', '') + ' form-select').strip()
            else:
                widget.attrs['class'] = (widget.attrs.get('class', '') + ' form-control').strip()


class HelpRequestForm(_BootstrapMixin, forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ['title', 'category', 'description', 'suburb',
                  'is_remote_ok', 'urgency', 'preferred_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
        }


class OfferForm(_BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4})}


class ReviewForm(_BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 3})}


class MessageForm(_BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {'body': forms.Textarea(attrs={'rows': 2,
                   'placeholder': 'Write a message…'})}
