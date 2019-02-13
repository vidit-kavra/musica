from .models import Album, Song
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm, SongForm, AlbumForm
from django.db.models import Q

AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def index(request):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        all_albums = Album.objects.filter(user=request.user)
        song_results = Song.objects.all()
        query = request.GET.get('q')
        if query:
            all_albums = all_albums.filter(
                Q(album_title__icontains=query) |
                Q(artist__icontains=query)
            ).distinct()
            song_results = song_results.filter(
                Q(song_title__icontains=query)
            ).distinct()
            return render(request, 'music/index.html', {
                'all_albums' : all_albums,
                'songs' : song_results,
            })
        else:
            return render(request, 'music/index.html', {'all_albums': all_albums})


def detail(request, album_id):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        user = request.user
        album = get_object_or_404(Album, pk=album_id)
        return render(request, 'music/detail.html', {'album': album, 'user': user})


def create_album(request):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.album_logo = request.FILES["album_logo"]
            file_type = album.album_logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Image file must be JPG, PNG, or JPEG',
                }
                return render(request, 'music/create_album.html', context)
            album.save()
            return render(request, 'music/detail.html', {'album': album})
        context = {
            "form": form
        }
        return render(request, 'music/create_album.html', context)


def delete_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    album.delete()
    all_albums = Album.objects.filter(user=request.user)
    return render(request, 'music/index.html', {'all_albums': all_albums})


def delete_song(request, album_id, song_id):
    album = get_object_or_404(Album, pk=album_id)
    song = album.song_set.filter(pk=song_id)
    song.delete()
    return render(request, 'music/detail.html', {'album': album})


def create_song(request, album_id):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = SongForm(request.POST or None, request.FILES or None)
        album = get_object_or_404(Album, pk=album_id)
        if form.is_valid():
            albums_songs = album.song_set.all()
            for s in albums_songs:
                if s.song_title == form.cleaned_data.get("song_title"):
                    context = {
                        'album': album,
                        'form': form,
                        'error_message': 'You already added that song',
                    }
                    return render(request, 'music/create_song.html', context)
            song = form.save(commit=False)
            song.album = album
            song.audio_file = request.FILES['audio_file']
            file_type = song.audio_file.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in AUDIO_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Audio file must be WAV, MP3, or OGG',
                }
                return render(request, 'music/create_song.html', context)
            song.save()
            return render(request, 'music/detail.html', {'album': album})
        context = {
            'album': album,
            'form': form,
        }
        return render(request, 'music/create_song.html', context)


def songs(request, filter_by):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        try:
            song_ids = []
            for album in Album.objects.filter(user=request.user):
                for song in album.song_set.all():
                    song_ids.append(song.pk)
            users_songs = Song.objects.filter(pk__in=song_ids)
            if filter_by == 'favorites':
                users_songs = users_songs.filter(is_favorite=True)
        except Album.DoesNotExist:
            users_songs = []
        return render(request, 'music/songs.html', {
            'song_list': users_songs,
            'filter_by': filter_by,
        })


def favorite(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    album = song.album
    if song.is_favorite:
        song.is_favorite = False
    else:
        song.is_favorite = True
    song.save()
    return render(request, 'music/detail.html', {'album': album})


def favorite_songs(request, song_id, filter_by):
    song = get_object_or_404(Song, pk=song_id)
    if song.is_favorite:
        song.is_favorite = False
    else:
        song.is_favorite = True
    song.save()
    return songs(request, filter_by)


def favorite_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    all_albums = Album.objects.all()
    if album.is_favorite:
        album.is_favorite = False
    else:
        album.is_favorite = True
    album.save()
    return render(request, 'music/index.html', {'all_albums': all_albums})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                all_albums = Album.objects.filter(user=request.user)
                return render(request, 'music/index.html', {'all_albums': all_albums})
            else:
                return render(request, 'music/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'music/login.html', {'error_message': 'Invalid Login'})
    return render(request, 'music/login.html')


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    return render(request, 'music/login.html', {'form': form})


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                all_albums = Album.objects.filter(user=request.user)
                return render(request, 'music/index.html', {'all_albums': all_albums})
    return render(request, 'music/registration_form.html', {'form': form})


# def favorite(request,album_id):
#    album = get_object_or_404(Album, pk=album_id)
#    try:
#        selected_song = album.song_set.get(pk=request.POST['song'])
#    except(KeyError,Song.DoesNotExist):
#        return render(request, 'music/detail.html', {
#            'album':album,
#            'error_message': "You did not select a valid song."
#        })
#    else:
#        selected_song.is_favorite = True;
#        selected_song.save()
#        return render(request, 'music/detail.html', {'album' : album} )
