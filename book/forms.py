from django import forms

class SearchForm(forms.Form):
    keyword = forms.CharField(label='検索', max_length=100, required=False)
    sort = forms.ChoiceField(
        label='並び順',
        required=False,
        choices=[
            ('', '選択...'),
            ('title', 'タイトル順'),
            ('rating', '評価順'),
            ('created', '新しい順'),
            ('created-reverse', '古い順'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )