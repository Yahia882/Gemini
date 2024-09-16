from django.urls import include, path
from .views import webAppCreate,webAppDelete,webAppUpdate,webAppList , createpage,ListPages,retrievePage,feedbackPage,deletePage,profile,createPageCustomizedInput,extension #, currentpageview

urlpatterns = [
    path("CreateApp",view=webAppCreate.as_view()),
    path("<int:pk>/DeleteApp",view=webAppDelete.as_view()),
    #path("<int:pk>AppDetails",view=webAppDetail.as_view()),
    path("<int:pk>/UpdateApp",view=webAppUpdate.as_view()),
    path("ListApp",view=webAppList.as_view()),
    path("<int:pk>/createPage",view=createpage.as_view()),
    path("<int:pk>/ListPages",view=ListPages.as_view()),
    path("<int:pk>/<str:name>/retrievePage",view=retrievePage.as_view()),
    path("<int:pk>/<str:name>/feedbackPage",view=feedbackPage.as_view()),
    path("<int:pk>/<str:name>/deletePage",view=deletePage.as_view()),
    path("profile",view=profile.as_view()),
    path("<int:pk>/createCustominput",view=createPageCustomizedInput.as_view()),
    path("currentpage",view=extension.as_view()),
    # path("currentpageview",view=currentpageview.as_view()),
]
