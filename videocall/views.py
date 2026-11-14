from django.shortcuts import render,redirect

# Create your views here.

def home(request):
    if request.method == "POST":
        room = request.POST.get("room", "").strip()
        if room:
            return redirect("room", room_name=room)
    return render(request, "videocall/home.html")


def room(request, room_name):
    return render(request, "videocall/room.html", {"room_name": room_name})