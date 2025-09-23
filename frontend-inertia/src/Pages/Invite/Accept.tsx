import React, { useState, useEffect } from 'react';
import { useForm } from '@inertiajs/react';
import {
  EyeIcon,
  EyeSlashIcon,
  LockClosedIcon,
  EnvelopeIcon,
  UserIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import styles from '@styles/InviteAccept.module.css';
import { useI18n } from '@hooks/useI18n';
import LanguageSwitcher from '@components/LanguageSwitcher';

/**
 * 招待情報
 * @interface
 */
interface InviteInfo {
  user_email: string;
  user_name: string;
  expires_in_minutes: number;
}

/**
 * プロパティ
 * @interface
 */
interface InviteAcceptProps {
  error?: string;
  token: string;
  invite_info: InviteInfo | null;
  errors?: {
    token?: string;
    password?: string;
  };
}

/**
 * 招待情報ページ
 * @param props - プロパティ
 * @return ページコンポーネント
 */
export default function InviteAccept({
  error: propError,
  token: initialToken,
  invite_info,
  errors: propErrors,
}: InviteAcceptProps) {
  const { t } = useI18n();
  const [showPassword, setShowPassword] = useState(false);
  const [queryError, setQueryError] = useState<string | null>(null);

  useEffect(() => {
    // URLクエリパラメータからエラーを取得
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');
    if (errorParam) {
      setQueryError(errorParam);
      // URLからエラーパラメータを削除
      window.history.replaceState(
        {},
        '',
        window.location.pathname + '?token=' + initialToken,
      );
    }
  }, [initialToken]);

  const error = propError || queryError;
  const { data, setData, post, processing, errors } = useForm({
    token: initialToken || '',
    password: '',
  });

  // propsとuseFormの両方からエラーを取得
  const allErrors = {
    token: propErrors?.token || errors.token,
    password: propErrors?.password || errors.password,
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    post('/invite/accept');
  };

  const formatExpiryTime = (minutes: number) => {
    if (minutes <= 0) {
      return t('ui.invite.expired');
    }
    if (minutes < 60) {
      return t('ui.invite.expires_in_minutes', { minutes });
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return t('ui.invite.expires_in_hours', { hours });
    }
    return t('ui.invite.expires_in_hours_minutes', {
      hours,
      minutes: remainingMinutes,
    });
  };

  return (
    <div className={styles.container}>
      <div className={styles.languageSwitcher}>
        <LanguageSwitcher />
      </div>

      <div className={styles.card}>
        <div className={styles.header}>
          <div className={styles.icon}>
            <EnvelopeIcon className={styles.iconSvg} />
          </div>
          <h1 className={styles.title}>{t('ui.invite.title')}</h1>
          <p className={styles.subtitle}>
            {invite_info
              ? t('ui.invite.subtitle_valid')
              : t('ui.invite.subtitle_error')}
          </p>
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div className={styles.errorContainer}>
            <ExclamationTriangleIcon className={styles.errorIcon} />
            <p className={styles.errorMessage}>{error}</p>
          </div>
        )}

        {/* 招待情報表示 */}
        {invite_info && !error && (
          <div className={styles.inviteInfo}>
            <div className={styles.infoItem}>
              <UserIcon className={styles.infoIcon} />
              <div>
                <span className={styles.infoLabel}>
                  {t('ui.invite.invited_user')}
                </span>
                <span className={styles.infoValue}>
                  {invite_info.user_name}
                </span>
              </div>
            </div>
            <div className={styles.infoItem}>
              <EnvelopeIcon className={styles.infoIcon} />
              <div>
                <span className={styles.infoLabel}>{t('ui.invite.email')}</span>
                <span className={styles.infoValue}>
                  {invite_info.user_email}
                </span>
              </div>
            </div>
            <div className={styles.infoItem}>
              <ClockIcon className={styles.infoIcon} />
              <div>
                <span className={styles.infoLabel}>
                  {t('ui.invite.expires')}
                </span>
                <span className={styles.infoValue}>
                  {formatExpiryTime(invite_info.expires_in_minutes)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* パスワード設定フォーム */}
        {invite_info && !error && (
          <form onSubmit={handleSubmit} className={styles.form}>
            <input type="hidden" name="token" value={data.token} />

            <div className={styles.formGroup}>
              <label htmlFor="password" className={styles.label}>
                {t('ui.invite.form.password.label')}
              </label>
              <div className={styles.inputWrapper}>
                <div className={styles.inputIcon}>
                  <LockClosedIcon className={styles.inputIconSvg} />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={data.password}
                  onChange={(e) => setData('password', e.target.value)}
                  className={`${styles.input} ${allErrors.password ? styles.inputError : ''}`}
                  placeholder={t('ui.invite.form.password.placeholder')}
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  className={styles.passwordToggle}
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeSlashIcon className={styles.passwordToggleIcon} />
                  ) : (
                    <EyeIcon className={styles.passwordToggleIcon} />
                  )}
                </button>
              </div>
              {allErrors.password && (
                <p className={styles.fieldError}>{allErrors.password}</p>
              )}
              <p className={styles.passwordHint}>
                {t('ui.invite.form.password.hint')}
              </p>
            </div>

            <button
              type="submit"
              disabled={processing || !data.password}
              className={`${styles.submitButton} ${processing ? styles.submitting : ''}`}
            >
              {processing
                ? t('ui.invite.form.submitting')
                : t('ui.invite.form.submit')}
            </button>
          </form>
        )}

        {/* トークンなし/無効の場合の案内 */}
        {(!invite_info || error) && (
          <div className={styles.helpText}>
            <p>{t('ui.invite.help_text')}</p>
            <a href="/login" className={styles.loginLink}>
              {t('ui.invite.back_to_login')}
            </a>
          </div>
        )}

        <div className={styles.footer}>
          <p className={styles.secureText}>
            {t('ui.login.footer.secure_connection')}
          </p>
        </div>
      </div>
    </div>
  );
}
