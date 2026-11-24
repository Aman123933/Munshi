import React, { useState, useEffect } from 'react';
import TopBar from './components/TopBar';
import NavigationTabs from './components/NavigationTabs';
import MessageComposer from './components/MessageComposer';
import LoadingSkeleton from './components/LoadingSkeleton';
import ReviewScreen from './review/ReviewScreen';
import RecordsTab from './tabs/RecordsTab';
import MarksTab from './tabs/MarksTab';
import AuditTab from './tabs/AuditTab';
import {
  apiClient,
  getApiMode,
  setApiMode,
  getStoredTeacher,
  setStoredTeacher,
  onServerWakingChange,
} from './api/client';
import { MOCK_TEACHERS } from './api/mock';
import { getTranslation } from './i18n';
import { Loader2 } from 'lucide-react';

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    return (
      getStoredTeacher() || {
        id: 'T01',
        name: 'Rajesh Sharma',
        subject: 'Mathematics',
        role: 'teacher',
      }
    );
  });

  const [apiMode, setMode] = useState(getApiMode());
  const [uiLang, setUiLang] = useState('en');
  const [activeTab, setActiveTab] = useState('update');
  const [updateView, setUpdateView] = useState('composer'); // 'composer' | 'loading' | 'review'
  const [activeReview, setActiveReview] = useState(null);
  const [sendError, setSendError] = useState(null);
  const [composerInitialText, setComposerInitialText] = useState('');
  const [isServerWaking, setIsServerWaking] = useState(false);

  const t = (key) => getTranslation(uiLang, key);

  // Subscribe to slow server waking notifications
  useEffect(() => {
    return onServerWakingChange((waking) => {
      setIsServerWaking(waking);
    });
  }, []);

  // Sync initial login on mount
  useEffect(() => {
    async function initAuth() {
      try {
        await apiClient.login({
          teacher_id: currentUser.id,
          pin: '1234',
        });
      } catch (err) {
        console.error('Initial login error:', err);
      }
    }
    initAuth();
  }, []);

  // Handle switching demo teacher
  const handleTeacherChange = async (teacherId) => {
    const selected = MOCK_TEACHERS.find((t) => t.id === teacherId);
    if (!selected) return;

    try {
      const res = await apiClient.login({
        teacher_id: selected.id,
        pin: selected.pin,
      });

      const updatedUser = {
        id: res.teacher.id,
        name: res.teacher.name,
        subject: res.teacher.subject,
        role: res.role,
      };

      setCurrentUser(updatedUser);
      setStoredTeacher(updatedUser);

      // If switching away from principal while on Audit tab, switch back to Update
      if (res.role !== 'principal' && activeTab === 'audit') {
        setActiveTab('update');
      }
    } catch (err) {
      console.error('Failed to switch teacher:', err);
      alert('Login failed: ' + err.message);
    }
  };

  // Toggle between Mock and Live API
  const handleToggleApiMode = () => {
    const nextMode = apiMode === 'mock' ? 'live' : 'mock';
    setApiMode(nextMode);
    setMode(nextMode);
  };

  // Handle Send message from Composer
  const handleSendMessage = async (payload) => {
    setUpdateView('loading');
    setSendError(null);

    try {
      const reviewObj = await apiClient.createMessage(payload);
      setActiveReview(reviewObj);
      setUpdateView('review');
    } catch (err) {
      console.error('Failed to create message:', err);
      setSendError(err.message || 'Failed to submit message to pipeline.');
      setUpdateView('composer');
    }
  };

  const handleEditMessage = (keptText) => {
    setComposerInitialText(keptText || '');
    setUpdateView('composer');
    setSendError(null);
  };

  const isPrincipal = currentUser?.role === 'principal';

  return (
    <div className="min-h-screen bg-tint text-ink flex flex-col font-body antialiased selection:bg-blue selection:text-white">
      {/* 1. Top Bar with "MUNSHI", Amber Accent Bar & Teacher Switcher */}
      <TopBar
        currentUser={currentUser}
        onTeacherChange={handleTeacherChange}
        apiMode={apiMode}
        onToggleApiMode={handleToggleApiMode}
        uiLang={uiLang}
        onToggleUiLang={setUiLang}
      />

      {/* Free-tier cold start indicator */}
      {isServerWaking && (
        <div className="bg-amber-100 border-b border-amber-300 text-amber-900 px-4 py-2 text-xs font-semibold flex items-center justify-center space-x-2 animate-pulse shadow-xs z-50">
          <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-800" />
          <span>Waking the server, this can take up to a minute...</span>
        </div>
      )}

      {/* 2. Navigation Tabs: Update, Records, Marks, Audit (principal only) */}
      <NavigationTabs
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
        }}
        isPrincipal={isPrincipal}
        uiLang={uiLang}
      />

      {/* 3. Main Workspace */}
      <main className="flex-1 max-w-6xl mx-auto w-full p-4 sm:p-6">
        {/* Update Tab */}
        {activeTab === 'update' && (
          <div>
            {updateView === 'loading' && <LoadingSkeleton />}

            {updateView === 'composer' && (
              <MessageComposer
                initialText={composerInitialText}
                onSendMessage={handleSendMessage}
                isSending={false}
                error={sendError}
                onClearError={() => setSendError(null)}
                uiLang={uiLang}
              />
            )}

            {updateView === 'review' && activeReview && (
              <ReviewScreen
                review={activeReview}
                onEditMessage={handleEditMessage}
                onReviewUpdated={(updated) => setActiveReview(updated)}
                uiLang={uiLang}
              />
            )}
          </div>
        )}

        {/* Records Tab */}
        {activeTab === 'records' && <RecordsTab />}

        {/* Marks Tab */}
        {activeTab === 'marks' && <MarksTab />}

        {/* Audit Tab (Principal Only) */}
        {activeTab === 'audit' && isPrincipal && <AuditTab />}
      </main>

      {/* Footer */}
      <footer className="border-t border-line bg-white px-6 py-4 mt-auto">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-grey-700">
          <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-3">
            <span>{t('builtWith')}</span>
            <span className="font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-dark border border-amber/30 text-[11px]">
              {t('footerNote')}
            </span>
          </div>
          <span className="font-mono text-grey-600 text-[11px] break-all sm:break-normal">
            Tokens: Ink #0B1220 &bull; Blue #1F4FD8 &bull; Amber #FFB020 &bull; Tint #EAF0FF
          </span>
        </div>
      </footer>
    </div>
  );
}
