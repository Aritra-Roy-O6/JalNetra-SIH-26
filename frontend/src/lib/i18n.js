import i18n from "i18next";

export const LOCALES = [
  ["en-IN", "English"], ["hi-IN", "हिन्दी"], ["ta-IN", "தமிழ்"], ["te-IN", "తెలుగు"],
  ["bn-IN", "বাংলা"], ["od-IN", "ଓଡ଼ିଆ"], ["ml-IN", "മലയാളം"], ["kn-IN", "ಕನ್ನಡ"],
];

const MESSAGES = {
  "en-IN": { replyIn: "Reply in", inputLanguage: "Voice input", appLanguage: "App language", settings: "Settings", close: "Close", marineAssistant: "Marine assistant", prompt: "Ask about marine safety, fishing areas, routes, or coastal conditions.", marineMap: "Marine map", agentReasoning: "Agent reasoning", events: "events" },
  "hi-IN": { replyIn: "उत्तर की भाषा", inputLanguage: "आवाज़ की भाषा", appLanguage: "ऐप की भाषा", settings: "सेटिंग्स", close: "बंद करें", marineAssistant: "समुद्री सहायक", prompt: "समुद्री सुरक्षा, मछली पकड़ने के क्षेत्र, मार्ग या तटीय परिस्थितियों के बारे में पूछें।", marineMap: "समुद्री मानचित्र", agentReasoning: "एजेंट का तर्क", events: "घटनाएं" },
  "ta-IN": { replyIn: "பதில் மொழி", inputLanguage: "குரல் உள்ளீட்டு மொழி", appLanguage: "செயலி மொழி", settings: "அமைப்புகள்", close: "மூடு", marineAssistant: "கடல் உதவியாளர்", prompt: "கடல் பாதுகாப்பு, மீன்பிடிப் பகுதிகள், பாதைகள் அல்லது கடலோர நிலைமைகள் பற்றி கேளுங்கள்.", marineMap: "கடல் வரைபடம்", agentReasoning: "முகவர் காரணம்", events: "நிகழ்வுகள்" },
  "te-IN": { replyIn: "సమాధాన భాష", inputLanguage: "వాయిస్ ఇన్‌పుట్ భాష", appLanguage: "యాప్ భాష", settings: "సెట్టింగ్‌లు", close: "మూసివేయి", marineAssistant: "సముద్ర సహాయకుడు", prompt: "సముద్ర భద్రత, చేపలు పట్టే ప్రాంతాలు, మార్గాలు లేదా తీర పరిస్థితుల గురించి అడగండి.", marineMap: "సముద్ర పటం", agentReasoning: "ఏజెంట్ వివరణ", events: "ఈవెంట్లు" },
  "bn-IN": { replyIn: "উত্তরের ভাষা", inputLanguage: "ভয়েস ইনপুটের ভাষা", appLanguage: "অ্যাপের ভাষা", settings: "সেটিংস", close: "বন্ধ করুন", marineAssistant: "সামুদ্রিক সহকারী", prompt: "সামুদ্রিক নিরাপত্তা, মাছ ধরার এলাকা, পথ বা উপকূলীয় পরিস্থিতি সম্পর্কে জিজ্ঞাসা করুন।", marineMap: "সামুদ্রিক মানচিত্র", agentReasoning: "এজেন্টের যুক্তি", events: "ইভেন্ট" },
  "od-IN": { replyIn: "ଉତ୍ତର ଭାଷା", inputLanguage: "ଭଏସ୍ ଇନପୁଟ୍ ଭାଷା", appLanguage: "ଆପ୍ ଭାଷା", settings: "ସେଟିଂସ୍", close: "ବନ୍ଦ କରନ୍ତୁ", marineAssistant: "ସାମୁଦ୍ରିକ ସହାୟକ", prompt: "ସାମୁଦ୍ରିକ ସୁରକ୍ଷା, ମାଛ ଧରିବା ଅଞ୍ଚଳ, ମାର୍ଗ କିମ୍ବା ଉପକୂଳ ପରିସ୍ଥିତି ବିଷୟରେ ପଚାରନ୍ତୁ।", marineMap: "ସାମୁଦ୍ରିକ ମାନଚିତ୍ର", agentReasoning: "ଏଜେଣ୍ଟର ଯୁକ୍ତି", events: "ଇଭେଣ୍ଟ" },
  "ml-IN": { replyIn: "മറുപടി ഭാഷ", inputLanguage: "വോയ്സ് ഇൻപുട്ട് ഭാഷ", appLanguage: "ആപ്പ് ഭാഷ", settings: "ക്രമീകരണങ്ങൾ", close: "അടയ്ക്കുക", marineAssistant: "സമുദ്ര സഹായി", prompt: "സമുദ്ര സുരക്ഷ, മത്സ്യബന്ധന മേഖലകൾ, പാതകൾ അല്ലെങ്കിൽ തീരദേശ സാഹചര്യങ്ങൾ ചോദിക്കൂ.", marineMap: "സമുദ്ര ഭൂപടം", agentReasoning: "ഏജന്റ് വിശദീകരണം", events: "ഇവന്റുകൾ" },
  "kn-IN": { replyIn: "ಉತ್ತರ ಭಾಷೆ", inputLanguage: "ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಭಾಷೆ", appLanguage: "ಆ್ಯಪ್ ಭಾಷೆ", settings: "ಸೆಟ್ಟಿಂಗ್‌ಗಳು", close: "ಮುಚ್ಚಿ", marineAssistant: "ಸಮುದ್ರ ಸಹಾಯಕ", prompt: "ಸಮುದ್ರ ಸುರಕ್ಷತೆ, ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶಗಳು, ಮಾರ್ಗಗಳು ಅಥವಾ ಕರಾವಳಿ ಪರಿಸ್ಥಿತಿಗಳ ಬಗ್ಗೆ ಕೇಳಿ.", marineMap: "ಸಮುದ್ರ ನಕ್ಷೆ", agentReasoning: "ಏಜೆಂಟ್ ವಿವರಣೆ", events: "ಈವೆಂಟ್‌ಗಳು" },
};

if (!i18n.isInitialized) {
  i18n.init({ fallbackLng: "en-IN", lng: "en-IN", resources: Object.fromEntries(Object.entries(MESSAGES).map(([locale, translations]) => [locale, { translation: translations }])) });
}

export function message(locale, key) {
  return i18n.getFixedT(locale)(key) || i18n.getFixedT("en-IN")(key) || key;
}

export function setAppLocale(locale) {
  return i18n.changeLanguage(locale);
}