aws configure sso --use-device-code --profile emc-ai-poc

pkill uvicorn
cd /app
poetry run uvicorn serve:app --reload --host 0.0.0.0 --port 8052
