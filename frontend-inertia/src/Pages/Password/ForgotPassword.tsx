import React, { useState, useEffect } from 'react';
import { useForm } from '@inertiajs/react';
import { EnvelopeIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import styles from '@styles/PasswordReset.module.css';
import { useI18n } from '@hooks/useI18n';
import LanguageSwitcher from '@components/LanguageSwitcher';

/**
 * プロパティ
 * @interface
 */
interface ForgotPasswordProps {
  success?: boolean;
  error?: string;
  errors?: {
    email?: string;
  };
}

/**
 * パスワードリセットページ
 * @param props - プロパティ
 * @return ページコンポーネント
 */
export default function ForgotPassword({
  success: propSuccess,
  error: propError,
  errors: propErrors,
}: ForgotPasswordProps) {
  const { t } = useI18n();
  const [queryError, setQueryError] = useState<string | null>(null);

  useEffect(() => {
    // URLクエリパラメータからエラーを取得
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');
    if (errorParam) {
      setQueryError(errorParam);
      // URLからエラーパラメータを削除
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const error = propError || queryError;
  const { data, setData, post, processing, errors } = useForm({
    email: '',
  });

  // propsとuseFormの両方からエラーを取得
  const allErrors = {
    email: propErrors?.email || errors.email,
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    post('/forgot-password');
  };

  const handleBackToLogin = () => {
    window.location.href = '/login';
  };

  // 成功状態の場合
  if (propSuccess) {
    return (
      <div className={styles.container}>
        <div className={styles.languageSwitcher}>
          <LanguageSwitcher compact />
        </div>

        <div className={styles.card}>
          <div className={styles.successContainer}>
            <div className={styles.successIcon}>
              <EnvelopeIcon className={styles.successIconSvg} />
            </div>

            <h1 className={styles.title}>
              {t('ui.password_reset.forgot_password.title')}
            </h1>

            <p className={styles.successMessage}>
              {t('ui.password_reset.forgot_password.success')}
            </p>

            <button
              type="button"
              onClick={handleBackToLogin}
              className={styles.backButton}
            >
              <ArrowLeftIcon className={styles.backButtonIcon} />
              {t('ui.password_reset.forgot_password.back_to_login')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.languageSwitcher}>
        <LanguageSwitcher compact />
      </div>

      <div className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.title}>
            {t('ui.password_reset.forgot_password.title')}
          </h1>
          <p className={styles.subtitle}>
            {t('ui.password_reset.forgot_password.subtitle')}
          </p>
          <p className={styles.description}>
            {t('ui.password_reset.forgot_password.description')}
          </p>
        </div>

        {error && (
          <div className={styles.errorContainer}>
            <p className={styles.errorMessage}>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="email" className={styles.label}>
              {t('ui.password_reset.forgot_password.form.email.label')}
            </label>
            <div className={styles.inputWrapper}>
              <div className={styles.inputIcon}>
                <EnvelopeIcon className={styles.inputIconSvg} />
              </div>
              <input
                id="email"
                name="email"
                type="email"
                value={data.email}
                onChange={(e) => setData('email', e.target.value)}
                className={`${styles.input} ${allErrors.email ? styles.inputError : ''}`}
                placeholder={t(
                  'ui.password_reset.forgot_password.form.email.placeholder',
                )}
                required
                disabled={processing}
              />
            </div>
            {allErrors.email && (
              <p className={styles.fieldError}>{allErrors.email}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={processing}
            className={`${styles.submitButton} ${processing ? styles.submitButtonDisabled : ''}`}
          >
            {processing
              ? t('ui.login.form.submitting')
              : t('ui.password_reset.forgot_password.form.submit')}
          </button>
        </form>

        <div className={styles.footer}>
          <button
            type="button"
            onClick={handleBackToLogin}
            className={styles.backLink}
          >
            <ArrowLeftIcon className={styles.backLinkIcon} />
            {t('ui.password_reset.forgot_password.back_to_login')}
          </button>
        </div>
      </div>
    </div>
  );
}
