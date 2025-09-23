import React, { useState, useEffect } from 'react';
import { useForm } from '@inertiajs/react';
import {
  EyeIcon,
  EyeSlashIcon,
  LockClosedIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';
import styles from '@styles/LoginForm.module.css';
import { useI18n } from '@hooks/useI18n';
import LanguageSwitcher from '@components/LanguageSwitcher';

/**
 * プロパティ
 * @interface
 */
interface LoginProps {
  error?: string;
  email?: string;
  errors?: {
    email?: string;
    password?: string;
  };
}

/**
 * ログインページ
 * @param props - プロパティ
 * @return ページコンポーネント
 */
export default function Login({
  error: propError,
  email: propEmail = '',
  errors: propErrors,
}: LoginProps) {
  const { t } = useI18n();
  const [queryError, setQueryError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    // URLクエリパラメータからエラーと成功メッセージを取得
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');
    const messageParam = urlParams.get('message');

    if (errorParam) {
      setQueryError(errorParam);
    }

    if (messageParam) {
      // 成功メッセージを翻訳
      if (messageParam === 'password_reset_success') {
        setSuccessMessage(t('ui.login.messages.password_reset_success'));
      } else if (messageParam === 'invitation_accepted') {
        setSuccessMessage(t('ui.login.messages.invitation_accepted'));
      }
    }

    // URLからパラメータを削除
    if (errorParam || messageParam) {
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [t]);

  const error = propError || queryError;
  const [showPassword, setShowPassword] = useState(false);
  const { data, setData, post, processing, errors, reset } = useForm({
    email: propEmail,
    password: '',
  });

  // propsとuseFormの両方からエラーを取得
  const allErrors = {
    email: propErrors?.email || errors.email,
    password: propErrors?.password || errors.password,
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    post('/auth/login', {
      onFinish: () => reset('password'),
    });
  };

  return (
    <div className={styles.container}>
      <div className={styles.loginCard}>
        <div className={styles.card}>
          <div className={styles.header}>
            <div className={styles.headerContent}>
              <div className={styles.headerLeft}>
                <div className={styles.formGroup}>
                  <LockClosedIcon className={styles.headerIcon} />
                </div>
                <h2 className={styles.headerTitle}>{t('ui.login.title')}</h2>
              </div>
              <div className={styles.headerRight}>
                <LanguageSwitcher compact={true} />
              </div>
            </div>
            <p className={styles.headerSubtitle}>{t('ui.login.subtitle')}</p>
          </div>

          <div className={styles.body}>
            {successMessage && (
              <div className={`${styles.alert} ${styles.alertSuccess}`}>
                <div className={styles.successContainer}>
                  <svg
                    className={styles.successIcon}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  {successMessage}
                </div>
              </div>
            )}

            {(error || allErrors.email || allErrors.password) && (
              <div className={`${styles.alert} ${styles.alertError}`}>
                <div className={styles.errorContainer}>
                  <svg
                    className={styles.errorIcon}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                  {error ||
                    allErrors.email ||
                    allErrors.password ||
                    t('ui.login.errors.default')}
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className={styles.formContainer}>
              <div className={styles.inputGroup}>
                <label htmlFor="email" className={styles.label}>
                  <EnvelopeIcon className={styles.inputIcon} />
                  {t('ui.login.form.email.label')}
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className={styles.input}
                  placeholder={t('ui.login.form.email.placeholder')}
                  value={data.email}
                  onChange={(e) => setData('email', e.target.value)}
                  disabled={processing}
                />
              </div>

              <div className={styles.inputGroup}>
                <label htmlFor="password" className={styles.label}>
                  <LockClosedIcon className={styles.inputIcon} />
                  {t('ui.login.form.password.label')}
                </label>
                <div className={styles.inputRelative}>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    className={`${styles.input} ${styles.inputPassword}`}
                    placeholder={t('ui.login.form.password.placeholder')}
                    value={data.password}
                    onChange={(e) => setData('password', e.target.value)}
                    disabled={processing}
                  />
                  <button
                    type="button"
                    className={styles.passwordToggle}
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={processing}
                  >
                    {showPassword ? (
                      <EyeSlashIcon className={styles.buttonIcon} />
                    ) : (
                      <EyeIcon className={styles.buttonIcon} />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  className={styles.button}
                  disabled={processing}
                >
                  {processing ? (
                    <div className={styles.buttonContent}>
                      <div className={styles.loadingSpinner}></div>
                      {t('ui.login.form.submitting')}
                    </div>
                  ) : (
                    <div className={styles.buttonContent}>
                      <LockClosedIcon className={styles.buttonIcon} />
                      {t('ui.login.form.submit')}
                    </div>
                  )}
                </button>
              </div>
            </form>

            <div className={styles.forgotPasswordLink}>
              <a href="/forgot-password" className={styles.forgotPasswordText}>
                {t('ui.login.links.forgot_password')}
              </a>
            </div>
          </div>

          <div className={styles.footer}>
            <small className={styles.footerText}>
              <svg
                className={styles.footerIcon}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                  clipRule="evenodd"
                />
              </svg>
              {t('ui.login.footer.secure_connection')}
            </small>
          </div>
        </div>
      </div>
    </div>
  );
}
