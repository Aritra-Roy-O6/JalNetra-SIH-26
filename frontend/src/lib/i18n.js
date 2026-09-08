import i18n from "i18next";

export const LOCALES = [
  ["en-IN", "English"], ["hi-IN", "हिन्दी"], ["ta-IN", "தமிழ்"], ["te-IN", "తెలుగు"],
  ["bn-IN", "বাংলা"], ["od-IN", "ଓଡ଼ିଆ"], ["ml-IN", "മലയാളം"], ["kn-IN", "ಕನ್ನಡ"],
];

const MESSAGES = {
    "en-IN": { replyIn: "Reply in", inputLanguage: "Voice input", appLanguage: "App language", settings: "Settings", close: "Close", marineAssistant: "Marine assistant", prompt: "Ask about marine safety, fishing areas, routes, or coastal conditions.", marineMap: "Marine map", agentReasoning: "Agent reasoning", events: "events", offlineData: "Offline data", offlinePaused: "Live requests are paused. Cached zones, alerts, and your last answer remain available.", offlineStored: "Your latest marine data is stored locally for low-connectivity use.", lastSync: "Last successful marine sync", cachedZones: "Cached fishing zones", cachedAlerts: "Cached alerts", offlineLimit: "New route calculations and voice requests need internet." },
    "hi-IN": { replyIn: "उत्तर की भाषा", inputLanguage: "आवाज़ की भाषा", appLanguage: "ऐप की भाषा", settings: "सेटिंग्स", close: "बंद करें", marineAssistant: "समुद्री सहायक", prompt: "समुद्री सुरक्षा, मछली पकड़ने के क्षेत्र, मार्ग या तटीय परिस्थितियों के बारे में पूछें।", marineMap: "समुद्री मानचित्र", agentReasoning: "एजेंट का तर्क", events: "घटनाएं", offlineData: "ऑफ़लाइन डेटा", offlinePaused: "लाइव अनुरोध रुके हुए हैं। कैश किए गए क्षेत्र, अलर्ट और आपका पिछला उत्तर उपलब्ध हैं।", offlineStored: "कम कनेक्टिविटी के लिए नवीनतम समुद्री डेटा स्थानीय रूप से संग्रहीत है।", lastSync: "अंतिम सफल समुद्री सिंक", cachedZones: "कैश किए गए मछली पकड़ने के क्षेत्र", cachedAlerts: "कैश किए गए अलर्ट", offlineLimit: "नए मार्ग और वॉइस अनुरोधों के लिए इंटरनेट आवश्यक है।" },
    "ta-IN": { replyIn: "பதில் மொழி", inputLanguage: "குரல் உள்ளீட்டு மொழி", appLanguage: "செயலி மொழி", settings: "அமைப்புகள்", close: "மூடு", marineAssistant: "கடல் உதவியாளர்", prompt: "கடல் பாதுகாப்பு, மீன்பிடிப் பகுதிகள், பாதைகள் அல்லது கடலோர நிலைமைகள் பற்றி கேளுங்கள்.", marineMap: "கடல் வரைபடம்", agentReasoning: "முகவர் காரணம்", events: "நிகழ்வுகள்", offlineData: "ஆஃப்லைன் தரவு", offlinePaused: "நேரடி கோரிக்கைகள் நிறுத்தப்பட்டுள்ளன. சேமிக்கப்பட்ட பகுதிகள், எச்சரிக்கைகள் மற்றும் முந்தைய பதில் கிடைக்கும்.", offlineStored: "குறைந்த இணைப்புக்காக சமீபத்திய கடல் தரவு உள்ளூரில் சேமிக்கப்பட்டுள்ளது.", lastSync: "கடைசி வெற்றிகரமான கடல் ஒத்திசைவு", cachedZones: "சேமிக்கப்பட்ட மீன்பிடிப் பகுதிகள்", cachedAlerts: "சேமிக்கப்பட்ட எச்சரிக்கைகள்", offlineLimit: "புதிய பாதைகள் மற்றும் குரல் கோரிக்கைகளுக்கு இணையம் தேவை." },
  "te-IN": { replyIn: "సమాధాన భాష", inputLanguage: "వాయిస్ ఇన్‌పుట్ భాష", appLanguage: "యాప్ భాష", settings: "సెట్టింగ్‌లు", close: "మూసివేయి", marineAssistant: "సముద్ర సహాయకుడు", prompt: "సముద్ర భద్రత, చేపలు పట్టే ప్రాంతాలు, మార్గాలు లేదా తీర పరిస్థితుల గురించి అడగండి.", marineMap: "సముద్ర పటం", agentReasoning: "ఏజెంట్ వివరణ", events: "ఈవెంట్లు" },
  "bn-IN": { replyIn: "উত্তরের ভাষা", inputLanguage: "ভয়েস ইনপুটের ভাষা", appLanguage: "অ্যাপের ভাষা", settings: "সেটিংস", close: "বন্ধ করুন", marineAssistant: "সামুদ্রিক সহকারী", prompt: "সামুদ্রিক নিরাপত্তা, মাছ ধরার এলাকা, পথ বা উপকূলীয় পরিস্থিতি সম্পর্কে জিজ্ঞাসা করুন।", marineMap: "সামুদ্রিক মানচিত্র", agentReasoning: "এজেন্টের যুক্তি", events: "ইভেন্ট" },
  "od-IN": { replyIn: "ଉତ୍ତର ଭାଷା", inputLanguage: "ଭଏସ୍ ଇନପୁଟ୍ ଭାଷା", appLanguage: "ଆପ୍ ଭାଷା", settings: "ସେଟିଂସ୍", close: "ବନ୍ଦ କରନ୍ତୁ", marineAssistant: "ସାମୁଦ୍ରିକ ସହାୟକ", prompt: "ସାମୁଦ୍ରିକ ସୁରକ୍ଷା, ମାଛ ଧରିବା ଅଞ୍ଚଳ, ମାର୍ଗ କିମ୍ବା ଉପକୂଳ ପରିସ୍ଥିତି ବିଷୟରେ ପଚାରନ୍ତୁ।", marineMap: "ସାମୁଦ୍ରିକ ମାନଚିତ୍ର", agentReasoning: "ଏଜେଣ୍ଟର ଯୁକ୍ତି", events: "ଇଭେଣ୍ଟ" },
  "ml-IN": { replyIn: "മറുപടി ഭാഷ", inputLanguage: "വോയ്സ് ഇൻപുട്ട് ഭാഷ", appLanguage: "ആപ്പ് ഭാഷ", settings: "ക്രമീകരണങ്ങൾ", close: "അടയ്ക്കുക", marineAssistant: "സമുദ്ര സഹായി", prompt: "സമുദ്ര സുരക്ഷ, മത്സ്യബന്ധന മേഖലകൾ, പാതകൾ അല്ലെങ്കിൽ തീരദേശ സാഹചര്യങ്ങൾ ചോദിക്കൂ.", marineMap: "സമുദ്ര ഭൂപടം", agentReasoning: "ഏജന്റ് വിശദീകരണം", events: "ഇവന്റുകൾ" },
  "kn-IN": { replyIn: "ಉತ್ತರ ಭಾಷೆ", inputLanguage: "ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಭಾಷೆ", appLanguage: "ಆ್ಯಪ್ ಭಾಷೆ", settings: "ಸೆಟ್ಟಿಂಗ್‌ಗಳು", close: "ಮುಚ್ಚಿ", marineAssistant: "ಸಮುದ್ರ ಸಹಾಯಕ", prompt: "ಸಮುದ್ರ ಸುರಕ್ಷತೆ, ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶಗಳು, ಮಾರ್ಗಗಳು ಅಥವಾ ಕರಾವಳಿ ಪರಿಸ್ಥಿತಿಗಳ ಬಗ್ಗೆ ಕೇಳಿ.", marineMap: "ಸಮುದ್ರ ನಕ್ಷೆ", agentReasoning: "ಏಜೆಂಟ್ ವಿವರಣೆ", events: "ಈವೆಂಟ್‌ಗಳು" },
};

const OFFLINE_MESSAGES = {
  "te-IN": { offlineData: "ఆఫ్‌లైన్ డేటా", offlinePaused: "లైవ్ అభ్యర్థనలు నిలిపివేయబడ్డాయి. క్యాష్ చేసిన ప్రాంతాలు, హెచ్చరికలు మరియు చివరి సమాధానం అందుబాటులో ఉన్నాయి.", offlineStored: "తక్కువ కనెక్టివిటీ కోసం తాజా సముద్ర డేటా స్థానికంగా నిల్వ చేయబడింది.", lastSync: "చివరి విజయవంతమైన సమకాలీకరణ", cachedZones: "క్యాష్ చేసిన చేపల వేట ప్రాంతాలు", cachedAlerts: "క్యాష్ చేసిన హెచ్చరికలు", offlineLimit: "కొత్త మార్గాలు మరియు వాయిస్ అభ్యర్థనలకు ఇంటర్నెట్ అవసరం." },
  "bn-IN": { offlineData: "অফলাইন ডেটা", offlinePaused: "লাইভ অনুরোধ স্থগিত। ক্যাশ করা অঞ্চল, সতর্কতা এবং শেষ উত্তর উপলব্ধ।", offlineStored: "কম সংযোগের জন্য সর্বশেষ সামুদ্রিক ডেটা স্থানীয়ভাবে সংরক্ষিত।", lastSync: "সর্বশেষ সফল সিঙ্ক", cachedZones: "ক্যাশ করা মাছ ধরার অঞ্চল", cachedAlerts: "ক্যাশ করা সতর্কতা", offlineLimit: "নতুন রুট এবং ভয়েস অনুরোধের জন্য ইন্টারনেট প্রয়োজন।" },
  "od-IN": { offlineData: "ଅଫଲାଇନ୍ ତଥ୍ୟ", offlinePaused: "ଲାଇଭ୍ ଅନୁରୋଧ ବନ୍ଦ ଅଛି। କ୍ୟାଶ୍ ଅଞ୍ଚଳ, ସତର୍କତା ଏବଂ ଶେଷ ଉତ୍ତର ଉପଲବ୍ଧ।", offlineStored: "କମ୍ ସଂଯୋଗ ପାଇଁ ସର୍ବଶେଷ ସାମୁଦ୍ରିକ ତଥ୍ୟ ସ୍ଥାନୀୟ ଭାବେ ସଂରକ୍ଷିତ।", lastSync: "ଶେଷ ସଫଳ ସିଙ୍କ୍", cachedZones: "କ୍ୟାଶ୍ ମାଛ ଧରିବା ଅଞ୍ଚଳ", cachedAlerts: "କ୍ୟାଶ୍ ସତର୍କତା", offlineLimit: "ନୂଆ ମାର୍ଗ ଏବଂ ଭଏସ୍ ଅନୁରୋଧ ପାଇଁ ଇଣ୍ଟରନେଟ୍ ଆବଶ୍ୟକ।" },
  "ml-IN": { offlineData: "ഓഫ്‌ലൈൻ ഡാറ്റ", offlinePaused: "ലൈവ് അഭ്യർത്ഥനകൾ നിർത്തിവച്ചിരിക്കുന്നു. കാഷ് ചെയ്ത മേഖലകളും മുന്നറിയിപ്പുകളും അവസാന ഉത്തരവും ലഭ്യമാണ്.", offlineStored: "കുറഞ്ഞ കണക്റ്റിവിറ്റിക്കായി ഏറ്റവും പുതിയ സമുദ്ര ഡാറ്റ പ്രാദേശികമായി സൂക്ഷിച്ചിരിക്കുന്നു.", lastSync: "അവസാന വിജയകരമായ സമന്വയം", cachedZones: "കാഷ് ചെയ്ത മത്സ്യബന്ധന മേഖലകൾ", cachedAlerts: "കാഷ് ചെയ്ത മുന്നറിയിപ്പുകൾ", offlineLimit: "പുതിയ റൂട്ടുകൾക്കും വോയ്സ് അഭ്യർത്ഥനകൾക്കും ഇന്റർനെറ്റ് ആവശ്യമാണ്." },
  "kn-IN": { offlineData: "ಆಫ್‌ಲೈನ್ ಡೇಟಾ", offlinePaused: "ಲೈವ್ ವಿನಂತಿಗಳನ್ನು ನಿಲ್ಲಿಸಲಾಗಿದೆ. ಕ್ಯಾಶ್ ಮಾಡಿದ ವಲಯಗಳು, ಎಚ್ಚರಿಕೆಗಳು ಮತ್ತು ಕೊನೆಯ ಉತ್ತರ ಲಭ್ಯವಿದೆ.", offlineStored: "ಕಡಿಮೆ ಸಂಪರ್ಕಕ್ಕಾಗಿ ಇತ್ತೀಚಿನ ಸಮುದ್ರ ಡೇಟಾವನ್ನು ಸ್ಥಳೀಯವಾಗಿ ಸಂಗ್ರಹಿಸಲಾಗಿದೆ.", lastSync: "ಕೊನೆಯ ಯಶಸ್ವಿ ಸಿಂಕ್", cachedZones: "ಕ್ಯಾಶ್ ಮಾಡಿದ ಮೀನುಗಾರಿಕೆ ವಲಯಗಳು", cachedAlerts: "ಕ್ಯಾಶ್ ಮಾಡಿದ ಎಚ್ಚರಿಕೆಗಳು", offlineLimit: "ಹೊಸ ಮಾರ್ಗಗಳು ಮತ್ತು ಧ್ವನಿ ವಿನಂತಿಗಳಿಗೆ ಇಂಟರ್ನೆಟ್ ಅಗತ್ಯವಿದೆ." },
};

Object.entries(OFFLINE_MESSAGES).forEach(([locale, translations]) => Object.assign(MESSAGES[locale], translations));

if (!i18n.isInitialized) {
  i18n.init({ fallbackLng: "en-IN", lng: "en-IN", resources: Object.fromEntries(Object.entries(MESSAGES).map(([locale, translations]) => [locale, { translation: translations }])) });
}

export function message(locale, key) {
  return MESSAGES[locale]?.[key] || MESSAGES["en-IN"]?.[key] || i18n.getFixedT(locale)(key) || key;
}

export function setAppLocale(locale) {
  return i18n.changeLanguage(locale);
}