import { useTranslation } from 'react-i18next';
import { usePage } from '@inertiajs/react';

/**
 * 国際化対応用のカスタムフック
 *
 * バックエンドから受け取った翻訳データを使用して
 * 翻訳機能を提供
 */
export function useI18n() {
  const { t, i18n } = useTranslation();
  const { props } = usePage<{
    locale?: string;
    translations?: Record<string, unknown>;
    available_locales?: string[];
  }>();

  /**
   * 翻訳テキストを取得
   * ネストしたキーにも対応（例: 'errors.user.not_found'）
   */
  const translate = (
    key: string,
    options?: Record<string, unknown>,
  ): string => {
    return t(key, options) as string;
  };

  /**
   * エラーメッセージの翻訳
   * バックエンドのエラーキー形式に対応
   */
  const translateError = (
    errorKey: string,
    options?: Record<string, unknown>,
  ): string => {
    return t(`errors.${errorKey}`, options) as string;
  };

  /**
   * 言語を変更（サーバー主導のため使用非推奨）
   * 言語切り替えはLanguageSwitcherからサーバー経由で行う
   */
  const changeLanguage = async (locale: string) => {
    console.warn(
      '[useI18n] changeLanguage is deprecated. Use LanguageSwitcher for language switching.',
    );
    await i18n.changeLanguage(locale);
  };

  /**
   * 現在の言語
   */
  const currentLanguage = i18n.language || props.locale || 'ja';

  /**
   * 利用可能な言語一覧
   */
  const availableLanguages = props.available_locales || ['ja'];

  /**
   * 言語表示名の取得
   */
  const getLanguageName = (locale: string): string => {
    const languageNames: Record<string, string> = {
      ja: '日本語',
      en: 'English',
      zh: '中文',
      ko: '한국어',
    };
    return languageNames[locale] || locale;
  };

  return {
    // 翻訳関数
    t: translate,
    te: translateError,

    // 言語管理
    currentLanguage,
    availableLanguages,
    changeLanguage,
    getLanguageName,

    // 言語チェック
    isJapanese: currentLanguage === 'ja',
    isEnglish: currentLanguage === 'en',
  };
}

/**
 * フォームバリデーションエラー翻訳用フック
 */
export function useFormI18n() {
  const { te } = useI18n();

  /**
   * Inertia.jsのエラーレスポンスを翻訳
   */
  const translateFormErrors = (
    errors: Record<string, string>,
  ): Record<string, string> => {
    const translatedErrors: Record<string, string> = {};

    Object.entries(errors).forEach(([field, message]) => {
      // バックエンドからのi18nキーの場合
      if (message.startsWith('errors.')) {
        translatedErrors[field] = te(message.replace('errors.', ''));
      } else {
        // 通常のメッセージの場合はそのまま
        translatedErrors[field] = message;
      }
    });

    return translatedErrors;
  };

  return {
    translateFormErrors,
    te,
  };
}
