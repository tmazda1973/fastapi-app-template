import { useCallback } from 'react';
import { useApi } from './useApi';

/**
 * 言語設定関連APIのカスタムフック
 *
 * 言語切り替え、利用可能言語の取得など
 * 国際化に関連するAPI呼び出しを管理
 */
export function useLocaleApi() {
  const api = useApi({ showGlobalLoader: true });

  /**
   * 言語設定変更
   */
  const changeLocale = useCallback(
    async (locale: string) => {
      return api.call('/api/v1/locale', {
        method: 'POST',
        body: JSON.stringify({ locale }),
      });
    },
    [api],
  );

  /**
   * 利用可能な言語一覧取得
   */
  const getAvailableLocales = useCallback(async () => {
    return api.call<{ locales: string[]; current: string }>('/api/v1/locales', {
      method: 'GET',
    });
  }, [api]);

  /**
   * 現在の言語設定取得
   */
  const getCurrentLocale = useCallback(async () => {
    return api.call<{ locale: string }>('/api/v1/locale', {
      method: 'GET',
    });
  }, [api]);

  return {
    ...api,
    changeLocale,
    getAvailableLocales,
    getCurrentLocale,
  };
}
