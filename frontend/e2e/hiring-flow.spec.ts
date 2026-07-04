import { test, expect } from "@playwright/test";
import {
  applyToListing,
  createListing,
  registerUser,
  simulateKyc,
} from "./helpers/api";

const API = process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000/api";
const ts = Date.now();

async function seedWallet(access: string, amount = "10000.00") {
  const res = await fetch(`${API}/v3/global/payments/wallet/seed/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${access}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ amount }),
  });
  if (!res.ok) throw new Error(`Seed wallet failed: ${await res.text()}`);
}

test.describe("Hiring flow: register → verify → job → apply → escrow → release", () => {
  test("full marketplace trust loop", async ({ page }) => {
    const employerEmail = `employer-${ts}@e2e.test`;
    const talentEmail = `talent-${ts}@e2e.test`;
    const employerHandle = `employer${ts}`;
    const talentHandle = `talent${ts}`;
    const jobTitle = `E2E Job ${ts}`;

    // --- Register employer via UI ---
    await page.goto("/auth/register");
    await page.getByLabel(/email/i).fill(employerEmail);
    await page.getByLabel(/password/i).fill("E2Epass123!");
    await page.getByLabel(/handle/i).fill(employerHandle);
    await page.getByRole("radio", { name: /employer/i }).check();
    await page.getByRole("button", { name: /create account/i }).click();
    await page.waitForURL(/dashboard/, { timeout: 30_000 });

    const employerLogin = await fetch(`${API}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: employerEmail, password: "E2Epass123!" }),
    });
    const { access: employerToken } = await employerLogin.json();
    await simulateKyc(employerToken);
    await seedWallet(employerToken);

    // --- Register & verify talent via API ---
    const talentSession = await registerUser({
      email: talentEmail,
      password: "E2Epass123!",
      handle: talentHandle,
      role: "talent",
    });
    await simulateKyc(talentSession.access);

    const talentMe = await (
      await fetch(`${API}/auth/me/`, {
        headers: { Authorization: `Bearer ${talentSession.access}` },
      })
    ).json();

    // Post job & apply
    const listing = await createListing(employerToken, jobTitle);
    await applyToListing(talentSession.access, listing.id);

    // Escrow create → fund → dual sign-off → release
    const escrowCreate = await fetch(`${API}/v3/global/payments/escrow/create/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${employerToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ listing_id: listing.id, talent_id: talentMe.id }),
    });
    expect(escrowCreate.ok).toBeTruthy();
    const { escrow } = await escrowCreate.json();

    const fundRes = await fetch(`${API}/v3/global/payments/escrow/fund/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${employerToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ escrow_id: escrow.id, use_wallet: true }),
    });
    expect(fundRes.ok).toBeTruthy();

    for (const token of [employerToken, talentSession.access]) {
      const signRes = await fetch(`${API}/v3/global/payments/release-escrow/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ escrow_id: escrow.id }),
      });
      expect(signRes.ok).toBeTruthy();
    }

    const final = await (
      await fetch(`${API}/v3/global/payments/release-escrow/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${employerToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ escrow_id: escrow.id }),
      })
    ).json();
    expect(final.released).toBe(true);

    // --- Talent wallet UI ---
    await page.goto("/auth/login");
    await page.getByLabel(/email/i).fill(talentEmail);
    await page.getByLabel(/password/i).fill("E2Epass123!");
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL(/dashboard/, { timeout: 30_000 });

    await page.goto("/dashboard/wallet");
    await expect(page.getByText(/available balance/i)).toBeVisible({ timeout: 15_000 });

    // --- Proof-of-work on public profile ---
    await page.goto(`/profile/${talentHandle}`);
    await expect(page.getByText(jobTitle)).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("button", { name: /verify/i }).first()).toBeVisible();
  });
});
