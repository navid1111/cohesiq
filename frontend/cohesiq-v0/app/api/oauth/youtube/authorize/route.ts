import { auth } from "@clerk/nextjs/server";
import { randomUUID } from "crypto";
import { NextResponse } from "next/server";
import {
  buildYouTubeAuthUrl,
  getYouTubeOAuthConfig,
  YouTubeOAuthConfigError,
} from "../_lib/oauth";

export async function POST() {
  const { userId } = await auth();
  if (!userId) {
    return new NextResponse("Unauthorized", { status: 401 });
  }

  let authUrl: string;
  try {
    const state = randomUUID();
    authUrl = buildYouTubeAuthUrl(getYouTubeOAuthConfig(), state);

    const response = NextResponse.json({ authUrl });
    response.cookies.set("youtube_oauth_state", state, {
      path: "/",
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      maxAge: 600,
    });
    return response;
  } catch (error) {
    if (error instanceof YouTubeOAuthConfigError) {
      return new NextResponse(error.message, { status: 500 });
    }

    return new NextResponse("YouTube OAuth is not configured", { status: 500 });
  }
}
