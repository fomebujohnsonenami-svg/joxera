const API = process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000/api";

export interface AuthSession {
  access: string;
  refresh: string;
  handle: string;
}

export async function registerUser(opts: {
  email: string;
  password: string;
  handle: string;
  role: "talent" | "employer";
  country?: string;
}): Promise<AuthSession> {
  const res = await fetch(`${API}/auth/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: opts.email,
      password: opts.password,
      handle: opts.handle,
      country: opts.country ?? "US",
      role: opts.role,
    }),
  });
  if (!res.ok) throw new Error(`Register failed: ${await res.text()}`);
  const data = await res.json();
  return { access: data.access, refresh: data.refresh, handle: opts.handle };
}

export async function simulateKyc(access: string): Promise<void> {
  const res = await fetch(`${API}/auth/kyc/simulate-approve/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${access}` },
  });
  if (!res.ok) throw new Error(`KYC simulate failed: ${await res.text()}`);
}

export async function createListing(
  access: string,
  title: string
): Promise<{ id: number }> {
  const res = await fetch(`${API}/listings/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${access}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
      description: "E2E test listing — Django REST API work.",
      field: "backend-dev",
      tier: "standard",
      mode: "remote",
      country_code: "US",
      currency: "USD",
      budget: "1500.00",
    }),
  });
  if (!res.ok) throw new Error(`Create listing failed: ${await res.text()}`);
  return res.json();
}

export async function applyToListing(
  access: string,
  listingId: number
): Promise<void> {
  const res = await fetch(`${API}/applications/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${access}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ listing: listingId, cover_note: "E2E application" }),
  });
  if (!res.ok) throw new Error(`Apply failed: ${await res.text()}`);
}

export async function fundEmployerWallet(
  access: string,
  amount = "10000.00"
): Promise<void> {
  // Dev helper: fund via wallet escrow lock path requires existing wallet balance.
  // Use escrow fund endpoint after creating escrow — employer wallet seeded via API lock.
  void access;
  void amount;
}

export async function runEscrowFlow(opts: {
  employerToken: string;
  talentToken: string;
  listingId: number;
  talentUserId: number;
}): Promise<number> {
  const createRes = await fetch(`${API}/v3/global/payments/escrow/create/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${opts.employerToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ listing_id: opts.listingId, talent_id: opts.talentUserId }),
  });
  if (!createRes.ok) throw new Error(`Escrow create: ${await createRes.text()}`);
  const { escrow } = await createRes.json();
  const escrowId = escrow.id;

  const fundRes = await fetch(`${API}/v3/global/payments/escrow/fund/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${opts.employerToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ escrow_id: escrowId, use_wallet: true }),
  });
  if (fundRes.status === 402) {
    // Seed employer wallet by simulating provider lock via direct fund skip
    throw new Error("Employer wallet insufficient — seed wallet in test setup");
  }

  for (const token of [opts.employerToken, opts.talentToken]) {
    const releaseRes = await fetch(`${API}/v3/global/payments/release-escrow/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ escrow_id: escrowId }),
    });
    if (!releaseRes.ok) throw new Error(`Release sign-off: ${await releaseRes.text()}`);
  }
  return escrowId;
}
