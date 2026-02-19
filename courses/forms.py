from django import forms
from .models import Folder, Course, Card

LANGUAGE_CHOICES = [
    ('ru', '🇷🇺 Русский'),
    ('en', '🇬🇧 English'),
    ('de', '🇩🇪 Deutsch'),
    ('fr', '🇫🇷 Français'),
    ('es', '🇪🇸 Español'),
    ('kk', '🇰🇿 Қазақша'),
    ('ky', '🏔️ Кыргызча'),
    ('zh', '🇨🇳 中文'),
    ('ja', '🇯🇵 日本語'),
    ('ar', '🇸🇦 العربية'),
]


class FolderForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Название папки', 'class': 'form-input'})
    )

    class Meta:
        model = Folder
        fields = ['title']


class CourseForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Название курса', 'class': 'form-input'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Описание (необязательно)', 'class': 'form-input', 'rows': 3})
    )
    front_language = forms.ChoiceField(choices=LANGUAGE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    back_language = forms.ChoiceField(choices=LANGUAGE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))

    class Meta:
        model = Course
        fields = ['title', 'description', 'front_language', 'back_language', 'folder']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['folder'].queryset = Folder.objects.filter(user=user)
        self.fields['folder'].required = False
        self.fields['folder'].widget.attrs['class'] = 'form-input'
        self.fields['folder'].empty_label = 'Без папки'


class CardForm(forms.ModelForm):
    front_text = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Слово или фраза', 'class': 'form-input card-front-input'})
    )
    back_text = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Перевод', 'class': 'form-input card-back-input'})
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Card
        fields = ['front_text', 'back_text', 'image']