"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, postVoiceQuery } from "@/lib/api";

export const VOICE_LANGUAGES = [
  { code: "en-IN", label: "English" },
  { code: "hi-IN", label: "हिन्दी (Hindi)" },
  { code: "ta-IN", label: "தமிழ் (Tamil)" },
  { code: "te-IN", label: "తెలుగు (Telugu)" },
  { code: "bn-IN", label: "বাংলা (Bengali)" },
  { code: "od-IN", label: "ଓଡ଼ିଆ (Odia)" },
  { code: "ml-IN", label: "മലയാളം (Malayalam)" },
  { code: "kn-IN", label: "ಕನ್ನಡ (Kannada)" },
];

type VoiceResult = {
  transcribed_text: string;
  answer: string;
  audio_base64?: string | null;
  audio_mime_type?: string | null;
  visual_trace?: unknown;
  voice_error?: string | null;
};

type VoiceInterfaceProps = {
  disabled?: boolean;
  onResult: (result: VoiceResult) => void;
  onStatus: (status: string) => void;
};

export default function VoiceInterface({ disabled = false, onResult, onStatus }: VoiceInterfaceProps) {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [language, setLanguage] = useState("hi-IN");
  const [recording, setRecording] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    recorderRef.current?.stream.getTracks().forEach((track) => track.stop());
  }, []);

  function stopRecording() {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    recorderRef.current?.stop();
  }

  async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setError("This browser does not support microphone recording. Please type your question.");
      return;
    }

    try {
      setError("");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";
      const uploadMimeType = "audio/webm";
      const recorder = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        setRecording(false);
        stream.getTracks().forEach((track) => track.stop());
        // Send the portable MIME type rather than the browser-specific codec tag.
        const recordingBlob = new Blob(chunksRef.current, { type: uploadMimeType });
        if (!recordingBlob.size) {
          setError("No audio was captured. Please try again.");
          return;
        }
        try {
          onStatus("Transcribing your voice request…");
          const result = await postVoiceQuery(recordingBlob, language);
          onResult(result);
          onStatus(result.voice_error ? "Text answer ready; audio playback is unavailable." : "Voice answer ready");
          if (result.audio_base64) {
            const audio = new Audio(`data:${result.audio_mime_type || "audio/wav"};base64,${result.audio_base64}`);
            await audio.play();
          }
        } catch (requestError) {
          setError(requestError instanceof ApiError ? requestError.message : "Voice request failed. Please type your question.");
          onStatus("Voice processing unavailable; text input is still available.");
        }
      };
      recorderRef.current = recorder;
      recorder.start();
      setRecording(true);
      onStatus("Listening… tap Stop when you finish.");
      // Saaras synchronous STT accepts recordings of up to 30 seconds.
      timeoutRef.current = setTimeout(stopRecording, 29_000);
    } catch {
      setError("Microphone access was denied. Please type your question instead.");
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-slate-700" htmlFor="voice-language">Voice language</label>
      <select id="voice-language" value={language} onChange={(event) => setLanguage(event.target.value)} disabled={recording || disabled} className="w-full border border-slate-300 px-3 py-2 text-sm">
        {VOICE_LANGUAGES.map((option) => <option key={option.code} value={option.code}>{option.label}</option>)}
      </select>
      <button type="button" onClick={recording ? stopRecording : startRecording} disabled={disabled} className="w-full border border-blue-800 px-4 py-2 text-sm font-semibold text-blue-800 disabled:border-slate-300 disabled:text-slate-400">
        {recording ? "Stop recording" : "Hold a voice conversation"}
      </button>
      {recording && <p className="text-xs text-red-700">Recording — automatically stops after 29 seconds.</p>}
      {error && <p role="status" className="text-xs text-red-700">{error}</p>}
    </div>
  );
}
