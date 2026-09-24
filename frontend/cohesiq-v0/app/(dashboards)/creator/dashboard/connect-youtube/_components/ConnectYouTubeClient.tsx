"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const errorMessages: Record<string, string> = {
  invalid_state: "The OAuth response could not be verified. Please try again.",
  no_channel: "No YouTube channel was found for this account. Make sure you have a channel.",
  backend_error: "Unable to save your channel. Please try again later.",
  server_error: "Something went wrong while connecting YouTube. Please try again.",
  creator_not_found: "Could not locate your creator profile. Please complete onboarding first.",
  config_missing: "YouTube OAuth is not configured on the server.",
};

export function ConnectYouTubeClient() {
  const { user, isLoaded, isSignedIn } = useUser();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const success = searchParams.get("success");
  const error = searchParams.get("error") || localError;
  const channel = searchParams.get("channel");
  const autoStart = searchParams.get("autoStart") === "true";

  const handleConnectYouTube = useCallback(async () => {
    setIsLoading(true);
    setLocalError(null);
    try {
      const response = await fetch("/api/oauth/youtube/authorize", {
        method: "POST",
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Failed to generate YouTube auth URL.");
      }

      const { authUrl } = await response.json();
      window.location.href = authUrl;
    } catch (err) {
      console.error("Failed to connect YouTube:", err);
      setLocalError("server_error");
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn || !user) {
      router.push("/sign-in");
    }
  }, [isLoaded, isSignedIn, router, user]);

  useEffect(() => {
    if (isLoaded && isSignedIn && autoStart && !success && !error && !isLoading) {
      void handleConnectYouTube();
    }
  }, [autoStart, error, handleConnectYouTube, isLoaded, isLoading, isSignedIn, success]);

  if (!isLoaded || !isSignedIn || !user) {
    return <div className="p-space-8 text-center text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="mx-auto max-w-3xl px-space-4 py-space-12 sm:px-space-6 lg:px-space-8">
      <Card>
        <CardContent className="p-space-8">
          <div className="flex flex-col gap-4 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <RefreshCw className="h-6 w-6" />
            </div>
            <h1 className="font-display text-3xl font-semibold text-foreground">Sync YouTube</h1>
            <p className="max-w-2xl text-muted-foreground">
              Verify your channel ownership with Google OAuth and sync your YouTube creator profile to Cohesiq.
            </p>
          </div>

          {success === "true" && channel ? (
            <div className="mt-space-8 rounded-lg border border-border bg-muted p-space-6 text-center text-foreground">
              <div className="flex items-center justify-center gap-2 text-lg font-medium">
                <CheckCircle2 className="h-5 w-5 text-primary" />
                Connected YouTube channel {channel} successfully.
              </div>
              <p className="mt-space-2 text-sm text-muted-foreground">
                Your channel has been verified and synced with your creator profile.
              </p>
            </div>
          ) : null}

          {error ? (
            <div className="mt-space-8 rounded-lg border border-destructive/30 bg-destructive/10 p-space-6 text-center text-destructive">
              <div className="flex items-center justify-center gap-2 text-lg font-medium">
                <AlertTriangle className="h-5 w-5" />
                {errorMessages[error] || "Unable to connect YouTube. Please try again."}
              </div>
            </div>
          ) : null}

          <div className="mt-space-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Button
              onClick={handleConnectYouTube}
              disabled={isLoading}
              className="w-full sm:w-auto"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Redirecting
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Sync to YouTube
                </>
              )}
            </Button>

            <Link href="/creator/dashboard/profile" className="text-sm font-medium text-primary hover:underline">
              Manage creator profile
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
