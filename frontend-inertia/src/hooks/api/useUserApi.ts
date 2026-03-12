import { useCallback } from 'react';
import { useApi } from './useApi';

/**
 * ユーザー関連APIのカスタムフック
 *
 * プロフィール更新、パスワード変更など
 * ユーザーに関連するAPI呼び出しを管理
 */
export function useUserApi() {
  const api = useApi();

  /**
   * ユーザープロフィール更新
   */
  const updateProfile = useCallback(
    async (profileData: { name: string }) => {
      return api.call<{ name: string; email: string }>('/api/v1/user/profile', {
        method: 'PATCH',
        body: JSON.stringify(profileData),
      });
    },
    [api],
  );

  /**
   * パスワード変更
   */
  const changePassword = useCallback(
    async (passwordData: {
      current_password: string;
      new_password: string;
    }) => {
      return api.call('/api/v1/user/password', {
        method: 'PATCH',
        body: JSON.stringify(passwordData),
      });
    },
    [api],
  );

  /**
   * ユーザー情報取得
   */
  const getUserProfile = useCallback(async () => {
    return api.call<{ id: number; name: string; email: string; role: string }>(
      '/api/v1/user/profile',
      {
        method: 'GET',
      },
    );
  }, [api]);

  /**
   * アバター画像アップロード（将来拡張用）
   */
  const uploadAvatar = useCallback(
    async (file: File) => {
      const formData = new FormData();
      formData.append('avatar', file);

      return api.call<{ avatar_url: string }>('/api/v1/user/avatar', {
        method: 'POST',
        body: formData,
        headers: {
          // Content-Typeを削除してブラウザに任せる（multipart/form-dataのため）
        },
      });
    },
    [api],
  );

  return {
    ...api,
    updateProfile,
    changePassword,
    getUserProfile,
    uploadAvatar,
  };
}
