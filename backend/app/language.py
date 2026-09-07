"""Small offline language/context layer used until model translation is enabled."""

from __future__ import annotations

import re

LANGUAGE_NAMES = {
    "en-IN": "English", "hi-IN": "Hindi", "ta-IN": "Tamil", "te-IN": "Telugu",
    "bn-IN": "Bengali", "od-IN": "Odia", "ml-IN": "Malayalam", "kn-IN": "Kannada",
}

QUERY_TRANSLATIONS = {
    "hi-IN": {
        "मछली कहाँ है": "where fish", "मछली कहाँ मिलेगी": "where fish",
        "सीमा चेतावनी": "boundary warning", "कम पकड़ क्यों": "why low catch",
        "कल समुद्र जाना सुरक्षित है": "is it safe to sail tomorrow",
    },
    "ta-IN": {
        "மீன் எங்கே": "where fish", "எல்லை எச்சரிக்கை": "boundary warning",
        "பிடிப்பு ஏன் குறைவு": "why low catch", "நாளை கடலுக்கு செல்வது பாதுகாப்பானதா": "is it safe to sail tomorrow",
    },
    "te-IN": {
        "చేపలు ఎక్కడ ఉన్నాయి": "where fish", "సరిహద్దు హెచ్చరిక": "boundary warning",
        "పట్టుబడి ఎందుకు తక్కువగా ఉంది": "why low catch",
    },
    "bn-IN": {"মাছ কোথায়": "where fish", "সীমানা সতর্কতা": "boundary warning", "ধরা কম কেন": "why low catch"},
    "od-IN": {"ମାଛ କେଉଁଠାରେ": "where fish", "ସୀମା ସତର୍କତା": "boundary warning", "ଧରା କମ କାହିଁକି": "why low catch"},
    "ml-IN": {"മീൻ എവിടെ": "where fish", "അതിർത്തി മുന്നറിയിപ്പ്": "boundary warning", "പിടിത്തം കുറയുന്നത് എന്തുകൊണ്ട്": "why low catch"},
    "kn-IN": {"ಮೀನು ಎಲ್ಲಿದೆ": "where fish", "ಗಡಿ ಎಚ್ಚರಿಕೆ": "boundary warning", "ಹಿಡಿತ ಏಕೆ ಕಡಿಮೆ": "why low catch"},
}

ANSWER_TRANSLATIONS = {
    "hi-IN": {
        "PFZ": "मछली पकड़ने का अच्छा क्षेत्र {location} के पास है। भरोसा {confidence} है।",
        "Weather": "अभी समुद्र में जाना सुरक्षित नहीं है। लहरें {wave} मीटर हैं और सुरक्षित सीमा {threshold} मीटर है।",
        "Regulation": "चेतावनी: {zone} में {restriction} सक्रिय है।",
        "Route": "सुरक्षित मार्ग {hazards} से बचता है।",
        "Trend": "कम पकड़ का कारण कमजोर समुद्री स्थिति और PFZ से बाहर मछली पकड़ना हो सकता है।",
    },
    "ta-IN": {
        "PFZ": "நல்ல மீன்பிடி பகுதி {location} அருகில் உள்ளது. நம்பிக்கை {confidence}.",
        "Weather": "இப்போது கடலுக்கு செல்வது பாதுகாப்பானது அல்ல. அலை உயரம் {wave} மீட்டர்; பாதுகாப்பு வரம்பு {threshold} மீட்டர்.",
        "Regulation": "எச்சரிக்கை: {zone} பகுதியில் {restriction} செயல்பாட்டில் உள்ளது.",
        "Route": "பாதுகாப்பான பாதை {hazards} பகுதிகளைத் தவிர்க்கிறது.",
        "Trend": "குறைந்த பிடிப்புக்கு பலவீனமான கடல் நிலையும் PFZ க்கு வெளியே மீன்பிடிப்பதும் காரணமாக இருக்கலாம்.",
    },
    "te-IN": {
        "PFZ": "మంచి చేపల వేట ప్రాంతం {location} దగ్గర ఉంది. నమ్మకం {confidence}.",
        "Weather": "ఇప్పుడు సముద్రానికి వెళ్లడం సురక్షితం కాదు. అలల ఎత్తు {wave} మీటర్లు; భద్రత పరిమితి {threshold} మీటర్లు.",
        "Regulation": "హెచ్చరిక: {zone} లో {restriction} అమల్లో ఉంది.",
        "Route": "సురక్షిత మార్గం {hazards} ప్రాంతాలను తప్పిస్తుంది.",
        "Trend": "తక్కువ వేటకు బలహీనమైన సముద్ర పరిస్థితులు కారణం కావచ్చు.",
    },
    "bn-IN": {
        "PFZ": "{location} এর কাছে ভালো মাছ ধরার এলাকা আছে। আত্মবিশ্বাস {confidence}।",
        "Weather": "এখন সমুদ্রে যাওয়া নিরাপদ নয়। ঢেউ {wave} মিটার; নিরাপদ সীমা {threshold} মিটার।",
        "Regulation": "সতর্কতা: {zone}-এ {restriction} চালু আছে।",
        "Route": "নিরাপদ পথ {hazards} এড়িয়ে চলে।",
        "Trend": "কম মাছ ধরার কারণ দুর্বল সমুদ্র পরিস্থিতি হতে পারে।",
    },
    "od-IN": {
        "PFZ": "{location} ନିକଟରେ ଭଲ ମାଛ ଧରିବା ଅଞ୍ଚଳ ଅଛି। ନିଶ୍ଚିତତା {confidence}।",
        "Weather": "ବର୍ତ୍ତମାନ ସମୁଦ୍ରକୁ ଯିବା ସୁରକ୍ଷିତ ନୁହେଁ। ଢେଉ {wave} ମିଟର; ସୁରକ୍ଷିତ ସୀମା {threshold} ମିଟର।",
        "Regulation": "ସତର୍କତା: {zone} ରେ {restriction} ସକ୍ରିୟ ଅଛି।",
        "Route": "ସୁରକ୍ଷିତ ମାର୍ଗ {hazards} ଠାରୁ ଦୂରେ ଯାଏ।",
        "Trend": "କମ୍ ମାଛ ଧରିବାର କାରଣ ଦୁର୍ବଳ ସମୁଦ୍ର ପରିସ୍ଥିତି ହୋଇପାରେ।",
    },
    "ml-IN": {
        "PFZ": "{location} ന് സമീപം നല്ല മത്സ്യബന്ധന മേഖല ഉണ്ട്. വിശ്വാസ്യത {confidence}.",
        "Weather": "ഇപ്പോൾ കടലിൽ പോകുന്നത് സുരക്ഷിതമല്ല. തിരമാല ഉയരം {wave} മീറ്റർ; സുരക്ഷാ പരിധി {threshold} മീറ്റർ.",
        "Regulation": "മുന്നറിയിപ്പ്: {zone}-ൽ {restriction} സജീവമാണ്.",
        "Route": "സുരക്ഷിത പാത {hazards} ഒഴിവാക്കുന്നു.",
        "Trend": "കുറഞ്ഞ മത്സ്യബന്ധനത്തിന് ദുർബലമായ കടൽ സാഹചര്യങ്ങൾ കാരണമാകാം.",
    },
    "kn-IN": {
        "PFZ": "{location} ಹತ್ತಿರ ಉತ್ತಮ ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶವಿದೆ. ವಿಶ್ವಾಸ {confidence}.",
        "Weather": "ಈಗ ಸಮುದ್ರಕ್ಕೆ ಹೋಗುವುದು ಸುರಕ್ಷಿತವಲ್ಲ. ಅಲೆ ಎತ್ತರ {wave} ಮೀಟರ್; ಸುರಕ್ಷತಾ ಮಿತಿ {threshold} ಮೀಟರ್.",
        "Regulation": "ಎಚ್ಚರಿಕೆ: {zone} ನಲ್ಲಿ {restriction} ಸಕ್ರಿಯವಾಗಿದೆ.",
        "Route": "ಸುರಕ್ಷಿತ ಮಾರ್ಗವು {hazards} ತಪ್ಪಿಸುತ್ತದೆ.",
        "Trend": "ಕಡಿಮೆ ಹಿಡಿತಕ್ಕೆ ದುರ್ಬಲ ಸಮುದ್ರ ಪರಿಸ್ಥಿತಿಗಳು ಕಾರಣವಾಗಿರಬಹುದು.",
    },
}

def normalize_language(language: str | None) -> str:
    return language if language in LANGUAGE_NAMES else "en-IN"

def detect_language(text: str, requested: str | None = None) -> str:
    if requested in LANGUAGE_NAMES and requested != "en-IN":
        return requested
    if re.search(r"[\u0900-\u097F]", text): return "hi-IN"
    if re.search(r"[\u0B80-\u0BFF]", text): return "ta-IN"
    if re.search(r"[\u0C00-\u0C7F]", text): return "te-IN"
    if re.search(r"[\u0980-\u09FF]", text): return "bn-IN"
    if re.search(r"[\u0B00-\u0B7F]", text): return "od-IN"
    return "en-IN"

def translate_to_english(text: str, language: str) -> str:
    clean = " ".join(text.split()).strip()
    for source, target in QUERY_TRANSLATIONS.get(language, {}).items():
        if source in clean: return target
    return clean

def translate_answer(intent: str, language: str, values: dict) -> str:
    if values.get("available") is False:
        return values["english"]
    template = ANSWER_TRANSLATIONS.get(language, {}).get(intent)
    return template.format(**values) if template else values["english"]
