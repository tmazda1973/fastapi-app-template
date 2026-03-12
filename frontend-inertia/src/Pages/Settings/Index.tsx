import React, { useState, useEffect } from 'react';
import { Link, router } from '@inertiajs/react';
import {
  UserIcon,
  CogIcon,
  ShieldCheckIcon,
  KeyIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';
import styles from '@styles/Settings.module.css';
import { AuthenticatedLayout } from '@layouts/AuthenticatedLayout';
import { useI18n } from '@hooks/useI18n';
import { useUserApi } from '@hooks/api';
import LanguageSwitcher from '@components/LanguageSwitcher';

interface User {
  id: number;
  name: string;
  email: string;
  role: string | null;
  role_name: string | null;
}

interface SettingsProps {
  user: User;
}

type TabType = 'account' | 'security' | 'preferences' | 'language' | 'api';
type NotificationType = 'success' | 'error' | 'info';

interface Notification {
  message: string;
  type: NotificationType;
}

export default function Settings({ user }: SettingsProps) {
  const { t, currentLanguage } = useI18n(); // i18nフックを使用
  const { updateProfile, loading: isSaving, error: apiError } = useUserApi();
  const [activeTab, setActiveTab] = useState<TabType>('account');

  const [profileData, setProfileData] = useState({ name: user.name });
  const [originalName, setOriginalName] = useState(user.name);
  const [isEditingName, setIsEditingName] = useState(false);
  const [notification, setNotification] = useState<Notification | null>(null);

  // URLハッシュ連動
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.substring(1) as TabType;
      if (
        ['account', 'security', 'preferences', 'language', 'api'].includes(hash)
      ) {
        setActiveTab(hash);
      }
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // 通知表示
  const showNotification = (message: string, type: NotificationType) => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // タブ切り替え
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    window.location.hash = tab;
  };

  // 名前編集
  const handleEditName = () => {
    setIsEditingName(true);
    setOriginalName(profileData.name);
  };

  const handleCancelEdit = () => {
    setIsEditingName(false);
    setProfileData({ name: originalName });
  };

  // ボタンテキストを安全に取得（フォールバック付き）
  const getSaveButtonText = () => {
    const translated = t('ui.settings.labels.save');
    return translated.startsWith('ui.') ? '保存' : translated;
  };

  const getSavingButtonText = () => {
    const translated = t('ui.common.loading.saving');
    return translated.startsWith('ui.') ? '保存中...' : translated;
  };

  const handleSaveName = async () => {
    if (!profileData.name.trim()) {
      showNotification(t('ui.settings.notifications.name_required'), 'error');
      return;
    }

    try {
      const { data: _updatedUser } = await updateProfile({
        name: profileData.name.trim(),
      });

      setIsEditingName(false);
      setOriginalName(profileData.name);
      showNotification(
        t('ui.settings.notifications.profile_updated'),
        'success',
      );

      // ページをリロードしてユーザー情報を最新に更新
      setTimeout(() => {
        router.reload({ only: ['user'] });
      }, 2000);
    } catch (error) {
      console.error('Profile update error:', error);
      const errorMessage =
        apiError?.message || t('ui.settings.notifications.save_error');
      showNotification(errorMessage, 'error');
    }
  };

  const _tabs = [
    { id: 'account', label: t('ui.settings.tabs.account'), icon: UserIcon },
    {
      id: 'security',
      label: t('ui.settings.tabs.security'),
      icon: ShieldCheckIcon,
    },
    {
      id: 'preferences',
      label: t('ui.settings.tabs.preferences'),
      icon: CogIcon,
    },
    { id: 'language', label: t('ui.settings.tabs.language'), icon: CogIcon },
    { id: 'api', label: t('ui.settings.tabs.api'), icon: KeyIcon },
  ];

  const _renderNotificationIcon = (type: NotificationType) => {
    const iconClass = `${styles.notificationIcon} ${styles[`notificationIcon${type.charAt(0).toUpperCase() + type.slice(1)}`]}`;

    switch (type) {
      case 'success':
        return <CheckCircleIcon className={iconClass} />;
      case 'error':
        return <ExclamationCircleIcon className={iconClass} />;
      case 'info':
        return <InformationCircleIcon className={iconClass} />;
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'account':
        return (
          <div className={styles.contentCard}>
            <div className={styles.contentHeader}>
              <h2 className={styles.contentTitle}>
                <UserIcon className={styles.contentIcon} />
                {t('ui.settings.titles.account_settings')}
              </h2>
            </div>
            <div className={styles.contentBody}>
              <form className="space-y-6">
                <div className={styles.formGrid}>
                  <div>
                    <label className={styles.formLabel}>
                      {t('ui.settings.labels.name')}
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={profileData.name}
                        onChange={(e) =>
                          setProfileData({ name: e.target.value })
                        }
                        readOnly={!isEditingName}
                        className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none ${
                          isEditingName
                            ? 'bg-white text-gray-900 focus:ring-emerald-500 focus:border-emerald-500'
                            : 'bg-gray-50 text-gray-500'
                        }`}
                        maxLength={255}
                        disabled={isSaving}
                      />
                      {!isEditingName && (
                        <div className={styles.editContainer}>
                          <button
                            type="button"
                            onClick={handleEditName}
                            className={styles.editLink}
                          >
                            {t('ui.settings.labels.edit')}
                          </button>
                        </div>
                      )}
                    </div>
                    {isEditingName && (
                      <div className={styles.buttonGroup}>
                        <button
                          type="button"
                          onClick={handleSaveName}
                          disabled={isSaving}
                          className={`${styles.buttonPrimary} ${isSaving ? styles.buttonLoading : ''}`}
                        >
                          {isSaving && (
                            <div className={styles.loadingSpinner}></div>
                          )}
                          {isSaving
                            ? getSavingButtonText()
                            : getSaveButtonText()}
                        </button>
                        <button
                          type="button"
                          onClick={handleCancelEdit}
                          disabled={isSaving}
                          className={styles.buttonSecondary}
                        >
                          {t('ui.settings.labels.cancel')}
                        </button>
                      </div>
                    )}
                  </div>

                  <div>
                    <label className={styles.formLabel}>
                      {t('ui.settings.labels.email')}
                    </label>
                    <input
                      type="email"
                      value={user.email}
                      readOnly
                      className={styles.formInputReadonly}
                    />
                  </div>

                  <div>
                    <label className={styles.formLabel}>
                      {t('ui.settings.labels.user_id')}
                    </label>
                    <input
                      type="text"
                      value={user.id}
                      readOnly
                      className={styles.formInputMono}
                    />
                  </div>

                  <div>
                    <label className={styles.formLabel}>
                      {t('ui.settings.labels.role')}
                    </label>
                    <span className={styles.roleBadge}>{user.role_name}</span>
                  </div>
                </div>
              </form>
            </div>
          </div>
        );

      case 'security':
        return (
          <div className={styles.contentCard}>
            <div className={styles.contentHeader}>
              <h2 className={styles.contentTitle}>
                <ShieldCheckIcon className={styles.contentIcon} />
                {t('ui.settings.titles.security_settings')}
              </h2>
            </div>
            <div className={styles.contentBody}>
              <div className={styles.securitySpaceY}>
                <div className={styles.securityItemFlex}>
                  <div className={styles.securityItemFlexOne}>
                    <h4 className={styles.securityItemTitleH4}>
                      {t('ui.settings.security.password_change.title')}
                    </h4>
                    <p className={styles.securityItemDescriptionP}>
                      {t('ui.settings.security.password_change.description')}
                    </p>
                  </div>
                  <div className={styles.securityItemButtonContainer}>
                    <button className={styles.buttonWhite}>
                      {t('ui.settings.labels.change')}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-900">
                      {t('ui.settings.security.two_factor.title')}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {t('ui.settings.security.two_factor.description')}
                    </p>
                  </div>
                  <div className="ml-4">
                    <button className={styles.buttonPrimary}>
                      {t('ui.settings.labels.enable')}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-900">
                      {t('ui.settings.security.login_history.title')}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {t('ui.settings.security.login_history.description')}
                    </p>
                  </div>
                  <div className="ml-4">
                    <button className={styles.buttonWhite}>
                      {t('ui.settings.labels.view')}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'preferences':
        return (
          <div className={styles.contentCard}>
            <div className={styles.contentHeader}>
              <h2 className={styles.contentTitle}>
                <CogIcon className={styles.contentIcon} />
                {t('ui.settings.titles.preferences_settings')}
              </h2>
            </div>
            <div className={styles.contentBody}>
              <form className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('ui.settings.labels.timezone')}
                  </label>
                  <select className={styles.formSelect}>
                    <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                    <option value="UTC">UTC</option>
                  </select>
                </div>

                <div className="flex gap-3 pt-4">
                  <button type="submit" className={styles.buttonPrimary}>
                    {t('ui.settings.labels.save')}
                  </button>
                  <button type="button" className={styles.buttonWhite}>
                    {t('ui.settings.labels.reset')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        );

      case 'language':
        return (
          <div className={styles.contentCard}>
            <div className={styles.contentHeader}>
              <h2 className={styles.contentTitle}>
                <CogIcon className={styles.contentIcon} />
                {t('ui.settings.titles.language_settings')}
              </h2>
            </div>
            <div className={styles.contentBody}>
              <form className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('ui.settings.labels.current_language')}
                  </label>
                  <p className="text-sm text-gray-600 mb-4">
                    現在の言語: {currentLanguage}
                  </p>
                  <LanguageSwitcher />
                </div>
              </form>
            </div>
          </div>
        );

      case 'api':
        return (
          <div className={styles.contentCard}>
            <div className={styles.contentHeader}>
              <h2 className={styles.contentTitle}>
                <KeyIcon className={styles.contentIcon} />
                {t('ui.settings.titles.api_settings')}
              </h2>
            </div>
            <div className={styles.contentBody}>
              <div className="space-y-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    {t('ui.settings.api.api_key')}
                  </h4>
                  <div className="font-mono text-sm bg-white border border-gray-200 rounded px-3 py-2 mb-3">
                    <span className="text-gray-400">
                      sk-••••••••••••••••••••••••••
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button className={styles.buttonSmall}>
                      {t('ui.settings.api.buttons.view')}
                    </button>
                    <button className={styles.buttonSmall}>
                      {t('ui.settings.api.buttons.copy')}
                    </button>
                    <button className={styles.buttonDanger}>
                      {t('ui.settings.api.buttons.regenerate')}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    {t('ui.settings.api.access_permissions')}
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        className={styles.checkbox}
                        defaultChecked
                      />
                      <span className="text-sm text-gray-700">
                        {t('ui.settings.api.permissions.read')}
                      </span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className={styles.checkbox} />
                      <span className="text-sm text-gray-700">
                        {t('ui.settings.api.permissions.write')}
                      </span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className={styles.checkbox} />
                      <span className="text-sm text-gray-700">
                        {t('ui.settings.api.permissions.admin')}
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <AuthenticatedLayout user={user} currentPath="/settings">
      <div className={styles.settingsContainer}>
        <div className={styles.pageContainer}>
          {/* 通知 */}
          {notification && (
            <div
              className={`${styles.notificationFixed} ${
                notification.type === 'success'
                  ? styles.notificationSuccess
                  : notification.type === 'error'
                    ? styles.notificationError
                    : styles.notificationDefault
              }`}
            >
              {notification.message}
            </div>
          )}
          {/* パンくずリスト */}
          <nav className={styles.breadcrumb}>
            <ol className={styles.breadcrumbList}>
              <li className={styles.breadcrumbItem}>
                <Link href="/dashboard" className={styles.breadcrumbLink}>
                  <svg
                    className={styles.breadcrumbIcon}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
                  </svg>
                  {t('ui.settings.breadcrumb.dashboard')}
                </Link>
              </li>
              <li>
                <div className="flex items-center">
                  <svg
                    className={styles.breadcrumbSeparator}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    ></path>
                  </svg>
                  <span className={styles.breadcrumbCurrent}>
                    {t('ui.settings.breadcrumb.settings')}
                  </span>
                </div>
              </li>
            </ol>
          </nav>

          {/* メインコンテンツ */}
          <div className={styles.mainLayout}>
            {/* サイドバー */}
            <div className={styles.sidebar}>
              <div className={styles.sidebarCard}>
                <h2 className={styles.sidebarTitle}>
                  {t('ui.settings.sidebar.menu_title')}
                </h2>
                <nav className={styles.sidebarNav}>
                  <button
                    onClick={() => handleTabChange('account')}
                    className={`${styles.navButton} ${
                      activeTab === 'account'
                        ? styles.navButtonActive
                        : styles.navButtonInactive
                    }`}
                  >
                    <UserIcon className={styles.navIcon} />
                    {t('ui.settings.sidebar.account_settings')}
                  </button>
                  <button
                    onClick={() => handleTabChange('security')}
                    className={`${styles.navButton} ${
                      activeTab === 'security'
                        ? styles.navButtonActive
                        : styles.navButtonInactive
                    }`}
                  >
                    <ShieldCheckIcon className={styles.navIcon} />
                    {t('ui.settings.sidebar.security_settings')}
                  </button>
                  <button
                    onClick={() => handleTabChange('preferences')}
                    className={`${styles.navButton} ${
                      activeTab === 'preferences'
                        ? styles.navButtonActive
                        : styles.navButtonInactive
                    }`}
                  >
                    <CogIcon className={styles.navIcon} />
                    {t('ui.settings.sidebar.preferences_settings')}
                  </button>
                  <button
                    onClick={() => handleTabChange('api')}
                    className={`${styles.navButton} ${
                      activeTab === 'api'
                        ? styles.navButtonActive
                        : styles.navButtonInactive
                    }`}
                  >
                    <KeyIcon className={styles.navIcon} />
                    {t('ui.settings.sidebar.api_settings')}
                  </button>
                </nav>
              </div>
            </div>

            {/* メインコンテンツ */}
            <div className={styles.content}>{renderTabContent()}</div>
          </div>
        </div>
      </div>
    </AuthenticatedLayout>
  );
}
