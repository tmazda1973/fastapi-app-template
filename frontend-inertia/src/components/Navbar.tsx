import React, { useState } from 'react';
import { Link } from '@inertiajs/react';
import {
  ChartBarIcon,
  CogIcon,
  UserIcon,
  ArrowRightEndOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import styles from '@styles/Navbar.module.css';
import { useI18n } from '@hooks/useI18n';
import LanguageSwitcher from './LanguageSwitcher';

/**
 * プロパティ
 * @interface
 */
interface NavbarProps {
  user: {
    id: number;
    name: string;
    email: string;
    role: string | null;
    role_name: string | null;
  };
  currentPath?: string;
  logoutUrl?: string;
  onLogout?: () => void | Promise<void>;
}

/**
 * ナビゲーションバーコンポーネント（Inertia.js版）
 * @module
 */
export const Navbar: React.FC<NavbarProps> = ({
  user,
  currentPath = '',
  logoutUrl = '/auth/logout',
  onLogout,
}) => {
  const { t } = useI18n();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      if (onLogout) {
        // カスタムログアウト関数を使用
        await onLogout();
      } else {
        // 従来のfetch処理
        const response = await fetch(logoutUrl, {
          method: 'GET',
          credentials: 'include',
        });

        if (response.ok) {
          window.location.href = '/login';
        } else {
          console.error(t('ui.navbar.errors.logout_failed'));
        }
      }
    } catch (error) {
      console.error(t('ui.navbar.errors.logout_error'), error);
    }
  };

  const navigationItems = [
    {
      name: t('ui.navbar.navigation.dashboard'),
      href: '/dashboard',
      icon: ChartBarIcon,
      current: currentPath === '/dashboard',
    },
    {
      name: t('ui.navbar.navigation.settings'),
      href: '/settings',
      icon: CogIcon,
      current: currentPath === '/settings',
    },
  ];

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <div className={styles.content}>
          {/* ロゴ・ブランド */}
          <div className={styles.brand}>
            <div className={styles.brandLogo}>
              <span className={styles.brandLogoText}>F</span>
            </div>
            <span className={styles.brandName}>
              {t('ui.navbar.brand.name')}
            </span>
          </div>

          {/* デスクトップナビゲーション */}
          <div className={styles.navigation}>
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`${styles.navLink} ${
                  item.current ? styles.navLinkActive : styles.navLinkInactive
                }`}
              >
                <item.icon className={styles.navLinkIcon} />
                {item.name}
              </Link>
            ))}
          </div>

          {/* ユーザーメニュー */}
          <div className={styles.userMenu}>
            {/* 言語切り替え */}
            <LanguageSwitcher className={styles.languageSwitcher} />
            {/* プロフィールドロップダウン */}
            <div className={styles.relativeContainer}>
              <button
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                className={styles.profileButton}
              >
                <div className={styles.profileAvatar}>
                  <UserIcon className={styles.profileAvatarIcon} />
                </div>
                <span className={styles.profileName}>{user.name}</span>
                <svg
                  className={`${styles.profileDropdownIcon} ${
                    isProfileMenuOpen ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {/* ドロップダウンメニュー */}
              {isProfileMenuOpen && (
                <div className={styles.dropdown}>
                  <div className={styles.dropdownContent}>
                    <div className={styles.dropdownUserInfo}>
                      <div className={styles.dropdownUserName}>{user.name}</div>
                      <div className={styles.dropdownUserEmail}>
                        {user.email}
                      </div>
                      <div className={styles.dropdownUserRole}>
                        {user.role_name}
                      </div>
                    </div>

                    <Link
                      href="/settings#account"
                      className={styles.dropdownLink}
                      onClick={() => setIsProfileMenuOpen(false)}
                    >
                      <UserIcon className={styles.dropdownLinkIcon} />
                      {t('ui.navbar.profile_menu.profile')}
                    </Link>

                    <Link
                      href="/settings#preferences"
                      className={styles.dropdownLink}
                      onClick={() => setIsProfileMenuOpen(false)}
                    >
                      <CogIcon className={styles.dropdownLinkIcon} />
                      {t('ui.navbar.profile_menu.settings')}
                    </Link>

                    <div className={styles.dropdownDivider} />

                    <button
                      onClick={handleLogout}
                      className={styles.logoutButton}
                    >
                      <ArrowRightEndOnRectangleIcon
                        className={styles.logoutButtonIcon}
                      />
                      {t('ui.navbar.profile_menu.logout')}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* モバイルメニューボタン */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className={styles.mobileMenuButton}
            >
              {isMenuOpen ? (
                <XMarkIcon className={styles.mobileMenuIcon} />
              ) : (
                <Bars3Icon className={styles.mobileMenuIcon} />
              )}
            </button>
          </div>
        </div>

        {/* モバイルメニュー */}
        {isMenuOpen && (
          <div className={styles.mobileMenu}>
            <div className={styles.mobileMenuList}>
              {navigationItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`${styles.mobileMenuItem} ${
                    item.current
                      ? styles.mobileMenuItemActive
                      : styles.mobileMenuItemInactive
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  <item.icon className={styles.mobileMenuItemIcon} />
                  {item.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* クリック時にメニューを閉じる */}
      {(isMenuOpen || isProfileMenuOpen) && (
        <div
          className={styles.overlay}
          onClick={() => {
            setIsMenuOpen(false);
            setIsProfileMenuOpen(false);
          }}
        />
      )}
    </nav>
  );
};
