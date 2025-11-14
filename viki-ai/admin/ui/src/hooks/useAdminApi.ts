import { useCallback } from "react";
import { useAuth } from "./useAuth";
import useEnvJson from "./useEnvJson";
import { Env } from "../types/env";
import { getAuthToken as getAuthTokenUtil } from '../utils/auth';

export const useAdminApi = () => {
  const { getUserId } = useAuth();
  const env = useEnvJson<Env>();

  const getAuthToken = useCallback((): string => {
    return getAuthTokenUtil() || ''
  }, []);

  const makeAuthenticatedRequest = useCallback(async (
    endpoint: string,
    options: RequestInit = {}
  ) => {
    if (!env) {
      throw new Error('Environment configuration not loaded');
    }

    const token = getAuthToken()
    const headers = {
      'Content-Type': 'application/json',
      'userId': getUserId(),
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(`${env.ADMIN_API}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  }, [env, getUserId, getAuthToken]);

  const get = useCallback(async (endpoint: string) => {
    const response = await makeAuthenticatedRequest(endpoint, { method: 'GET' });
    return response.json();
  }, [makeAuthenticatedRequest]);

  const post = useCallback(async (endpoint: string, data: any) => {
    const response = await makeAuthenticatedRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response.json();
  }, [makeAuthenticatedRequest]);

  const put = useCallback(async (endpoint: string, data: any) => {
    const response = await makeAuthenticatedRequest(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return response.json();
  }, [makeAuthenticatedRequest]);

  const del = useCallback(async (endpoint: string) => {
    const response = await makeAuthenticatedRequest(endpoint, { method: 'DELETE' });
    return response.json();
  }, [makeAuthenticatedRequest]);

  return {
    get,
    post,
    put,
    delete: del,
    makeAuthenticatedRequest,
  };
};