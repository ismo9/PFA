import React, { createContext, useContext, useMemo, useState } from 'react';

type Lang = 'en' | 'fr';

interface IntlContextType {
  lang: Lang;
  setLang: (lang: Lang) => void;
  toggleLang: () => void;
  t: (key: string) => string;
}

const IntlContext = createContext<IntlContextType | undefined>(undefined);

const STORAGE_KEY = 'erpconnect_lang';

const messages: Record<Lang, Record<string, string>> = {
  en: {
    'app.title': 'ERPConnect',
    'dashboard.title': 'Dashboard',
    'dashboard.subtitle': 'Live KPIs pulled from FastAPI backend',
    'inventory.title': 'Inventory',
    'inventory.subtitle': 'Live product list and recent stock moves',
    'forecast.title': 'Forecast',
    'forecast.subtitle': '30-day ML forecast per product',
    'replenishment.title': 'Replenishment',
    'replenishment.subtitle': 'ROP-based reorder suggestions with urgency levels',
    'analytics.title': 'Analytics',
    'analytics.subtitle': 'Anomalies and ABC/XYZ segmentation from live backend',
    'kpi.title': 'KPI Builder',
    'kpi.subtitle': 'Live KPI catalog from backend for dashboard composition',
    'notifications.title': 'Notifications',
    'settings.title': 'Settings',
  },
  fr: {
    'app.title': 'ERPConnect',
    'dashboard.title': 'Tableau de bord',
    'dashboard.subtitle': 'Indicateurs en temps réel depuis FastAPI',
    'inventory.title': 'Stock',
    'inventory.subtitle': 'Liste des produits et derniers mouvements',
    'forecast.title': 'Prévisions',
    'forecast.subtitle': 'Prévisions ML sur 30 jours par produit',
    'replenishment.title': 'Réapprovisionnement',
    'replenishment.subtitle': 'Propositions de commande basées sur le point de commande',
    'analytics.title': 'Analytique',
    'analytics.subtitle': 'Anomalies et segmentation ABC/XYZ en temps réel',
    'kpi.title': 'Constructeur de KPI',
    'kpi.subtitle': 'Catalogue de KPI pour construire vos tableaux de bord',
    'notifications.title': 'Notifications',
    'settings.title': 'Paramètres',
  },
};

export function IntlProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(
    ((localStorage.getItem(STORAGE_KEY) as Lang | null) || 'en'),
  );

  const setLang = (value: Lang) => {
    setLangState(value);
    localStorage.setItem(STORAGE_KEY, value);
  };

  const toggleLang = () => setLang(lang === 'en' ? 'fr' : 'en');

  const t = (key: string) => {
    return messages[lang][key] || messages.en[key] || key;
  };

  const value = useMemo(
    () => ({ lang, setLang, toggleLang, t }),
    [lang],
  );

  return <IntlContext.Provider value={value}>{children}</IntlContext.Provider>;
}

export function useIntl() {
  const ctx = useContext(IntlContext);
  if (!ctx) throw new Error('useIntl must be used within IntlProvider');
  return ctx;
}



