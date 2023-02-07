from django import forms

from .models import Comment, Post, Word


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        words = Word.objects.all()
        data = self.cleaned_data['text']
        for word in words:
            if word.word in data.lower():
                raise forms.ValidationError(
                    f'Вы использовали запретное слово «{word.word}»!'
                )
        return data
