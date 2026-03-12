import React, { useState, useEffect } from 'react';
import { useForm } from '@inertiajs/react';
import {
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
  ArrowLeftIcon,
  KeyIcon,
} from '@heroicons/react/24/outline';
import styles from '@styles/PasswordReset.module.css';
import { useI18n } from '@hooks/useI18n';
import LanguageSwitcher from '@components/LanguageSwitcher';

/**
 * プロパティ
 * @interface
 */
interface ResetPasswordProps {
  success?: boolean;
  error?: string;
  token?: string;
  email?: string;
  errors?: {
    email?: string;
    token?: string;
    reset_code?: string;
    new_password?: string;
    confirm_password?: string;
  };
}

/**
 * パスワードリセットページ
 * @param props - プロパティ
 * @return ページコンポーネント
 */
export default function ResetPassword({
  success: propSuccess,
  error: propError,
  token: propToken,
  email: propEmail,
  errors: propErrors,
}: ResetPasswordProps) {
  const { t } = useI18n();
  const [queryError, setQueryError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  useEffect(() => {
    // URLクエリパラメータからエラーを取得
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');
    if (errorParam) {
      setQueryError(errorParam);
      // URLからエラーパラメータを削除
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.delete('error');
      window.history.replaceState({}, '', newUrl.toString());
    }
  }, []);

  const error = propError || queryError;

  const { data, setData, post, processing, errors } = useForm({
    email: propEmail || '',
    token: propToken || '',
    reset_code: '',
    new_password: '',
    confirm_password: '',
  });

  // propsとuseFormの両方からエラーを取得
  const allErrors = {
    email: propErrors?.email || errors.email,
    token: propErrors?.token || errors.token,
    reset_code: propErrors?.reset_code || errors.reset_code,
    new_password: propErrors?.new_password || errors.new_password,
    confirm_password: propErrors?.confirm_password || errors.confirm_password,
  };

  // パスワード確認のクライアントサイドバリデーション
  const [confirmPasswordError, setConfirmPasswordError] = useState<
    string | null
  >(null);

  useEffect(() => {
    if (
      data.confirm_password &&
      data.new_password &&
      data.confirm_password !== data.new_password
    ) {
      setConfirmPasswordError(t('ui.password_reset.errors.password_mismatch'));
    } else {
      setConfirmPasswordError(null);
    }
  }, [data.new_password, data.confirm_password, t]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // クライアントサイドバリデーション
    if (data.new_password !== data.confirm_password) {
      setConfirmPasswordError(t('ui.password_reset.errors.password_mismatch'));
      return;
    }

    post('/reset-password');
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
              <LockClosedIcon className={styles.successIconSvg} />
            </div>

            <h1 className={styles.title}>
              {t('ui.password_reset.reset_password.title')}
            </h1>

            <p className={styles.successMessage}>
              {t('ui.password_reset.reset_password.success')}
            </p>

            <button
              type="button"
              onClick={handleBackToLogin}
              className={styles.backButton}
            >
              <ArrowLeftIcon className={styles.backButtonIcon} />
              {t('ui.password_reset.reset_password.back_to_login')}
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
            {t('ui.password_reset.reset_password.title')}
          </h1>
          <p className={styles.subtitle}>
            {t('ui.password_reset.reset_password.subtitle')}
          </p>
          <p className={styles.description}>
            {t('ui.password_reset.reset_password.description')}
          </p>
        </div>

        {error && (
          <div className={styles.errorContainer}>
            <p className={styles.errorMessage}>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* 隠しフィールド（メールアドレス） */}
          <input type="hidden" name="email" value={data.email} />
          {/* 隠しフィールド（リセットトークン） */}
          <input type="hidden" name="token" value={data.token} />

          <div className={styles.formGroup}>
            <label htmlFor="reset_code" className={styles.label}>
              {t('ui.password_reset.reset_password.form.reset_code.label')}
            </label>
            <div className={styles.inputWrapper}>
              <div className={styles.inputIcon}>
                <KeyIcon className={styles.inputIconSvg} />
              </div>
              <input
                id="reset_code"
                name="reset_code"
                type="text"
                value={data.reset_code}
                onChange={(e) => setData('reset_code', e.target.value)}
                className={`${styles.input} ${allErrors.reset_code ? styles.inputError : ''}`}
                placeholder={t(
                  'ui.password_reset.reset_password.form.reset_code.placeholder',
                )}
                required
                disabled={processing}
                maxLength={6}
                pattern="[0-9|A-Z|a-z]{6}"
              />
            </div>
            {allErrors.reset_code && (
              <p className={styles.fieldError}>{allErrors.reset_code}</p>
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="new_password" className={styles.label}>
              {t('ui.password_reset.reset_password.form.new_password.label')}
            </label>
            <div className={styles.inputWrapper}>
              <div className={styles.inputIcon}>
                <LockClosedIcon className={styles.inputIconSvg} />
              </div>
              <input
                id="new_password"
                name="new_password"
                type={showPassword ? 'text' : 'password'}
                value={data.new_password}
                onChange={(e) => setData('new_password', e.target.value)}
                className={`${styles.input} ${allErrors.new_password ? styles.inputError : ''}`}
                placeholder={t(
                  'ui.password_reset.reset_password.form.new_password.placeholder',
                )}
                required
                disabled={processing}
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
            {allErrors.new_password && (
              <p className={styles.fieldError}>{allErrors.new_password}</p>
            )}
            <p className={styles.passwordHint}>
              {t('ui.password_reset.reset_password.form.new_password.hint')}
            </p>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="confirm_password" className={styles.label}>
              {t(
                'ui.password_reset.reset_password.form.confirm_password.label',
              )}
            </label>
            <div className={styles.inputWrapper}>
              <div className={styles.inputIcon}>
                <LockClosedIcon className={styles.inputIconSvg} />
              </div>
              <input
                id="confirm_password"
                name="confirm_password"
                type={showConfirmPassword ? 'text' : 'password'}
                value={data.confirm_password}
                onChange={(e) => setData('confirm_password', e.target.value)}
                className={`${styles.input} ${allErrors.confirm_password || confirmPasswordError ? styles.inputError : ''}`}
                placeholder={t(
                  'ui.password_reset.reset_password.form.confirm_password.placeholder',
                )}
                required
                disabled={processing}
                minLength={8}
              />
              <button
                type="button"
                className={styles.passwordToggle}
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex={-1}
              >
                {showConfirmPassword ? (
                  <EyeSlashIcon className={styles.passwordToggleIcon} />
                ) : (
                  <EyeIcon className={styles.passwordToggleIcon} />
                )}
              </button>
            </div>
            {(allErrors.confirm_password || confirmPasswordError) && (
              <p className={styles.fieldError}>
                {allErrors.confirm_password || confirmPasswordError}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={processing || !!confirmPasswordError}
            className={`${styles.submitButton} ${processing || !!confirmPasswordError ? styles.submitButtonDisabled : ''}`}
          >
            {processing
              ? t('ui.login.form.submitting')
              : t('ui.password_reset.reset_password.form.submit')}
          </button>
        </form>

        <div className={styles.footer}>
          <button
            type="button"
            onClick={handleBackToLogin}
            className={styles.backLink}
          >
            <ArrowLeftIcon className={styles.backLinkIcon} />
            {t('ui.password_reset.reset_password.back_to_login')}
          </button>
        </div>
      </div>
    </div>
  );
}
