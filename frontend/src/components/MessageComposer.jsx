import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Send,
  Sparkles,
  AlertCircle,
  Languages,
  Check,
} from 'lucide-react';
import { apiClient } from '../api/client';
import FirstRunExplainer from './FirstRunExplainer';
import { getTranslation } from '../i18n';

export default function MessageComposer({
  initialText = '',
  onSendMessage,
  isSending,
  error,
  onClearError,
  uiLang = 'en',
}) {
  const [text, setText] = useState(initialText);
  const [langHint, setLangHint] = useState('auto');
  const [demoMessages, setDemoMessages] = useState([]);
  const [loadingDemos, setLoadingDemos] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [speechError, setSpeechError] = useState(null);

  const t = (key) => getTranslation(uiLang, key);
  const recognitionRef = useRef(null);

  // Sync initialText if updated from parent
  useEffect(() => {
    if (initialText !== undefined) {
      setText(initialText);
    }
  }, [initialText]);

  // Check Web Speech API support
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
    } else {
      setSpeechSupported(false);
    }
  }, []);

  // Fetch 6 demo messages from GET /api/demo/messages
  useEffect(() => {
    let isMounted = true;
    async function loadDemos() {
      try {
        setLoadingDemos(true);
        const demos = await apiClient.getDemoMessages();
        if (isMounted) {
          setDemoMessages(demos);
        }
      } catch (err) {
        console.error('Failed to load demo messages:', err);
      } finally {
        if (isMounted) setLoadingDemos(false);
      }
    }
    loadDemos();
    return () => {
      isMounted = false;
    };
  }, []);

  // Clean up speech recognition on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  // Handle Web Speech API listening
  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      return;
    }

    setSpeechError(null);

    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      // hi-IN or en-IN by language selector
      recognition.lang =
        langHint === 'hi' || langHint === 'hinglish' ? 'hi-IN' : 'en-IN';
      recognition.continuous = false;
      recognition.interimResults = true;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        if (transcript) {
          setText((prev) => (prev ? `${prev} ${transcript}` : transcript));
        }
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        if (event.error !== 'no-speech') {
          setSpeechError(`Speech error: ${event.error}`);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch (err) {
      console.error('Failed to start speech recognition:', err);
      setSpeechError('Could not start microphone. Check browser permissions.');
      setIsListening(false);
    }
  };

  const handleSelectDemo = (demoText) => {
    setText(demoText);
    if (onClearError) onClearError();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || isSending) return;
    onSendMessage({
      text: text.trim(),
      lang_hint: langHint === 'auto' ? null : langHint,
    });
  };

  // Required 3-Kabirs test scenario
  const testCollisionCase =
    '8A: 3 absent — Kabir, Ayaan, Riya. Covered chapter 4. Homework Ex 4.2.';

  return (
    <div className="space-y-6">
      {/* 1. First-Run State 3-Step Explainer Banner */}
      <FirstRunExplainer lang={uiLang} />

      {/* 2. Demo Message Chips Section */}
      <section className="bg-white rounded-xl border border-line p-5 shadow-xs">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2 text-ink">
            <Sparkles className="w-4 h-4 text-blue" />
            <h2 className="font-heading text-xs tracking-wider uppercase text-grey-700">
              Demo Scenarios &amp; Sample Messages (GET /api/demo/messages)
            </h2>
          </div>
          <span className="text-xs text-grey-600 font-medium hidden sm:inline">
            Click a chip to populate composer
          </span>
        </div>

        {/* Featured Test Case Prompt Chip */}
        <div className="mb-3 p-3 bg-tint/60 border border-blue/20 rounded-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-black uppercase tracking-wider bg-[#FFB020] text-ink">
              Demo Scenario
            </span>
            <span className="text-xs font-bold text-ink">
              3 Kabirs Collision &amp; Syllabus Chapter 4
            </span>
          </div>
          <button
            type="button"
            onClick={() => handleSelectDemo(testCollisionCase)}
            className="text-xs font-semibold px-3 py-1 rounded-md bg-blue text-white hover:bg-blue-700 transition cursor-pointer shadow-xs focus:outline-none focus:ring-2 focus:ring-blue"
          >
            Load: &quot;8A: 3 absent — Kabir, Ayaan, Riya...&quot;
          </button>
        </div>

        {/* 6 Clickable Demo Message Chips */}
        {loadingDemos ? (
          <div className="flex flex-wrap gap-2 animate-pulse">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-8 w-36 bg-grey-100 rounded-lg" />
            ))}
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {demoMessages.map((demo) => {
              const isSelected = text === demo.text;
              return (
                <button
                  key={demo.id}
                  type="button"
                  onClick={() => handleSelectDemo(demo.text)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border text-left transition cursor-pointer flex items-center space-x-1.5 focus:outline-none focus:ring-2 focus:ring-blue ${
                    isSelected
                      ? 'bg-blue text-white border-blue shadow-xs font-bold'
                      : 'bg-[#F9FAFB] text-grey-800 border-line hover:border-blue/50 hover:bg-tint/30'
                  }`}
                  title={demo.scenario || demo.text}
                >
                  <span className="font-bold uppercase font-heading text-[11px]">
                    {demo.class_label || '8A'}:
                  </span>
                  <span>{demo.title}</span>
                  {isSelected && <Check className="w-3.5 h-3.5 ml-1" />}
                </button>
              );
            })}
          </div>
        )}
      </section>

      {/* 3. Main Message Composer Card */}
      <section className="bg-white rounded-xl border border-line p-5 shadow-sm space-y-4">
        {/* Error State Banner */}
        {error && (
          <div className="p-3.5 bg-red-50 border border-status-block/30 rounded-lg flex items-start space-x-3 text-status-block">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div className="flex-1 text-xs font-medium">
              <span className="font-bold">Error sending message: </span>
              <span>{error}</span>
            </div>
            <button
              onClick={onClearError}
              className="text-xs underline font-semibold hover:opacity-80 ml-2"
            >
              Dismiss
            </button>
          </div>
        )}

        {speechError && (
          <div className="p-2.5 bg-amber-50 border border-amber/40 rounded-lg text-xs text-amber-dark flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{speechError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Top Bar inside Composer: Language Selector & Speech Note */}
          <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-line">
            {/* Language Hint Selector */}
            <div className="flex items-center space-x-2">
              <Languages className="w-4 h-4 text-grey-600" />
              <label htmlFor="lang-hint" className="text-xs font-semibold text-grey-700 uppercase tracking-wider">
                {t('languageHint')}:
              </label>
              <div className="inline-flex rounded-lg border border-line bg-grey-50 p-0.5 text-xs">
                {[
                  { value: 'auto', label: 'Auto' },
                  { value: 'en', label: 'English' },
                  { value: 'hi', label: 'Hindi' },
                  { value: 'hinglish', label: 'Hinglish' },
                ].map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setLangHint(opt.value)}
                    className={`px-2.5 py-1 rounded-md font-semibold transition cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue ${
                      langHint === opt.value
                        ? 'bg-white text-blue font-bold shadow-xs'
                        : 'text-grey-700 hover:text-ink'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Voice Input capability status note */}
            <div className="text-[11px] text-grey-600">
              {speechSupported ? (
                <span className="inline-flex items-center space-x-1">
                  <span>Voice works in Chrome and Edge only.</span>
                  <span className="font-mono text-[10px] bg-grey-100 text-grey-800 px-1 py-0.5 rounded font-bold">
                    {langHint === 'hi' || langHint === 'hinglish' ? 'hi-IN' : 'en-IN'}
                  </span>
                </span>
              ) : (
                <span className="text-status-block font-medium">
                  Voice input is not supported in this browser. Voice works in Chrome and Edge only.
                </span>
              )}
            </div>
          </div>

          {/* Large Textarea Composer */}
          <div className="relative">
            <textarea
              rows={5}
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                if (error && onClearError) onClearError();
              }}
              placeholder={t('composerPlaceholder')}
              className="w-full p-4 rounded-xl border border-line focus:border-blue focus:ring-2 focus:ring-blue/20 text-ink text-base font-body leading-relaxed placeholder:text-grey-400 focus:outline-none transition resize-y min-h-[140px]"
            />
            {text && (
              <button
                type="button"
                onClick={() => setText('')}
                className="absolute top-3 right-3 text-xs text-grey-700 hover:text-ink bg-white/90 px-2 py-0.5 rounded border border-line font-medium focus:outline-none focus:ring-1 focus:ring-blue"
                title="Clear text"
              >
                {t('clear')}
              </button>
            )}
          </div>

          {/* Composer Footer Actions */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
            <div className="flex items-center space-x-3">
              {/* Microphone Button (visible only if browser supports Web Speech API) */}
              {speechSupported && (
                <button
                  type="button"
                  onClick={toggleListening}
                  className={`inline-flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold border transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue ${
                    isListening
                      ? 'bg-red-500 text-white border-red-600 animate-pulse ring-2 ring-red-400'
                      : 'bg-white text-grey-700 border-line hover:border-grey hover:bg-grey-50'
                  }`}
                  title={`Voice input (${langHint === 'hi' || langHint === 'hinglish' ? 'hi-IN' : 'en-IN'})`}
                >
                  {isListening ? (
                    <>
                      <MicOff className="w-4 h-4 animate-spin" />
                      <span>{t('listening')} ({langHint === 'hi' || langHint === 'hinglish' ? 'Hindi' : 'English'})...</span>
                    </>
                  ) : (
                    <>
                      <Mic className="w-4 h-4 text-blue" />
                      <span>{t('dictateVoice')}</span>
                    </>
                  )}
                </button>
              )}

              <span className="text-xs text-grey-600 font-mono">
                {text.length} characters
              </span>
            </div>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!text.trim() || isSending}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-blue text-white font-semibold text-sm hover:bg-blue-700 active:bg-blue-800 disabled:opacity-40 disabled:cursor-not-allowed transition shadow-xs cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue focus:ring-offset-2"
            >
              <Send className="w-4 h-4" />
              <span>{isSending ? t('processing') : t('send')}</span>
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
