import { useCallback } from 'react';
import { useApi } from './useApi';

/**
 * 管理者関連APIのカスタムフック
 *
 * ユーザー管理、システム設定、APIキー管理など
 * 管理者権限が必要なAPI呼び出しを管理
 */
export function useAdminApi() {
  const api = useApi({ showGlobalLoader: true });

  /**
   * ユーザー一覧取得
   */
  const getUsers = useCallback(
    async (params?: { page?: number; limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.append('page', params.page.toString());
      if (params?.limit) searchParams.append('limit', params.limit.toString());

      const url = `/api/v1/admin/users${searchParams.toString() ? `?${searchParams}` : ''}`;
      return api.call<{
        users: Array<{ id: number; name: string; email: string; role: string }>;
        total: number;
        page: number;
        limit: number;
      }>(url, { method: 'GET' });
    },
    [api],
  );

  /**
   * ユーザー削除
   */
  const deleteUser = useCallback(
    async (userId: number) => {
      return api.call(`/api/v1/admin/users/${userId}`, {
        method: 'DELETE',
      });
    },
    [api],
  );

  /**
   * APIキー生成
   */
  const generateApiKey = useCallback(
    async (keyData: {
      name: string;
      permissions: string[];
      expires_at?: string;
    }) => {
      return api.call<{
        key: string;
        id: string;
        name: string;
        permissions: string[];
        created_at: string;
        expires_at?: string;
      }>('/api/v1/admin/api-keys', {
        method: 'POST',
        body: JSON.stringify(keyData),
      });
    },
    [api],
  );

  /**
   * APIキー一覧取得
   */
  const getApiKeys = useCallback(async () => {
    return api.call<
      Array<{
        id: string;
        name: string;
        permissions: string[];
        created_at: string;
        last_used_at?: string;
        expires_at?: string;
      }>
    >('/api/v1/admin/api-keys', { method: 'GET' });
  }, [api]);

  /**
   * APIキー削除
   */
  const revokeApiKey = useCallback(
    async (keyId: string) => {
      return api.call(`/api/v1/admin/api-keys/${keyId}`, {
        method: 'DELETE',
      });
    },
    [api],
  );

  /**
   * システム統計取得
   */
  const getSystemStats = useCallback(async () => {
    return api.call<{
      total_users: number;
      active_users: number;
      total_api_calls: number;
      system_health: 'healthy' | 'warning' | 'error';
    }>('/api/v1/admin/stats', { method: 'GET' });
  }, [api]);

  return {
    ...api,
    getUsers,
    deleteUser,
    generateApiKey,
    getApiKeys,
    revokeApiKey,
    getSystemStats,
  };
}
