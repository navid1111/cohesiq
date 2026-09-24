const TIKTOK_SCOPES = [
  "user.info.basic",
  "user.info.profile",
  "user.info.stats",
];

export interface TikTokOAuthConfig {
  clientKey: string;
  clientSecret: string;
  redirectUri: string;
}

export interface TikTokTokenResponse {
  access_token: string;
  expires_in?: number;
  open_id?: string;
  refresh_expires_in?: number;
  refresh_token?: string;
  scope?: string;
  token_type?: string;
}

export interface TikTokUserSummary {
  open_id: string;
  username?: string;
  display_name?: string;
  avatar_url?: string;
  profile_deep_link?: string;
}

export class TikTokOAuthConfigError extends Error {
  constructor(public readonly missingKeys: string[]) {
    super(`TikTok OAuth is not configured. Missing: ${missingKeys.join(", ")}`);
  }
}

export function getTikTokOAuthConfig(): TikTokOAuthConfig {
  const clientKey = process.env.TIKTOK_CLIENT_KEY;
  const clientSecret = process.env.TIKTOK_CLIENT_SECRET;
  const redirectUri = process.env.TIKTOK_REDIRECT_URI;

  const missingKeys = [
    ["TIKTOK_CLIENT_KEY", clientKey],
    ["TIKTOK_CLIENT_SECRET", clientSecret],
    ["TIKTOK_REDIRECT_URI", redirectUri],
  ]
    .filter(([, value]) => !value)
    .map(([key]) => key);

  if (missingKeys.length > 0) {
    throw new TikTokOAuthConfigError(missingKeys);
  }

  return { clientKey, clientSecret, redirectUri };
}

export function buildTikTokAuthUrl(config: TikTokOAuthConfig, state: string) {
  const url = new URL("https://www.tiktok.com/v2/auth/authorize/");
  url.searchParams.set("client_key", config.clientKey);
  url.searchParams.set("redirect_uri", config.redirectUri);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("scope", TIKTOK_SCOPES.join(","));
  url.searchParams.set("state", state);
  return url.toString();
}

export async function exchangeTikTokCode(
  config: TikTokOAuthConfig,
  code: string
): Promise<TikTokTokenResponse> {
  const response = await fetch("https://open.tiktokapis.com/v2/oauth/token/", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_key: config.clientKey,
      client_secret: config.clientSecret,
      code,
      grant_type: "authorization_code",
      redirect_uri: config.redirectUri,
    }),
  });

  if (!response.ok) {
    throw new Error(`TikTok token exchange failed with status ${response.status}`);
  }

  const data = await response.json();
  if (data.error) {
    throw new Error(data.error_description || data.error);
  }
  return data;
}

export async function getAuthorizedTikTokUser(
  accessToken: string
): Promise<TikTokUserSummary | null> {
  const url = new URL("https://open.tiktokapis.com/v2/user/info/");
  url.searchParams.set(
    "fields",
    [
      "open_id",
      "username",
      "display_name",
      "avatar_url",
      "profile_deep_link",
    ].join(",")
  );

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error(`TikTok user lookup failed with status ${response.status}`);
  }

  const data = await response.json();
  if (data.error && data.error.code !== "ok") {
    throw new Error(data.error.message || data.error.code);
  }

  const user = data.data?.user;
  if (!user?.open_id) {
    return null;
  }

  return user;
}

