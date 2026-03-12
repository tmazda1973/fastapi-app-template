import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

/**
 * i18next設定
 *
 * バックエンドのi18nシステムと統合し、
 * サーバーサイドで管理される翻訳データを利用
 */

export interface I18nResources {
  [locale: string]: {
    translation: Record<string, unknown>;
  };
}

const config = {
  // デフォルト言語
  fallbackLng: 'ja',

  // 言語設定
  lng: 'ja', // 初期言語を明示的に設定

  // デバッグモード（開発時のみ）
  debug: import.meta.env.DEV,

  // 言語検出設定 - サーバー主導にするため無効化
  detection: {
    // 検出方法を空にしてサーバー側の言語設定に完全依存
    order: [],
    // キャッシュも無効化
    caches: [],
  },

  // 補間設定
  interpolation: {
    escapeValue: false, // React側でエスケープ処理されるため
  },

  // リソース管理設定
  react: {
    useSuspense: false, // Suspenseを無効にして手動制御
  },

  // キー不在時の動作
  returnKeyIfNotFound: true,
  returnEmptyString: false,

  // リソース（初期は空、サーバーから動的にロード）
  resources: {} as I18nResources,
};

// i18nextを初期化
i18n.use(initReactI18next).init(config);

/**
 * サーバーから取得した翻訳データを設定
 * Inertia.jsのページプロップから呼び出される
 */
export async function setI18nResources(
  locale: string,
  translations: Record<string, unknown>,
): Promise<void> {
  const isDev = import.meta.env.DEV;
  if (isDev) console.log(`[i18n] Setting resources for locale: ${locale}`);

  // 既存のリソースを削除してからクリーンに設定
  if (i18n.hasResourceBundle(locale, 'translation')) {
    i18n.removeResourceBundle(locale, 'translation');
  }

  // リソースを追加
  i18n.addResourceBundle(locale, 'translation', translations, true, true);
  if (isDev) console.log(`[i18n] Resource bundle added for locale: ${locale}`);

  // 言語を変更（完了まで待機）
  if (isDev)
    console.log(`[i18n] Changing language from ${i18n.language} to ${locale}`);
  await i18n.changeLanguage(locale);
  if (isDev) console.log(`[i18n] Language changed to: ${i18n.language}`);

  // 翻訳データが実際に使用可能になるまで確実に待機
  await new Promise<void>((resolve, reject) => {
    const startTime = Date.now();
    const timeout = 5000; // 5秒タイムアウト

    const checkTranslation = () => {
      // 現在の時間チェック
      if (Date.now() - startTime > timeout) {
        console.error('[i18n] Timeout waiting for translations to be ready');
        reject(new Error('Translation setup timeout'));
        return;
      }

      // より厳密なテスト用のキーで翻訳が正しく動作するかチェック
      const testKeys = [
        'ui.dashboard.title',
        'ui.navbar.brand.name',
        'ui.login.title',
      ];
      const translationResults = testKeys.map((key) => {
        const translation = i18n.t(key);
        const isTranslated = translation !== key && translation.length > 0;
        if (isDev)
          console.log(
            `[i18n] Key: ${key} -> ${translation} (translated: ${isTranslated})`,
          );
        return isTranslated;
      });

      const allTranslated = translationResults.every((result) => result);

      if (allTranslated) {
        if (isDev)
          console.log(`[i18n] All translations ready for locale: ${locale}`);
        resolve();
      } else {
        if (isDev)
          console.log(
            `[i18n] Still waiting for translations... (${translationResults.filter((r) => r).length}/${testKeys.length} ready)`,
          );
        setTimeout(checkTranslation, 50); // 50ms後に再チェック
      }
    };

    // 初回チェック前に少し待機
    setTimeout(checkTranslation, 100);
  });

  // 追加の安全な待機時間
  await new Promise((resolve) => setTimeout(resolve, 200));
  if (isDev)
    console.log(
      `[i18n] Resources fully set and verified for locale: ${locale}`,
    );
}

/**
 * 現在の言語を取得
 */
export function getCurrentLanguage(): string {
  return i18n.language || 'ja';
}

/**
 * 利用可能な言語一覧を取得
 */
export function getAvailableLanguages(): string[] {
  return Object.keys(i18n.options.resources || {});
}

export default i18n;
