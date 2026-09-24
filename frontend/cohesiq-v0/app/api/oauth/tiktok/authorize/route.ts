import { auth } from "@clerk/nextjs/server";
import { randomUUID } from "crypto";
import { NextResponse } from "next/server";
import {
  buildTikTokAuthUrl,
  getTikTokOAuthConfig,
  TikTokOAuthConfigError,
} from "../_lib/oauth";

export async function POST() {
  const { userId } = await auth();
  if (!userId) {
    return new NextResponse("Unauthorized", { status: 401 });
  }

  try {
    const state = randomUUID();
    const authUrl = buildTikTokAuthUrl(getTikTokOAuthConfig(), state);

    const response = NextResponse.json({ authUrl });
    response.cookies.set("tiktok_oauth_state", state, {
      path: "/",
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      maxAge: 600,
    });
    return response;
  } catch (error) {
    if (error instanceof TikTokOAuthConfigError) {
      return new NextResponse(error.message, { status: 500 });
    }

    return new NextResponse("TikTok OAuth is not configured", { status: 500 });
  }
}

