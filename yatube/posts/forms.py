from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Картинка'
        }
        help_texts = {
            'text': 'Текст вашего поста нужно писать здесь',
            'group': 'Группа, к которой относится этот пост',
            'image': 'Дополните свой пост картинкой'
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Комментарий',
        }
        help_texts = {
            'text': 'Напишите свой комментарий',
        }
