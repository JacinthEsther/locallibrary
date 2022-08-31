from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import render

# Create your views here.
from django.views import generic, View

from catalog.models import Author, BookInstance, Book


def index(request):
    """View function for home page of site."""
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    context_object_name = 'book_list'  # your own name for the list as a template variable

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

    # queryset = Book.objects.filter(title__icontains='war')[:5]
    # Get 5 books containing the title war

    def get_queryset(self):
        return Book.objects.filter(title__icontains='war')[:5]

    template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location


class MyView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    # Or multiple permissions
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')


class BookDetailView(generic.ListView):
    model = Book

    def book_detail_view(request, primary_key):
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise Http404('Book does not exist')

        return render(request, 'book_detail.html', context={'book': book})


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


def renew_book_librarian(request):
    return None