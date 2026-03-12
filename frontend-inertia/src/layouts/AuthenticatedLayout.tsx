import React from 'react';
import { Navbar } from '@components/Navbar';
import styles from '@styles/Layout.module.css';
import { useI18n } from '@hooks/useI18n';

interface User {
  id: number;
  name: string;
  email: string;
  role: string | null;
  role_name: string | null;
}

interface AuthenticatedLayoutProps {
  user: User;
  children: React.ReactNode;
  currentPath?: string;
}

/**
 * レイアウトコンポーネント（認証済）
 *
 * @param props - プロパティ
 * @param props.user - ユーザー情報
 * @param props.children - 子コンポーネント
 * @param props.currentPath - 現在のパス
 * @returns レイアウトコンポーネント
 */
export const AuthenticatedLayout: React.FC<AuthenticatedLayoutProps> = ({
  user,
  children,
  currentPath,
}) => {
  const { t } = useI18n();
  const currentYear = new Date().getFullYear();

  return (
    <div className={styles.layout}>
      <Navbar user={user} currentPath={currentPath} />

      <main className={`${styles.main} ${styles.mainWithNavbar}`}>
        <div className={styles.content} style={{ paddingBottom: '4rem' }}>
          {children}
        </div>
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <small>
            &copy; {currentYear} {t('ui.layout.footer.copyright')}
          </small>
        </div>
      </footer>
    </div>
  );
};
