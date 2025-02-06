from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage
import requests, json

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("chat")
    # TODO: Throw an error msg that this user is not rregistered
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("chat")
    return render(request, "register.html")

@login_required
def chat(request):
    sessions = ChatSession.objects.filter(user=request.user)
    return render(request, "chat.html", {"sessions": sessions})

@login_required
def create_session(request):
    if request.method == "POST":
        session_name = request.POST["session_name"]
        session = ChatSession.objects.create(user=request.user, session_name=session_name)
        return redirect(f"/chat/{session.id}/")
    return render(request, "create_session.html")

@login_required
def chat_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = ChatMessage.objects.filter(session=session)
    return render(request, "chat_session.html", {"session": session, "messages": messages})

@login_required
def send_message(request, session_id):
    if request.method == "POST":
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        user_message = request.POST["message"]

        # Fetch previous chat history for context (last 10 messages for brevity)
        previous_messages = ChatMessage.objects.filter(session=session).order_by("timestamp")[:10]

        # Build the conversation history
        chat_history = ""
        for msg in previous_messages:
            chat_history += f"{msg.sender}: {msg.message}\n"

        # Append the new user message
        chat_history += f"User: {user_message}\n"

        # Save user message to database
        ChatMessage.objects.create(session=session, sender="user", message=user_message)

        try:
            response = requests.post(f"{settings.OLLAMA_API_URL}/api/generate", json={
                "model": "deepseek-r1",
                "prompt": chat_history,  # Sending full conversation context
                "stream": False  # Ensures we get a full response
            })

            # Ensure request was successful
            if response.status_code != 200:
                return JsonResponse({"error": f"Ollama API error {response.status_code}: {response.text}"}, status=500)

            # Extract and store the bot's response
            response_data = response.json()
            bot_message = response_data.get("response", "I'm not sure how to respond.")

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Request failed: {str(e)}"}, status=500)

        # Save bot response to database
        ChatMessage.objects.create(session=session, sender="bot", message=bot_message)

        return JsonResponse({"user_message": user_message, "bot_message": bot_message})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def chat_history(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = ChatMessage.objects.filter(session=session)
    return JsonResponse({"messages": list(messages.values())})
