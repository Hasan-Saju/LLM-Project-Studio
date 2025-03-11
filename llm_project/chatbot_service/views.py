from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage
from config import SERVICE_DISCOVER_GRAMMAR, DEEPSEEK_CHAT_URL
import requests
from django.views.decorators.csrf import csrf_exempt
import json
import re

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("chat")
        else:
            print("NO user found")
            # messages.error(request, "No user found. Please register first.")
            return render(request, "login.html", {"error": "User not registered. Please register first."})
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

        # Send message to Grammar Service first
        grammar_response = requests.post(SERVICE_DISCOVER_GRAMMAR, json={
            "target_service": "grammar_service",
            "payload": {"message": user_message}
        })

        print("User Message:", user_message)
        print("Grammar response status:", grammar_response.status_code)
        print("Grammar response text:", grammar_response.text)

        if grammar_response.status_code != 200:
            return JsonResponse({"error": "Failed to process message"}, status=500)

        try:
            grammar_data = grammar_response.json()  
            fixed_message = grammar_data.get("fixed_message", user_message)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON response from Grammar Service"}, status=500)

        print("Fixed Message destruc:", fixed_message)
        # Save fixed message
        ChatMessage.objects.create(session=session, sender="user", message=fixed_message)


        previous_messages = ChatMessage.objects.filter(session=session).order_by("timestamp")[:10]
        chat_history = ""
        for msg in previous_messages:
            chat_history += f"{msg.sender}: {msg.message}\n"

        # Append the new user message
        chat_history += f"User: {fixed_message}\n"

        # Save user message to database
        # ChatMessage.objects.create(session=session, sender="user", message=fixed_message)
        # Send to LLM (DeepSeek R1)
        response = requests.post(DEEPSEEK_CHAT_URL, json={
            "model": "deepseek-r1",
            "prompt": chat_history,
            "stream": False
        })

        if response.status_code != 200:
            return JsonResponse({"error": f"Ollama API error {response.status_code}: {response.text}"}, status=500)

        try:
            bot_message = response.json().get("response", "I'm not sure how to respond.")
            bot_message = process_response_message(bot_message)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON response from LLM"}, status=500)

        ChatMessage.objects.create(session=session, sender="bot", message=bot_message)

        return JsonResponse({"user_message": fixed_message, "bot_message": bot_message})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def chat_history(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = ChatMessage.objects.filter(session=session)
    return JsonResponse({"messages": list(messages.values())})

def process_response_message(text):
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()