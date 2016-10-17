/**
 * i18n.js
 *
 * This will setup the i18n language files and locale data for your app.
 *
 */
import { addLocaleData } from 'react-intl';

import enLocaleData from 'react-intl/locale-data/en';
import ruLocaleData from 'react-intl/locale-data/ru';

export const appLocales = [
  'en',
  'ru',
];

addLocaleData(enLocaleData);
addLocaleData(ruLocaleData);

import enTranslationMessages from './translations/en.json';
import ruTranslationMessages from './translations/ru.json';

const formatTranslationMessages = (messages) => {
  const formattedMessages = {};
  for (const message of messages) {
    formattedMessages[message.id] = message.message || message.defaultMessage;
  }

  return formattedMessages;
};

export const translationMessages = {
  en: formatTranslationMessages(enTranslationMessages),
  ru: formatTranslationMessages(ruTranslationMessages),
};
