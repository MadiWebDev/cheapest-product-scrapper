// Feature flags. Barcode/snap-to-search need camera entitlements and a
// device runtime to verify; they ship DISABLED (honest stub) until a
// device-verified build enables them.
export const FEATURE_BARCODE_SCAN = false;
export const FEATURE_SNAP_SEARCH = false;

export function assertFeatureEnabled(name: string, enabled: boolean): void {
  if (!enabled) throw new Error(`Feature ${name} is disabled in this build`);
}
