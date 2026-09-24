const YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"];

export interface YouTubeOAuthConfig {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
}

export interface YouTubeTokenResponse {
  access_token: string;
  expires_in?: number;
  refresh_token?: string;
  scope?: string;
  token_type?: string;
}

export interface YouTubeChannelSummary {
  id: string;
  title?: string;
}

export class YouTubeOAuthConfigError extends Error {
  constructor(public readonly missingKeys: string[]) {
    super(`YouTube OAuth is not configured. Missing: ${missingKeys.join(", ")}`);
  }
}

export function getYouTubeOAuthConfig(): YouTubeOAuthConfig {
  const clientId = process.env.YOUTUBE_CLIENT_ID;
  const clientSecret = process.env.YOUTUBE_CLIENT_SECRET;
  const redirectUri = process.env.YOUTUBE_REDIRECT_URI;

  const missingKeys = [
    ["YOUTUBE_CLIENT_ID", clientId],
    ["YOUTUBE_CLIENT_SECRET", clientSecret],
    ["YOUTUBE_REDIRECT_URI", redirectUri],
  ]
    .filter(([, value]) => !value)
    .map(([key]) => key);

  if (missingKeys.length > 0) {
    throw new YouTubeOAuthConfigError(missingKeys);
  }

  return { clientId, clientSecret, redirectUri };
}

export function buildYouTubeAuthUrl(config: YouTubeOAuthConfig, state: string) {
  const url = new URL("https://accounts.google.com/o/oauth2/v2/auth");
  url.searchParams.set("client_id", config.clientId);
  url.searchParams.set("redirect_uri", config.redirectUri);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("access_type", "offline");
  url.searchParams.set("prompt", "consent");
  url.searchParams.set("include_granted_scopes", "true");
  url.searchParams.set("scope", YOUTUBE_SCOPES.join(" "));
  url.searchParams.set("state", state);
  return url.toString();
}

export async function exchangeYouTubeCode(
  config: YouTubeOAuthConfig,
  code: string
): Promise<YouTubeTokenResponse> {
  const response = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: config.clientId,
      client_secret: config.clientSecret,
      code,
      grant_type: "authorization_code",
      redirect_uri: config.redirectUri,
    }),
  });

  if (!response.ok) {
    throw new Error(`YouTube token exchange failed with status ${response.status}`);
  }

  return response.json();
}

export async function getAuthorizedYouTubeChannel(
  accessToken: string
): Promise<YouTubeChannelSummary | null> {
  const url = new URL("https://www.googleapis.com/youtube/v3/channels");
  url.searchParams.set("part", "snippet");
  url.searchParams.set("mine", "true");

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error(`YouTube channel lookup failed with status ${response.status}`);
  }

  const data = await response.json();
  const channel = data.items?.[0];
  if (!channel?.id) {
    return null;
  }

  return {
    id: channel.id,
    title: channel.snippet?.title,
  };
}
