from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма создания/редактирования поста."""

    class Meta:

        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):

        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Постов без текста не бывает...')
        return data


class CommentForm(forms.ModelForm):
    """Форма комментариев."""

    class Meta:

        model = Comment
        fields = ('text',)

    def clean_text(self):

        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Комментариев без текста не бывает...')
        return data
