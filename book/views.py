from django.shortcuts import render,redirect
from django.views.generic import ListView,DetailView,CreateView,DeleteView,UpdateView
from .models import Book,Review
from django.urls import reverse,reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from django.core.paginator import Paginator
from .consts import ITEM_PER_PAGE
from .forms import SearchForm




class ListBookView(LoginRequiredMixin,ListView):
    object_list=Book.objects.order_by('-id')[:5]
    template_name='book/book_list.html'
    model = Book
    paginate_by=ITEM_PER_PAGE
    # context_object_name='new_name'

class DetailBookView(LoginRequiredMixin,DetailView):
    template_name='book/book_detail.html'
    model=Book

class CreateBookView(LoginRequiredMixin,CreateView):
    template_name='book/book_create.html'
    model=Book
    fields=('title','text','category','thumbnail')
    success_url=reverse_lazy('list-book')

    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DeleteBookView(LoginRequiredMixin,DeleteView):
    template_name='book/book_confirm_delete.html'
    model=Book
    success_url=reverse_lazy('list-book')

    def get_object(self,queryset=None):
        obj=super().get_object(queryset)

        if obj.user != self.request.user:
            raise PermissionDenied

            return obj


class UpdateBookView(LoginRequiredMixin,UpdateView):
    template_name='book/book_confirm_update.html'
    model=Book
    fields=('title','text','category','thumbnail')

    def get_object(self,queryset=None):
        obj=super().get_object(queryset)

        if obj.user != self.request.user:
            raise PermissionDenied

            return obj
    
    def get_success_url(self):
        return reverse('detail-book',kwargs={'pk':self.object.id})


def index_view(request):
    searchForm = SearchForm(request.GET)
    avg_rating = Avg('review__rate')
    
    # 基本のクエリセット
    object_list = Book.objects.annotate(avg_rating=avg_rating)
    
    if searchForm.is_valid():
        # 検索キーワードによるフィルタリング
        keyword = searchForm.cleaned_data.get('keyword', '')
        if keyword:
            object_list = object_list.filter(title__contains=keyword)
        
        # ソート処理
        sort = searchForm.cleaned_data.get('sort', '')
        if sort:
            if sort == 'title':
                object_list = object_list.order_by('title')
            elif sort == 'rating':
                object_list = object_list.order_by('-avg_rating')
            elif sort == 'created':
                object_list = object_list.order_by('-id')
            elif sort == 'created-reverse':
                object_list = object_list.order_by('id')
    else:
        object_list = object_list.order_by('-id')  # デフォルトは登録順
    
    # ランキングリストの処理（変更なし）
    ranking_list = Book.objects.annotate(avg_rating=avg_rating).order_by('-avg_rating')
    paginator = Paginator(ranking_list, ITEM_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.page(page_number)

    return render(
        request, 
        'book/index.html',
        {
            'object_list': object_list,
            'ranking_list': ranking_list,
            'page_obj': page_obj,
            'searchForm': searchForm,
        }
    )

class CreateReviewView(LoginRequiredMixin,CreateView):
    model=Review
    fields=('book','title','text','rate')
    template_name='book/review_form.html'
    success_url=reverse_lazy('list-book')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['book']=Book.objects.get(pk=self.kwargs['book_id'])
        return context

    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('detail-book',kwargs={'pk':self.object.book.id})

