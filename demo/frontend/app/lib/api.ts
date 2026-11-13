import { isObject, isDocument, isHealth, isSignedResult, isVerification } from "./contracts";
import type { DocumentInfo, Health, SignedResult, Verification } from "./contracts";
export type { DocumentInfo, Health, SignedResult, Signature, Verification } from "./contracts";

export const API = process.env.NEXT_PUBLIC_API_ORIGIN ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status = 0,
  ) {
    super(message);
  }
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
  validate?: (value: unknown) => value is T,
): Promise<T> {
  const controller = new AbortController();
  const cancel = () => controller.abort();
  if (options.signal?.aborted) controller.abort();
  options.signal?.addEventListener("abort", cancel, { once: true });
  const timer = setTimeout(() => controller.abort(), options.method === "POST" ? 35000 : 6000);
  try {
    const response = await fetch(`${API}${path}`, {
      ...options,
      credentials: "omit",
      cache: "no-store",
      signal: controller.signal,
    });
    if (!response.ok) {
      const data: unknown = await response.json().catch(() => null);
      throw new ApiError(
        isObject(data) && typeof data.detail === "string"
          ? data.detail
          : "Le service n’a pas pu traiter cette demande.",
        response.status,
      );
    }
    if (response.status === 204) return undefined as T;
    const data: unknown = await response.json();
    if (validate && !validate(data))
      throw new ApiError("La réponse du service est inattendue. Actualisez la connexion.");
    return data as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      controller.signal.aborted
        ? "Le service n’a pas répondu à temps. Réessayez dans un instant."
        : "Le service local est inaccessible. Vérifiez qu’il est démarré.",
    );
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener("abort", cancel);
  }
}

export const getHealth = (signal?: AbortSignal) =>
  request<Health>("/api/health", { signal }, isHealth);
export const getDocuments = (signal?: AbortSignal) =>
  request<DocumentInfo[]>(
    "/api/documents",
    { signal },
    (v): v is DocumentInfo[] => Array.isArray(v) && v.every(isDocument),
  );
export const uploadDocument = (file: File) => {
  const body = new FormData();
  body.append("file", file);
  return request<DocumentInfo>("/api/documents", { method: "POST", body }, isDocument);
};
export const removeDocument = (id: string) =>
  request<void>(`/api/documents/${id}`, { method: "DELETE" });
const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});
export const signDocument = (id: string) =>
  request<SignedResult>(
    `/api/documents/${id}/sign`,
    json({ confirm_test_signature: true }),
    isSignedResult,
  );
export const verifyDocument = (id: string, source: "original" | "signed") =>
  request<Verification>(`/api/documents/${id}/verify`, json({ source }), isVerification);

export function size(bytes: number) {
  return `${(bytes / 1024).toLocaleString("fr-FR", { maximumFractionDigits: 1 })} Kio`;
}
export function time(iso: string) {
  const date = new Date(iso);
  return Number.isNaN(date.valueOf())
    ? "Indisponible"
    : date.toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "medium", timeZone: "UTC" });
}
