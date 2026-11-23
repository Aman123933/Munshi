import React from 'react';
import { Send, ClipboardList, FileSpreadsheet, ShieldAlert } from 'lucide-react';
import { getTranslation } from '../i18n';

export default function NavigationTabs({ activeTab, onSelectTab, isPrincipal, uiLang = 'en' }) {
  const t = (key) => getTranslation(uiLang, key);

  const tabs = [
    { id: 'update', label: t('update'), icon: Send },
    { id: 'records', label: t('records'), icon: ClipboardList },
    { id: 'marks', label: t('marks'), icon: FileSpreadsheet },
    ...(isPrincipal
      ? [{ id: 'audit', label: t('audit'), icon: ShieldAlert, badge: t('principalOnly') }]
      : []),
  ];

  return (
    <nav className="bg-white border-b border-line px-4 sm:px-6">
      <div className="max-w-6xl mx-auto flex space-x-1 sm:space-x-4 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className={`flex items-center space-x-2 py-3 px-3 border-b-2 text-sm font-semibold transition cursor-pointer whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-blue focus:ring-offset-2 ${
                isActive
                  ? 'border-blue text-blue font-bold'
                  : 'border-transparent text-grey-700 hover:text-ink hover:border-line'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue' : 'text-grey-600'}`} />
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="ml-1 text-[10px] px-1.5 py-0.5 rounded font-mono font-bold uppercase bg-amber-100 text-amber-dark border border-amber/30">
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
