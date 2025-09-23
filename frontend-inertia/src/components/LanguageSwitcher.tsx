import React, { useState } from 'react';
import { ChevronDownIcon, GlobeAltIcon } from '@heroicons/react/24/outline';
import { useI18n } from '@hooks/useI18n';
import { useLocaleApi } from '@hooks/api';
import styles from '@styles/LanguageSwitcher.module.css';

/**
 * プロパティ
 *
 * @property className - クラス名
 * @property compact - コンパクトモード
 * @interface
 */
interface LanguageSwitcherProps {
  className?: string;
  compact?: boolean;
}

/**
 * 言語切り替えコンポーネント
 *
 * ドロップダウンメニューで言語を選択可能
 */
export default function LanguageSwitcher({
  className = '',
  compact = false,
}: LanguageSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { t, currentLanguage, availableLanguages, getLanguageName } = useI18n();
  const { changeLocale, loading: isChanging } = useLocaleApi();

  const handleLanguageChange = async (locale: string) => {
    if (isChanging) return; // 変更中は無効

    try {
      setIsOpen(false);
      await changeLocale(locale);
      await new Promise((resolve) => setTimeout(resolve, 200));

      // ページをリロードして新しい言語設定を反映
      window.location.reload();
    } catch (error) {
      console.error('Error saving language preference:', error);
    }
  };

  // 利用可能な言語が1つの場合は表示しない
  if (availableLanguages.length <= 1) {
    return null;
  }

  return (
    <div className={`${styles.languageSwitcher} ${className}`}>
      <button
        type="button"
        className={`${styles.toggleButton} ${compact ? styles.compact : ''} ${isChanging ? styles.changing : ''}`}
        onClick={() => !isChanging && setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        disabled={isChanging}
      >
        <GlobeAltIcon
          className={`${styles.icon} ${isChanging ? styles.spinning : ''}`}
        />
        {!compact && (
          <>
            <span className={styles.currentLanguage}>
              {isChanging
                ? t('language_switcher.changing')
                : getLanguageName(currentLanguage)}
            </span>
            {!isChanging && (
              <ChevronDownIcon
                className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ''}`}
              />
            )}
          </>
        )}
      </button>

      {isOpen && (
        <>
          {/* オーバーレイ */}
          <div className={styles.overlay} onClick={() => setIsOpen(false)} />

          {/* ドロップダウンメニュー */}
          <div className={styles.dropdown}>
            {availableLanguages.map((locale) => (
              <button
                key={locale}
                type="button"
                className={`${styles.dropdownItem} ${
                  locale === currentLanguage ? styles.active : ''
                }`}
                onClick={() => handleLanguageChange(locale)}
              >
                <span className={styles.languageName}>
                  {getLanguageName(locale)}
                </span>
                {locale === currentLanguage && (
                  <span className={styles.checkmark}>✓</span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
