import { createRoot } from 'react-dom/client';
import { createInertiaApp, router } from '@inertiajs/react';
import './main.css';
import './i18n/config'; // i18n設定を初期化
import { setI18nResources } from './i18n/config';

/**
 * グローバル設定
 */
router.on('before', (event) => {
  const pageEl = document.querySelector('div[data-page]') as HTMLElement;
  if (pageEl && pageEl.dataset.page) {
    try {
      const pageData = JSON.parse(pageEl.dataset.page);
      const componentName = pageData.component || 'Unknown';
      event.detail.visit.headers['X-Inertia-Current-Component'] = componentName;
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('Failed to parse page data:', error);
      }
      event.detail.visit.headers['X-Inertia-Current-Component'] =
        pageEl.dataset.page;
    }
  }
});

/**
 * ローディング画面用の多言語メッセージ
 * @return 多言語メッセージ
 */
const getLoadingMessage = () => {
  const language = navigator.language.toLowerCase();
  if (language.startsWith('ja')) {
    return '読み込み中...';
  }
  return 'Loading...';
};

/**
 * ローディングページコンポーネント
 * @return DOM要素
 */
const LoadingScreen = () => (
  <div
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: '#ffffff',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 9999,
    }}
  >
    <div
      style={{
        width: '40px',
        height: '40px',
        border: '4px solid #f3f3f3',
        borderTop: '4px solid #10b981',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
      }}
    ></div>
    <p
      style={{
        marginTop: '16px',
        color: '#6b7280',
        fontSize: '14px',
      }}
    >
      {getLoadingMessage()}
    </p>
    <style>{`
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `}</style>
  </div>
);

/**
 * メインアプリケーションの初期化
 */
document.addEventListener('DOMContentLoaded', () => {
  createInertiaApp({
    title: (title) => `${title} - FastAPI App`,
    resolve: (name) => {
      const pages = import.meta.glob('./Pages/**/*.tsx', { eager: true });
      return pages[`./Pages/${name}.tsx`];
    },
    setup({ el, App, props }) {
      if (!el) return;
      const root = createRoot(el);
      // 非同期でi18n初期化とレンダリング
      const initializeAndRender = async () => {
        try {
          // ローディング画面を表示
          root.render(<LoadingScreen />);
          if (import.meta.env.DEV)
            console.log('[Main] Starting i18n initialization...');

          // i18nの初期化：サーバーから受け取った翻訳データを設定
          const pageProps = props.initialPage.props as Record<string, unknown>;
          if (
            typeof pageProps.locale === 'string' &&
            typeof pageProps.translations === 'object' &&
            pageProps.translations
          ) {
            if (import.meta.env.DEV)
              console.log(
                `[Main] Initializing i18n for locale: ${pageProps.locale}`,
              );
            await setI18nResources(
              pageProps.locale,
              pageProps.translations as Record<string, unknown>,
            );
            if (import.meta.env.DEV)
              console.log('[Main] i18n initialization completed');
          }

          // 翻訳データの準備完了後にReactアプリをレンダリング
          if (import.meta.env.DEV) console.log('[Main] Rendering main app...');
          root.render(<App {...props} />);
          if (import.meta.env.DEV)
            console.log('[Main] App rendered successfully');
        } catch (error) {
          console.error('Failed to initialize i18n:', error);
          // エラーが発生した場合もレンダリングを続行
          root.render(<App {...props} />);
        }
      };

      initializeAndRender();
    },
  });
});
