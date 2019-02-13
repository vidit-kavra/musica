from django.urls import path
from . import views

app_name = 'music'  # namespace

urlpatterns = [
    # music/
    path('', views.index, name='index'),

    # music/register/
    path('register/', views.register, name='register'),

    # music/login_user/
    path('login_user', views.login_user, name='login_user'),

    # music/logout_user/
    path('logout_user', views.logout_user, name='logout_user'),

    # music/pk/
    path('<int:album_id>/', views.detail, name='detail'),

    # music/songs/all/ or music/songs/favorites/
    path('songs/<str:filter_by>/', views.songs, name='songs'),

    # music/song_id/favorite/
    path('<int:song_id>/favorite/', views.favorite, name='favorite'),

    # music/album_id/favorite/
    path('<int:album_id>/favorite_album/', views.favorite_album, name='favorite_album'),

    # music/songs/song_id/all/ or /favorites/
    path('songs/<int:song_id>/<str:filter_by>/', views.favorite_songs, name='favorite_songs'),

    # music/pk/create_song/
    path('<int:album_id>/create_song/', views.create_song, name='create_song'),

    # music/create_album/
    path('create_album/', views.create_album, name='create_album'),

    # music/album/pk/delete/
    path('<int:album_id>/delete/<int:song_id>/', views.delete_song, name='song_delete'),

    # music/album/pk/delete/
    path('album/<int:album_id>/delete/', views.delete_album, name='album_delete'),
]
