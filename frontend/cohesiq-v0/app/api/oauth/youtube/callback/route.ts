import { auth } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";
import { fetchApi } from "@/lib/api/client";
import type { Creator } from "@/lib/types";
import {
  exchangeYouTubeCode,
  getAuthorizedYouTubeChannel,
  getYouTubeOAuthConfig,
} from "../_lib/oauth";

function buildRedirect(origin: string, path: string, params?: Record<string, string>) {
  const url = new URL(path, origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, value);
    });
  }
  return url;
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const error = searchParams.get("error");

  const origin = req.nextUrl.origin;

  if (error) {
    const redirectUrl = buildRedirect(origin, "/creator/dashboard/connect-youtube", {
      error,
    });
    return NextResponse.redirect(redirectUrl);
  }

  const stateCookie = req.cookies.get("youtube_oauth_state")?.value;
  if (!code || !state || state !== stateCookie) {
    const redirectUrl = buildRedirect(origin, "/creator/dashboard/connect-youtube", {
      error: "invalid_state",
    });
    return NextResponse.redirect(redirectUrl);
  }

  let config;
  try {
    config = getYouTubeOAuthConfig();
  } catch (err) {
    const redirectUrl = buildRedirect(origin, "/creator/dashboard/connect-youtube", {
      error: "config_missing",
    });
    return NextResponse.redirect(redirectUrl);
  }

  try {
    const tokens = await exchangeYouTubeCode(config, code);
    const channel = await getAuthorizedYouTubeChannel(tokens.access_token);
    if (!channel) {
      const redirectUrl = buildRedirect(origin, "/creator/dashboard/connect-youtube", {
        error: "no_channel",
      });
      return NextResponse.redirect(redirectUrl);
    }

    const { getToken } = await auth();
    const token = await getToken();
    if (!token) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    let creator: Creator;
    try {
      creator = await fetchApi<Creator>("/creators/me", { token });
    } catch (error) {
      const redirectUrl = buildRedirect(origin, "/creator/dashboard/connect-youtube", {
        error: "creator_not_found",
      });
      return NextResponse.redirect(redirectUrl);
    }

    try {
      await fetchApi(`/creators/${creator.id}/platforms/youtube/enrich`, {
        method: "POST",
        token,
        body: JSON.stringify({
          channel_ref: channel.id,
          recent_video_limit: 5,
        }),
      });
    } catch (error) {
      const redirectUrl = buildRedirect(origin, "/creator/dashboard/connect-youtube", {
        error: "backend_error",
      });
      return NextResponse.redirect(redirectUrl);
    }

    const redirectUrl = buildRedirect(origin, "/creator/dashboard/connect-youtube", {
      success: "true",
      channel: channel.id,
    });
    const response = NextResponse.redirect(redirectUrl);
    response.cookies.set("youtube_oauth_state", "", {
      path: "/",
      maxAge: 0,
    });
    return response;
  } catch (err) {
    console.error("YouTube OAuth callback error:", err);
    const redirectUrl = buildRedirect(origin, "/creator/dashboard/connect-youtube", {
      error: "server_error",
    });
    return NextResponse.redirect(redirectUrl);
  }
}
