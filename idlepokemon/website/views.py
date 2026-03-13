from django.views.generic import TemplateView

class HomeView(TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['website/userLoggedIn.html']
        return ['website/home.html']