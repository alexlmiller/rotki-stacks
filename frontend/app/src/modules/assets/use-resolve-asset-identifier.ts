import { type AssetInfo, getAddressFromEvmIdentifier, getContractFromStacksIdentifier, isEvmIdentifier, isStacksTokenIdentifier } from '@rotki/common';
import { CUSTOM_ASSET } from '@/modules/assets/types';
import { useGeneralSettingsStore } from '@/modules/settings/use-general-settings-store';

export function useResolveAssetIdentifier(): (identifier: string) => string {
  const { treatEth2AsEth } = storeToRefs(useGeneralSettingsStore());

  return (identifier: string): string => {
    if (get(treatEth2AsEth) && identifier === 'ETH2')
      return 'ETH';

    return identifier;
  };
}

function getAssetNameFallback(id: string): string {
  if (isEvmIdentifier(id)) {
    const address = getAddressFromEvmIdentifier(id);
    return `EVM Token: ${address}`;
  }
  if (isStacksTokenIdentifier(id)) {
    const contract = getContractFromStacksIdentifier(id);
    // Truncate long contract IDs for display
    const displayContract = contract.length > 20 ? `${contract.slice(0, 20)}...` : contract;
    return `Stacks Token: ${displayContract}`;
  }
  return '';
}

export function processAssetInfo(
  data: AssetInfo | null,
  id: string,
  collectionData: AssetInfo | null,
): AssetInfo | null {
  if (!data) {
    const fallback = getAssetNameFallback(id);
    if (!fallback) {
      return null;
    }

    return {
      name: fallback,
      symbol: fallback,
    };
  }

  const isCustomAsset = data.isCustomAsset || data.assetType === CUSTOM_ASSET;

  if (isCustomAsset) {
    return {
      ...data,
      isCustomAsset,
      symbol: data.name,
    };
  }

  const fallback = getAssetNameFallback(id);
  const name = collectionData?.name || data.name || fallback;
  const symbol = collectionData?.symbol || data.symbol || fallback;

  return {
    ...data,
    isCustomAsset,
    name,
    symbol,
  };
}
