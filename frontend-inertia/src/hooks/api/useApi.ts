import { useState, useCallback } from 'react';
import { useI18n } from '../useI18n';

export interface ApiResponse<T = unknown> {
  data: T;
  response: Response;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

export interface UseApiOptions {
  showGlobalLoader?: boolean;
  suppressErrorLogging?: boolean;
}

export interface ApiCallOptions extends RequestInit {
  suppressErrorNotification?: boolean;
}

/**
 * API呼び出し用カスタムフック
 *
 * ローディング状態、エラーハンドリング、レスポンス処理を統一管理
 */
export function useApi(options: UseApiOptions = {}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const { t } = useI18n();

  const { showGlobalLoader = false, suppressErrorLogging = false } = options;

  /**
   * API呼び出し実行
   */
  const call = useCallback(
    async <T = unknown>(
      url: string,
      callOptions: ApiCallOptions = {},
    ): Promise<ApiResponse<T>> => {
      setLoading(true);
      setError(null);

      if (showGlobalLoader) {
        window.dispatchEvent(new CustomEvent('api-loading-start'));
      }

      try {
        const {
          suppressErrorNotification: _suppressErrorNotification,
          ...fetchOptions
        } = callOptions;

        // デフォルトオプション設定
        const defaultOptions: RequestInit = {
          headers: {
            'Content-Type': 'application/json',
            ...fetchOptions.headers,
          },
          credentials: 'include',
          ...fetchOptions,
        };

        const response = await fetch(url, defaultOptions);

        // レスポンスの処理
        let responseData: T;
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
          responseData = await response.json();
        } else {
          responseData = (await response.text()) as T;
        }

        // エラーレスポンスの処理
        if (!response.ok) {
          const errorResponse = responseData as Record<string, unknown>;
          const apiError: ApiError = {
            message:
              (typeof errorResponse?.message === 'string'
                ? errorResponse.message
                : null) || t('ui.common.errors.api_error'),
            status: response.status,
            details: responseData,
          };

          if (!suppressErrorLogging) {
            console.error('[useApi] API Error:', apiError);
          }

          setError(apiError);
          throw apiError;
        }

        return { data: responseData, response };
      } catch (err) {
        const apiError: ApiError =
          err instanceof Error
            ? {
                message: err.message,
                details: err,
              }
            : {
                message: t('ui.common.errors.network_error'),
                details: err,
              };

        if (!suppressErrorLogging) {
          console.error('[useApi] Network Error:', apiError);
        }

        setError(apiError);
        throw apiError;
      } finally {
        setLoading(false);
        if (showGlobalLoader) {
          window.dispatchEvent(new CustomEvent('api-loading-end'));
        }
      }
    },
    [showGlobalLoader, suppressErrorLogging, t],
  );

  /**
   * エラーのクリア
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * ローディング状態のリセット
   */
  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
  }, []);

  return {
    call,
    loading,
    error,
    clearError,
    reset,

    // 便利なヘルパー
    isLoading: loading,
    hasError: !!error,
    errorMessage: error?.message,
  };
}
