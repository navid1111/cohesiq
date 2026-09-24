import { auth } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";
import { fetchApi } from "@/lib/api/client";
import type { Creator } from "@/lib/types";
import {
  exchangeTikTokCode,
  getAuthorizedTikTokUser,
  getTikTokOAuthConfig,
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

function normalizeTikTokUsername(username: string | undefined) {
  return username?.trim().replace(/^@/, "");
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const error = searchParams.get("error");

  const origin = req.nextUrl.origin;

  if (error) {
    return NextResponse.redirect(
      buildRedirect(origin, "/creator/dashboard/connect-tiktok", { error })
    );
  }

  const stateCookie = req.cookies.get("tiktok_oauth_state")?.value;
  if (!code || !state || state !== stateCookie) {
    return NextResponse.redirect(
      buildRedirect(origin, "/creator/dashboard/connect-tiktok", {
        error: "invalid_state",
      })
    );
  }

  let config;
  try {
    config = getTikTokOAuthConfig();
  } catch {
    return NextResponse.redirect(
      buildRedirect(origin, "/creator/dashboard/connect-tiktok", {
        error: "config_missing",
      })
    );
  }

  try {
    const tokens = await exchangeTikTokCode(config, code);
    const tiktokUser = await getAuthorizedTikTokUser(tokens.access_token);
    const username = normalizeTikTokUsername(tiktokUser?.username);

    if (!tiktokUser) {
      return NextResponse.redirect(
        buildRedirect(origin, "/creator/dashboard/connect-tiktok", {
          error: "no_user",
        })
      );
    }

    if (!username) {
      return NextResponse.redirect(
        buildRedirect(origin, "/creator/dashboard/connect-tiktok", {
          error: "username_unavailable",
        })
      );
    }

    const { getToken } = await auth();
    const token = await getToken();
    if (!token) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    let creator: Creator;
    try {
      creator = await fetchApi<Creator>("/creators/me", { token });
    } catch {
      return NextResponse.redirect(
        buildRedirect(origin, "/creator/dashboard/connect-tiktok", {
          error: "creator_not_found",
        })
      );
    }

    try {
      await fetchApi(`/creators/${creator.id}/platforms/tiktok/enrich`, {
        method: "POST",
        token,
        body: JSON.stringify({
          profile_ref: username,
          recent_post_limit: 6,
        }),
      });
    } catch (error) {
      console.error("TikTok backend enrichment failed:", error);
      return NextResponse.redirect(
        buildRedirect(origin, "/creator/dashboard/connect-tiktok", {
          error: "backend_error",
        })
      );
    }

    const response = NextResponse.redirect(
      buildRedirect(origin, "/creator/dashboard/connect-tiktok", {
        success: "true",
        username,
      })
    );
    response.cookies.set("tiktok_oauth_state", "", {
      path: "/",
      maxAge: 0,
    });
    return response;
  } catch (err) {
    console.error("TikTok OAuth callback error:", err);
    return NextResponse.redirect(
      buildRedirect(origin, "/creator/dashboard/connect-tiktok", {
        error: "server_error",
      })
    );
  }
}

