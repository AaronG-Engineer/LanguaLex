import boto3

# 🌍 Language translation service wrapped with better error handling & optimization
def lambda_handler(event, context):
    try:
        # Validate sessionState existence
        session_data = event.get("sessionState", {}).get("intent", {})
        slots = session_data.get("slots", {})

        # Extract and sanitize input text
        input_text = slots.get("text", {}).get("value", {}).get("interpretedValue", "").strip()
        if not input_text:
            raise ValueError("Missing or empty input text.")

        # Extract language selection
        language_slot = slots.get("language", {}).get("value", {}).get("interpretedValue", "").strip()
        if not language_slot:
            raise ValueError("Missing or empty language selection.")

        # 🔡 Define supported languages
        supported_languages = {
            'French': 'fr', 'Japanese': 'ja', 'Chinese': 'zh',
            'Spanish': 'es', 'German': 'de', 'Norwegian': 'no'
        }

        # Check if language is supported
        target_language_code = supported_languages.get(language_slot)
        if not target_language_code:
            raise ValueError(f"Unsupported language: {language_slot}")

        # ⚡ Translation API Call
        translate_client = boto3.client("translate")
        response = translate_client.translate_text(
            Text=input_text,
            SourceLanguageCode="auto",  # Auto-detect source
            TargetLanguageCode=target_language_code
        )
        translated_text = response.get("TranslatedText", "Translation unavailable.")

        # 🏁 Construct chatbot response
        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": "BotTranslateIntent", "state": "Fulfilled"}
            },
            "messages": [{"contentType": "PlainText", "content": translated_text}]
        }

    except Exception as error:
        # 🚨 Error handling for robustness
        error_message = f"LunguaLex Translation Error: {str(error)}"
        print(error_message)
        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": "BotTranslateIntent", "state": "Fulfilled"}
            },
            "messages": [{"contentType": "PlainText", "content": error_message}]
        }
