import React, { useEffect, useState } from 'react';
import { Link } from '@inertiajs/react';
import {
  UserIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  CodeBracketIcon,
  ClockIcon,
  ChartBarIcon,
  CogIcon,
  DocumentTextIcon,
  AtSymbolIcon,
  IdentificationIcon,
  TagIcon,
} from '@heroicons/react/24/outline';
import styles from '@styles/Dashboard.module.css';
import { AuthenticatedLayout } from '@layouts/AuthenticatedLayout';
import { useI18n } from '@hooks/useI18n';

interface User {
  id: number;
  name: string;
  email: string;
  role: string | null;
  role_name: string | null;
  last_login_at: string | null;
}

interface DashboardProps {
  user: User;
}

export default function Dashboard({ user }: DashboardProps) {
  const { t } = useI18n();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatLastLogin = (lastLoginAt?: string | null) => {
    if (!lastLoginAt) return t('ui.dashboard.no_login_record');
    const date = new Date(lastLoginAt);
    return formatTime(date);
  };

  const handleEditProfile = () => {
    window.location.href = '/settings#account';
  };

  const quickActions = [
    {
      title: t('ui.dashboard.quick_actions.api_docs.title'),
      description: t('ui.dashboard.quick_actions.api_docs.description'),
      icon: DocumentTextIcon,
      link: '/api/v1/docs',
      color: styles.blue,
      bgColor: styles.bgBlue,
      external: true,
    },
    {
      title: t('ui.dashboard.quick_actions.settings.title'),
      description: t('ui.dashboard.quick_actions.settings.description'),
      icon: CogIcon,
      link: '/settings',
      color: styles.green,
      bgColor: styles.bgGreen,
      external: false,
    },
    {
      title: t('ui.dashboard.quick_actions.health_check.title'),
      description: t('ui.dashboard.quick_actions.health_check.description'),
      icon: ChartBarIcon,
      link: '/healthcheck',
      color: styles.indigo,
      bgColor: styles.bgIndigo,
      external: true,
    },
  ];

  const stats = [
    {
      title: t('ui.dashboard.stats.user_info'),
      value: user?.role_name || 'Unknown',
      icon: UserIcon,
      color: styles.blue,
      bgColor: styles.bgBlue,
      borderColor: styles.borderBlue,
    },
    {
      title: t('ui.dashboard.stats.status'),
      value: t('ui.dashboard.stats.active'),
      icon: CheckCircleIcon,
      color: styles.green,
      bgColor: styles.bgGreen,
      borderColor: styles.borderGreen,
    },
    {
      title: t('ui.dashboard.stats.session'),
      value: t('ui.dashboard.stats.logged_in'),
      icon: ShieldCheckIcon,
      color: styles.indigo,
      bgColor: styles.bgIndigo,
      borderColor: styles.borderIndigo,
    },
    {
      title: t('ui.dashboard.stats.api_access'),
      value: t('ui.dashboard.stats.available'),
      icon: CodeBracketIcon,
      color: styles.purple,
      bgColor: styles.bgPurple,
      borderColor: styles.borderPurple,
    },
  ];

  if (!user) {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingContent}>
          <div className={styles.loadingSpinner}></div>
          <p className={styles.loadingText}>{t('ui.dashboard.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <AuthenticatedLayout user={user} currentPath="/dashboard">
      <div className={styles.container}>
        {/* ヘッダー */}
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <div>
              <h1 className={styles.title}>
                <ChartBarIcon className={styles.titleIcon} />
                {t('ui.dashboard.title')}
              </h1>
              <p className={styles.subtitle}>
                {t('ui.dashboard.greeting', { name: user.name })}
              </p>
            </div>
            <div className={styles.timeInfo}>
              <p className={styles.timeText}>
                <ClockIcon className={styles.timeIcon} />
                <span className={styles.timeLabel}>
                  {t('ui.dashboard.current_time')}
                </span>{' '}
                {formatTime(currentTime)}
              </p>
              <p className={styles.timeText}>
                <ClockIcon className={styles.timeIcon} />
                <span className={styles.timeLabel}>
                  {t('ui.dashboard.last_login')}
                </span>{' '}
                {formatLastLogin(user.last_login_at)}
              </p>
            </div>
          </div>
        </div>

        {/* 統計カード */}
        <div className={styles.statsGrid}>
          {stats.map((stat, index) => (
            <div
              key={index}
              className={`${styles.statCard} ${stat.borderColor}`}
            >
              <div className={styles.statCardBody}>
                <div className={styles.statCardContent}>
                  <div className={styles.statCardText}>
                    <div className={styles.statCardTitle}>{stat.title}</div>
                    <div className={styles.statCardValue}>{stat.value}</div>
                  </div>
                  <div className={`${styles.statCardIcon} ${stat.bgColor}`}>
                    <stat.icon className={`${styles.statIcon} ${stat.color}`} />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* メインコンテンツ */}
        <div className={styles.mainGrid}>
          {/* ユーザー情報 */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h3 className={styles.cardTitle}>
                <UserIcon className={styles.cardTitleIcon} />
                {t('ui.dashboard.user_card.title')}
              </h3>
            </div>
            <div className={styles.cardBody}>
              <div className={styles.userInfo}>
                <div className={styles.userAvatar}>
                  <div className={styles.userAvatarCircle}>
                    <UserIcon className={styles.userAvatarIcon} />
                  </div>
                </div>
                <div className={styles.userDetails}>
                  <div className={styles.userPropertiesGrid}>
                    <div className={styles.userPropertyBox}>
                      <div className={styles.userPropertyHeader}>
                        <UserIcon className={styles.userPropertyIcon} />
                        <span className={styles.userPropertyLabel}>
                          {t('ui.dashboard.user_card.labels.name')}
                        </span>
                      </div>
                      <div className={styles.userPropertyValue}>
                        {user.name}
                      </div>
                    </div>

                    <div className={styles.userPropertyBox}>
                      <div className={styles.userPropertyHeader}>
                        <AtSymbolIcon className={styles.userPropertyIcon} />
                        <span className={styles.userPropertyLabel}>
                          {t('ui.dashboard.user_card.labels.email')}
                        </span>
                      </div>
                      <div className={styles.userPropertyValue}>
                        {user.email}
                      </div>
                    </div>

                    <div className={styles.userPropertyBox}>
                      <div className={styles.userPropertyHeader}>
                        <TagIcon className={styles.userPropertyIcon} />
                        <span className={styles.userPropertyLabel}>
                          {t('ui.dashboard.user_card.labels.role')}
                        </span>
                      </div>
                      <div className={styles.userPropertyBadge}>
                        {user.role_name}
                      </div>
                    </div>

                    <div className={styles.userPropertyBox}>
                      <div className={styles.userPropertyHeader}>
                        <IdentificationIcon
                          className={styles.userPropertyIcon}
                        />
                        <span className={styles.userPropertyLabel}>
                          {t('ui.dashboard.user_card.labels.id')}
                        </span>
                      </div>
                      <div className={styles.userPropertyId}>{user.id}</div>
                    </div>
                  </div>
                  <div className={styles.userActions}>
                    <button
                      className={styles.editButton}
                      onClick={handleEditProfile}
                    >
                      <UserIcon className={styles.editButtonIcon} />
                      {t('ui.dashboard.user_card.edit_profile')}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* クイックアクション */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h3 className={styles.cardTitle}>
                <CodeBracketIcon className={styles.cardTitleIcon} />
                {t('ui.dashboard.quick_actions.title')}
              </h3>
            </div>
            <div className={styles.cardBody}>
              <div className={styles.actionsList}>
                {quickActions.map((action, index) =>
                  action.external ? (
                    <a
                      key={index}
                      href={action.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`${styles.actionItem} group no-underline`}
                    >
                      <div className={`${styles.actionIcon} ${action.bgColor}`}>
                        <action.icon
                          className={`${styles.actionIconInner} ${action.color}`}
                        />
                      </div>
                      <div className={styles.actionContent}>
                        <div className={styles.actionTitle}>{action.title}</div>
                        <div className={styles.actionDescription}>
                          {action.description}
                        </div>
                      </div>
                      <div className={styles.actionArrow}>
                        <svg
                          className={styles.actionArrowIcon}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </div>
                    </a>
                  ) : (
                    <Link
                      key={index}
                      href={action.link}
                      className={`${styles.actionItem} group no-underline`}
                    >
                      <div className={`${styles.actionIcon} ${action.bgColor}`}>
                        <action.icon
                          className={`${styles.actionIconInner} ${action.color}`}
                        />
                      </div>
                      <div className={styles.actionContent}>
                        <div className={styles.actionTitle}>{action.title}</div>
                        <div className={styles.actionDescription}>
                          {action.description}
                        </div>
                      </div>
                      <div className={styles.actionArrow}>
                        <svg
                          className={styles.actionArrowIcon}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </div>
                    </Link>
                  ),
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AuthenticatedLayout>
  );
}
