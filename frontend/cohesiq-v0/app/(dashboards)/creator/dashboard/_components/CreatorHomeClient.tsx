"use client";

import Link from "next/link";
import { useCallback, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { PlatformBadge, getPlatformLabel } from "@/components/shared/PlatformBadge";
import { NicheBadge } from "@/components/shared/NicheBadge";
import { ApplicationStatusBadge } from "@/components/application/ApplicationStatusBadge";
import { getAvatarInitials } from "@/lib/avatar";
import { formatDate, formatFollowerCount, sanitizeImageUrl } from "@/lib/utils";
import type { Application, Campaign, Creator, CreatorPortfolioItem, CreatorSocialProfile, PlatformType } from "@/lib/types";
import {
  ArrowRight,
  BadgeCheck,
  BarChart3,
  Eye,
  FileText,
  Heart,
  ImageIcon,
  MessageCircle,
  Music2,
  RefreshCw,
  Settings,
  Users,
  Youtube,
} from "lucide-react";

interface CreatorHomeClientProps {
  creator: Creator;
  applications: Application[];
  suggestedCampaigns: Campaign[];
}

const PLATFORM_ORDER: PlatformType[] = ["youtube", "instagram", "tiktok", "facebook", "linkedin", "twitter_x", "snapchat", "other"];

function pickPrimaryPlatform(profiles: CreatorSocialProfile[]) {
  return [...profiles].sort((a, b) => {
    if (a.is_primary_platform !== b.is_primary_platform) return a.is_primary_platform ? -1 : 1;
    return PLATFORM_ORDER.indexOf(a.platform) - PLATFORM_ORDER.indexOf(b.platform);
  })[0];
}

function numberOrZero(value: number | undefined) {
  return value ?? 0;
}

function formatMetric(value: number | undefined) {
  return formatFollowerCount(numberOrZero(value));
}

function topContent(items: CreatorPortfolioItem[], platform?: PlatformType) {
  return [...items]
    .filter(item => !platform || item.platform === platform)
    .sort((a, b) => {
      const scoreA = (a.views ?? 0) * 3 + (a.likes ?? 0) + (a.comments ?? 0) * 2;
      const scoreB = (b.views ?? 0) * 3 + (b.likes ?? 0) + (b.comments ?? 0) * 2;
      if (scoreA !== scoreB) return scoreB - scoreA;
      if (a.is_featured !== b.is_featured) return a.is_featured ? -1 : 1;
      return a.sort_order - b.sort_order;
    })
    .slice(0, 5);
}

function contentCover(items: CreatorPortfolioItem[], platform?: PlatformType) {
  return topContent(items, platform).find(item => item.thumbnail_url)?.thumbnail_url;
}

function platformBio(creator: Creator, profile?: CreatorSocialProfile) {
  if (!profile) return creator.bio || creator.tagline || "Connect a platform to build your creator media kit.";
  if (profile.notes) return profile.notes;
  const platformName = getPlatformLabel(profile.platform);
  const handle = profile.display_name_on_platform || `@${profile.handle}`;
  const metrics = profile.follower_count ? `${formatMetric(profile.follower_count)} followers` : "verified profile metrics";
  return `${handle} on ${platformName}, synced with ${metrics}. ${creator.bio || creator.tagline || ""}`.trim();
}

function platformHref(platform: PlatformType) {
  if (platform === "youtube") return "/creator/dashboard/connect-youtube?autoStart=true";
  if (platform === "tiktok") return "/creator/dashboard/connect-tiktok?autoStart=true";
  return "/creator/dashboard/profile";
}

type SyncingPlatform = "youtube" | "tiktok" | null;

export function CreatorHomeClient({ creator, applications, suggestedCampaigns }: CreatorHomeClientProps) {
  const profiles = useMemo(
    () => [...creator.social_profiles].sort((a, b) => PLATFORM_ORDER.indexOf(a.platform) - PLATFORM_ORDER.indexOf(b.platform)),
    [creator.social_profiles],
  );
  const primary = pickPrimaryPlatform(profiles);
  const [selectedPlatform, setSelectedPlatform] = useState<PlatformType | undefined>(primary?.platform);
  const [bioMode, setBioMode] = useState<"profile" | "platform">("profile");
  const [syncing, setSyncing] = useState<SyncingPlatform>(null);
  const [syncError, setSyncError] = useState<string | null>(null);

  const handleSyncYouTube = useCallback(async () => {
    setSyncing("youtube");
    setSyncError(null);
    try {
      const response = await fetch("/api/oauth/youtube/authorize", { method: "POST" });
      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Failed to generate YouTube auth URL.");
      }
      const { authUrl } = await response.json();
      window.location.href = authUrl;
    } catch (err) {
      console.error("Failed to connect YouTube:", err);
      setSyncError("Could not start YouTube sync. Please try again.");
      setSyncing(null);
    }
  }, []);

  const handleSyncTikTok = useCallback(() => {
    setSyncing("tiktok");
    window.location.href = "/creator/dashboard/connect-tiktok?autoStart=true";
  }, []);

  const selectedProfile = profiles.find(profile => profile.platform === selectedPlatform) ?? primary;
  const selectedContent = topContent(creator.portfolio_items, selectedProfile?.platform);
  const allTopContent = topContent(creator.portfolio_items);
  const coverImage = sanitizeImageUrl(
    contentCover(creator.portfolio_items, selectedProfile?.platform)
    || contentCover(creator.portfolio_items)
    || creator.profile_photo_url,
  );
  const displayBio = bioMode === "platform" ? platformBio(creator, selectedProfile) : (creator.bio || platformBio(creator, selectedProfile));
  const pendingApps = applications.filter(app => app.status === "pending" || app.status === "shortlisted").length;
  const connectedCount = profiles.length;
  const totalReach = profiles.reduce((sum, profile) => sum + numberOrZero(profile.follower_count), 0);
  const avgEngagement = profiles.length
    ? profiles.reduce((sum, profile) => sum + numberOrZero(profile.engagement_rate), 0) / profiles.length
    : 0;

  return (
    <div className="bd-page">
      <header
        className="bd-header"
        style={coverImage ? { backgroundImage: `linear-gradient(to right, color-mix(in oklab, var(--color-surface) 90%, transparent), color-mix(in oklab, var(--color-surface) 52%, transparent)), url(${coverImage})`, backgroundSize: "cover", backgroundPosition: "center" } : undefined}
      >
        <div className="bd-header-inner">
          <div className="flex max-w-3xl items-end gap-5">
            <Avatar className="h-20 w-20 border-4 border-background shadow-md">
              <AvatarImage src={sanitizeImageUrl(creator.profile_photo_url)} alt={creator.display_name} />
              <AvatarFallback className="text-xl font-bold">{getAvatarInitials(creator.display_name)}</AvatarFallback>
            </Avatar>
            <div>
              <span className="eyebrow mb-3 block">Creator Home</span>
              <h1 className="bd-header-title">{creator.display_name}</h1>
              <p className="bd-header-sub max-w-2xl">{displayBio}</p>
              <div className="mt-4 flex flex-wrap items-center gap-2">
                <NicheBadge niche={creator.primary_niche} size="sm" />
                {selectedProfile?.is_api_verified && (
                  <span className="bd-status bd-status-active">
                    <BadgeCheck className="h-3.5 w-3.5" />
                    API verified
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="bd-header-actions">
            <Button variant="outline" asChild>
              <Link href="/creator/dashboard/profile">
                <Settings className="mr-2 h-4 w-4" />
                Manage Profile
              </Link>
            </Button>
            <Button asChild>
              <Link href={platformHref(selectedProfile?.platform || "youtube")}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Sync Platform
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <div className="bd-body">
        <div className="bd-stats">
          <div className="bd-stat">
            <div className="bd-stat-icon"><Users className="h-5 w-5" /></div>
            <div className="bd-stat-num">{formatMetric(totalReach)}</div>
            <div className="bd-stat-label">Total Reach</div>
            <div className="bd-stat-sub">across {connectedCount} connected platform{connectedCount === 1 ? "" : "s"}</div>
          </div>
          <div className="bd-stat">
            <div className="bd-stat-icon warm"><BarChart3 className="h-5 w-5" /></div>
            <div className="bd-stat-num">{avgEngagement ? `${avgEngagement.toFixed(1)}%` : "-"}</div>
            <div className="bd-stat-label">Avg Engagement</div>
            <div className="bd-stat-sub">from stored synced metrics</div>
          </div>
          <div className="bd-stat">
            <div className="bd-stat-icon"><FileText className="h-5 w-5" /></div>
            <div className="bd-stat-num">{applications.length}</div>
            <div className="bd-stat-label">Applications</div>
            <div className="bd-stat-sub">{pendingApps} waiting or shortlisted</div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="bd-section">
            <div className="bd-section-head">
              <span className="bd-section-title">Platform Analytics</span>
              <div className="flex flex-wrap gap-2">
                {profiles.length === 0 ? (
                  <Button size="sm" asChild><Link href="/creator/dashboard/profile">Add platform</Link></Button>
                ) : profiles.map(profile => (
                  <button
                    key={profile.id}
                    type="button"
                    onClick={() => setSelectedPlatform(profile.platform)}
                    className={`bd-status ${selectedProfile?.platform === profile.platform ? "bd-status-active" : "bd-status-draft"}`}
                  >
                    <PlatformBadge platform={profile.platform} />
                    {getPlatformLabel(profile.platform)}
                  </button>
                ))}
              </div>
            </div>
            <div className="bd-section-body space-y-6">
              {selectedProfile ? (
                <>
                  <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <Metric label={selectedProfile.platform === "youtube" ? "Subscribers" : "Followers"} value={formatMetric(selectedProfile.follower_count)} />
                    <Metric label="Avg Views" value={formatMetric(selectedProfile.avg_views_per_post)} />
                    <Metric label="Avg Likes" value={formatMetric(selectedProfile.avg_likes_per_post)} />
                    <Metric label="Engagement" value={selectedProfile.engagement_rate ? `${selectedProfile.engagement_rate}%` : "-"} />
                  </div>
                  <div className="rounded-lg border border-border bg-muted/20 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-foreground">@{selectedProfile.handle}</p>
                        <p className="text-xs text-muted-foreground">
                          Last synced {selectedProfile.stats_reported_at ? formatDate(selectedProfile.stats_reported_at) : "manually"} · {selectedProfile.stats_reported_for_period || "stored profile metrics"}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {(selectedProfile.platform === "youtube" || !selectedProfile) && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={handleSyncYouTube}
                            disabled={syncing !== null}
                          >
                            <RefreshCw className={`mr-2 h-3.5 w-3.5${syncing === "youtube" ? " animate-spin" : ""}`} />
                            {syncing === "youtube" ? "Syncing…" : "Re-sync YouTube"}
                          </Button>
                        )}
                        <Button variant="outline" size="sm" asChild>
                          <Link href={selectedProfile.profile_url} target="_blank">
                            Open profile <ArrowRight className="ml-2 h-3.5 w-3.5" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  {/* ── Sync CTA when no platform is connected ─── */}
                  <div className="rounded-xl border border-border bg-muted/20 p-6 space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Verify your channel with OAuth for an instant, trusted sync — or add a platform manually from your profile. Verified handles boost your authenticity score and match rank.
                    </p>
                    {syncError && (
                      <p className="text-sm font-medium text-destructive">{syncError}</p>
                    )}
                    <div className="space-y-3">
                      <div className="flex items-center gap-4 rounded-lg border border-border bg-background p-4">
                        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-500/10 text-red-500">
                          <Youtube className="h-5 w-5" />
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-foreground">Verify with YouTube</p>
                          <p className="text-xs text-muted-foreground">Sync your channel &amp; subscriber count directly from Google.</p>
                        </div>
                        <Button
                          size="sm"
                          onClick={handleSyncYouTube}
                          disabled={syncing !== null}
                        >
                          <RefreshCw className={`mr-2 h-3.5 w-3.5${syncing === "youtube" ? " animate-spin" : ""}`} />
                          {syncing === "youtube" ? "Syncing…" : "Sync YouTube"}
                        </Button>
                      </div>
                      <div className="flex items-center gap-4 rounded-lg border border-border bg-background p-4">
                        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-black/10 text-foreground dark:bg-white/10">
                          <Music2 className="h-5 w-5" />
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-foreground">Verify with TikTok</p>
                          <p className="text-xs text-muted-foreground">Sync your TikTok profile from your authorized account.</p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleSyncTikTok}
                          disabled={syncing !== null}
                        >
                          <RefreshCw className={`mr-2 h-3.5 w-3.5${syncing === "tiktok" ? " animate-spin" : ""}`} />
                          {syncing === "tiktok" ? "Redirecting…" : "Sync TikTok"}
                        </Button>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="h-px flex-1 bg-border" />
                      <span className="text-xs text-muted-foreground">or add manually</span>
                      <div className="h-px flex-1 bg-border" />
                    </div>
                    <Button variant="ghost" size="sm" className="w-full" asChild>
                      <Link href="/creator/dashboard/profile">Manage platforms manually</Link>
                    </Button>
                  </div>
                </>
              )}
            </div>
          </section>

          <section className="bd-section">
            <div className="bd-section-head">
              <span className="bd-section-title">Bio Source</span>
            </div>
            <div className="bd-section-body space-y-4">
              <div className="grid grid-cols-2 gap-2">
                <Button type="button" variant={bioMode === "profile" ? "default" : "outline"} onClick={() => setBioMode("profile")}>Profile Bio</Button>
                <Button type="button" variant={bioMode === "platform" ? "default" : "outline"} onClick={() => setBioMode("platform")}>Platform Bio</Button>
              </div>
              <p className="text-sm leading-6 text-muted-foreground">{displayBio}</p>
              <Button variant="outline" className="w-full" asChild>
                <Link href="/creator/dashboard/profile">Edit saved profile</Link>
              </Button>
            </div>
          </section>
        </div>

        <section className="bd-section">
          <div className="bd-section-head">
            <span className="bd-section-title">Top Content</span>
            <span className="text-xs text-muted-foreground">
              {selectedContent.length ? `Showing ${selectedContent.length} stored ${selectedProfile ? getPlatformLabel(selectedProfile.platform) : ""} item${selectedContent.length === 1 ? "" : "s"}` : `${allTopContent.length} stored items`}
            </span>
          </div>
          <div className="bd-section-body">
            {(selectedContent.length ? selectedContent : allTopContent).length === 0 ? (
              <EmptyPanel title="No content stored yet" description="Sync YouTube or TikTok to import recent posts into your media kit." />
            ) : (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
                {(selectedContent.length ? selectedContent : allTopContent).map(item => (
                  <TopContentCard key={item.id ?? item.content_url} item={item} />
                ))}
              </div>
            )}
          </div>
        </section>

        <div className="grid gap-8 lg:grid-cols-2">
          <section className="bd-section">
            <div className="bd-section-head">
              <span className="bd-section-title">Recent Applications</span>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/creator/dashboard/collaborations">View all <ArrowRight className="ml-1 h-3.5 w-3.5" /></Link>
              </Button>
            </div>
            <div className="bd-section-body">
              {applications.length === 0 ? (
                <EmptyPanel title="No applications yet" description="Discover campaigns and apply when the fit is right." />
              ) : applications.slice(0, 4).map(app => (
                <div key={app.id} className="bd-campaign-row">
                  <div>
                    <p className="text-sm font-semibold text-foreground">{app.campaign?.title || "Campaign"}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{app.campaign?.brand?.brand_name || "Brand"} · {formatDate(app.applied_at)}</p>
                  </div>
                  <ApplicationStatusBadge status={app.status} />
                </div>
              ))}
            </div>
          </section>

          <section className="bd-section">
            <div className="bd-section-head">
              <span className="bd-section-title">Suggested Campaigns</span>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/creator/dashboard/campaigns">Browse <ArrowRight className="ml-1 h-3.5 w-3.5" /></Link>
              </Button>
            </div>
            <div className="bd-section-body">
              {suggestedCampaigns.length === 0 ? (
                <EmptyPanel title="No suggestions yet" description="Campaign suggestions appear when active campaigns match your niche." />
              ) : suggestedCampaigns.slice(0, 4).map(campaign => (
                <div key={campaign.id} className="bd-campaign-row">
                  <div>
                    <p className="text-sm font-semibold text-foreground">{campaign.title}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground capitalize">{campaign.primary_niche}</p>
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/creator/dashboard/campaigns/${campaign.id}`}>View</Link>
                  </Button>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-muted/20 p-4">
      <p className="text-xs font-medium uppercase text-muted-foreground">{label}</p>
      <p className="mt-2 font-display text-2xl font-bold text-foreground">{value}</p>
    </div>
  );
}

function EmptyPanel({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex min-h-36 flex-col items-center justify-center rounded-lg border border-dashed border-border p-6 text-center">
      <ImageIcon className="mb-3 h-8 w-8 text-muted-foreground" />
      <p className="text-sm font-semibold text-foreground">{title}</p>
      <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p>
    </div>
  );
}

function TopContentCard({ item }: { item: CreatorPortfolioItem }) {
  const thumbnailUrl = sanitizeImageUrl(item.thumbnail_url);

  return (
    <Link href={item.content_url} target="_blank" className="group overflow-hidden rounded-lg border border-border bg-background transition-colors hover:border-primary/50">
      <div className="aspect-video bg-muted">
        {thumbnailUrl ? (
          <img src={thumbnailUrl} alt={item.title || "Creator content"} className="h-full w-full object-cover transition-transform group-hover:scale-[1.03]" />
        ) : (
          <div className="flex h-full items-center justify-center">
            <ImageIcon className="h-8 w-8 text-muted-foreground" />
          </div>
        )}
      </div>
      <div className="space-y-3 p-3">
        <div className="flex items-center justify-between gap-2">
          <PlatformBadge platform={item.platform} showLabel size="sm" />
          {item.published_at && <span className="text-[11px] text-muted-foreground">{formatDate(item.published_at)}</span>}
        </div>
        <p className="line-clamp-2 min-h-10 text-sm font-semibold text-foreground">{item.title || "Untitled content"}</p>
        <div className="grid grid-cols-3 gap-2 text-[11px] text-muted-foreground">
          <span className="flex items-center gap-1"><Eye className="h-3 w-3" />{formatMetric(item.views)}</span>
          <span className="flex items-center gap-1"><Heart className="h-3 w-3" />{formatMetric(item.likes)}</span>
          <span className="flex items-center gap-1"><MessageCircle className="h-3 w-3" />{formatMetric(item.comments)}</span>
        </div>
      </div>
    </Link>
  );
}
