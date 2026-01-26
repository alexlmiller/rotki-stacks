"""Stacks blockchain constants and configuration."""

from typing import TYPE_CHECKING, Final, NamedTuple

from rotkehlchen.fval import FVal
from rotkehlchen.history.events.structures.types import HistoryEventType

if TYPE_CHECKING:
    from rotkehlchen.chain.decoding.types import CounterpartyDetails

# Hiro API configuration
HIRO_API_BASE_URL: Final = 'https://api.mainnet.hiro.so'

# Retry/backoff configuration for rate limiting
INITIAL_BACKOFF: Final = 4  # seconds
BACKOFF_MULTIPLIER: Final = 2
MAX_RETRIES: Final = 3

# STX token configuration
STX_DECIMALS: Final = 6


class StacksTokenMetadata(NamedTuple):
    """Metadata for well-known Stacks tokens."""

    name: str
    symbol: str
    decimals: int
    coingecko: str | None = None
    cryptocompare: str | None = None
    protocol: str | None = None


# Curated metadata for well-known Stacks tokens
# Key is the contract ID without ::asset-name suffix
CURATED_STACKS_TOKENS: Final[dict[str, StacksTokenMetadata]] = {
    # sBTC - Bitcoin-backed token on Stacks (mainnet)
    'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token': StacksTokenMetadata(
        name='sBTC',
        symbol='sBTC',
        decimals=8,  # Same as BTC
        coingecko='sbtc-2',
        protocol='sbtc',
    ),
    # sBTC (legacy/testnet contract)
    'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token': StacksTokenMetadata(
        name='sBTC',
        symbol='sBTC',
        decimals=8,  # Same as BTC
        coingecko='sbtc-2',
        protocol='sbtc',
    ),
    # stSTX - StackingDAO liquid staking token (mainnet)
    'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststx-token': StacksTokenMetadata(
        name='Stacked STX',
        symbol='stSTX',
        decimals=6,  # Same as STX
        coingecko='stacking-dao',
        protocol='stackingdao',
    ),
    # stSTXBTC - StackingDAO liquid staking token with BTC yield (v1 - legacy)
    'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststxbtc-token': StacksTokenMetadata(
        name='Stacked STX BTC (v1)',
        symbol='stSTXBTC',
        decimals=6,  # Same as STX
        coingecko='stacking-dao-stacked-stacks-btc',
        protocol='stackingdao',
    ),
    # stSTXBTC - StackingDAO liquid staking token with BTC yield (v2 - current)
    'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststxbtc-token-v2': StacksTokenMetadata(
        name='Stacked STX BTC',
        symbol='stSTXBTC',
        decimals=6,  # Same as STX
        coingecko='stacking-dao-stacked-stacks-btc',
        protocol='stackingdao',
    ),
    # zstSTX - Zest Protocol stSTX supply token
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.zststx-token': StacksTokenMetadata(
        name='Zest stSTX',
        symbol='zstSTX',
        decimals=6,
        coingecko=None,
        protocol='zest',
    ),
    # zstSTXBTC - Zest Protocol stSTXBTC supply token
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.zststxbtc-v2-token': StacksTokenMetadata(
        name='Zest stSTXBTC',
        symbol='zstSTXBTC',
        decimals=6,
        coingecko=None,
        protocol='zest',
    ),
    # zsBTC - Zest Protocol sBTC supply token
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.zsbtc-token': StacksTokenMetadata(
        name='Zest sBTC',
        symbol='zsBTC',
        decimals=8,  # Same as sBTC
        coingecko=None,
        protocol='zest',
    ),
    # aeUSDC - Allbridge bridged USDC
    'SP3Y2ZSH8P7D50B0VBTSX11S7XSG24M1VB9YFQA4K.token-aeusdc': StacksTokenMetadata(
        name='Allbridge USDC',
        symbol='aeUSDC',
        decimals=6,
        coingecko='allbridge-bridged-usdc-stacks',
        protocol='allbridge',
    ),
    # USDCx - Circle bridged USDC via xReserve
    'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx': StacksTokenMetadata(
        name='USDCx',
        symbol='USDCx',
        decimals=6,
        coingecko='usdcx-stacks',
        protocol='circle',
    ),
    # ALEX - ALEX Lab governance token
    'SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-alex': StacksTokenMetadata(
        name='ALEX',
        symbol='ALEX',
        decimals=8,
        coingecko='alexgo',
        protocol='alex',
    ),
    # VELAR - Velar DEX token
    'SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.velar-token': StacksTokenMetadata(
        name='Velar',
        symbol='VELAR',
        decimals=6,
        coingecko='velar',
        protocol='velar',
    ),
    # USDA - Arkadiko stablecoin
    'SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.usda-token': StacksTokenMetadata(
        name='USDA',
        symbol='USDA',
        decimals=6,
        coingecko='arkadiko-usda',
        protocol='arkadiko',
    ),
    # xBTC - Wrapped Bitcoin on Stacks (legacy)
    'SP3DX3H4FEYZJZ586MFBS25ZW3HZDMEW92260R2PR.Wrapped-Bitcoin': StacksTokenMetadata(
        name='Wrapped Bitcoin',
        symbol='xBTC',
        decimals=8,
        coingecko='wrapped-bitcoin-stacks',
        protocol=None,
    ),
    # =====================================
    # Tier 1: DeFi Protocol Tokens
    # =====================================
    # Hermetica USDh - USD stablecoin on Stacks
    'SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1': StacksTokenMetadata(
        name='USDh',
        symbol='USDh',
        decimals=8,
        coingecko='hermetica-usdh',
        protocol='hermetica',
    ),
    # Arkadiko DIKO - Governance token
    'SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-token': StacksTokenMetadata(
        name='Arkadiko',
        symbol='DIKO',
        decimals=6,
        coingecko='arkadiko-protocol',
        protocol='arkadiko',
    ),
    # Wrapped STX (Velar) - For DeFi
    'SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.wstx': StacksTokenMetadata(
        name='Wrapped STX',
        symbol='WSTX',
        decimals=6,
        coingecko='wrapped-stx-velar',
        protocol='velar',
    ),
    # =====================================
    # Tier 2: Bridge Tokens
    # =====================================
    # ALEX sUSDT - Bridged USDT
    'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.token-susdt': StacksTokenMetadata(
        name='sUSDT',
        symbol='sUSDT',
        decimals=8,
        coingecko='alex-wrapped-usdt',
        protocol='alex',
    ),
    # XLink aBTC - Bridged BTC
    'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.token-abtc': StacksTokenMetadata(
        name='aBTC',
        symbol='aBTC',
        decimals=8,
        coingecko='xlink-bridged-btc-stacks',
        protocol='xlink',
    ),
    # LunarCrush on Stacks
    'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.token-slunr': StacksTokenMetadata(
        name='LunarCrush',
        symbol='sLUNR',
        decimals=8,
        coingecko='lunr-token',
        protocol='alex',
    ),
    # =====================================
    # Tier 3: Community/Meme Tokens
    # =====================================
    # Welsh Corgi Coin - Meme token
    'SP3NE50GEXFG9SZGTT51P40X2CKYSZ5CC4ZTZ7A2G.welshcorgicoin-token': StacksTokenMetadata(
        name='Welshcorgicoin',
        symbol='WELSH',
        decimals=6,
        coingecko='welsh-corgi-coin',
        protocol=None,
    ),
    # LEO - Leopold meme token
    'SP1AY6K3PQV5MRT6R4S671NWW2FRVPKM0BR162CT6.leo-token': StacksTokenMetadata(
        name='LEO',
        symbol='LEO',
        decimals=6,
        coingecko='leopold',
        protocol=None,
    ),
    # SatoshAI
    'SP3M31QFF6S96215K4Y2Z9K5SGHJN384NV6YM6VM8.satoshai': StacksTokenMetadata(
        name='SatoshAI',
        symbol='SAI',
        decimals=6,
        coingecko='satoshai',
        protocol=None,
    ),
    # Nothing - Meme token (0 decimals)
    'SP32AEEF6WW5Y0NMJ1S8SBSZDAY8R5J32NBZFPKKZ.nope': StacksTokenMetadata(
        name='Nothing',
        symbol='NOT',
        decimals=0,
        coingecko='nothing-3',
        protocol=None,
    ),
    # GUS - Meme token
    'SP1JFFSYTSH7VBM54K29ZFS9H4SVB67EA8VT2MYJ9.gus-token': StacksTokenMetadata(
        name='GUS',
        symbol='GUS',
        decimals=6,
        coingecko='gus',
        protocol=None,
    ),
    # Flat Earth
    'SP3W69VDG9VTZNG7NTW1QNCC1W45SNY98W1JSZBJH.flat-earth-stxcity': StacksTokenMetadata(
        name='Flat Earth',
        symbol='FLAT',
        decimals=6,
        coingecko='flat-earth',
        protocol=None,
    ),
    # Skullcoin
    'SP3BRXZ9Y7P5YP28PSR8YJT39RT51ZZBSECTCADGR.skullcoin-stxcity': StacksTokenMetadata(
        name='Skullcoin',
        symbol='SKULL',
        decimals=6,
        coingecko='skullcoin',
        protocol=None,
    ),
    # WEN
    'SP25K3XPVBNWXPMYDXBPSZHGC8APW0Z21CWJ3Y3B1.wen-nakamoto-stxcity': StacksTokenMetadata(
        name='WEN',
        symbol='WEN',
        decimals=6,
        coingecko='wen-5',
        protocol=None,
    ),
    # Kangaroo
    'SP2C1WREHGM75C7TGFAEJPFKTFTEGZKF6DFT6E2GE.kangaroo': StacksTokenMetadata(
        name='Kangaroo',
        symbol='$ROO',
        decimals=6,
        coingecko='kangaroo-the-jumping-co-in',
        protocol=None,
    ),
    # Droid
    'SP2EEV5QBZA454MSMW9W3WJNRXVJF36VPV17FFKYH.DROID': StacksTokenMetadata(
        name='Droid',
        symbol='DROID',
        decimals=6,
        coingecko='droid',
        protocol=None,
    ),
    # NotaStrategy (7 decimals)
    'SP2TT71CXBRDDYP2P8XMVKRFYKRGSMBWCZ6W6FDGT.notastrategy': StacksTokenMetadata(
        name='NotaStrategy',
        symbol='NASTY',
        decimals=7,
        coingecko='notastrategy',
        protocol=None,
    ),
    # Blocks
    'SPV9K21TBFAK4KNRJXF5DFP8N7W46G4V9RCJDC22.b-faktory': StacksTokenMetadata(
        name='Blocks',
        symbol='B',
        decimals=6,
        coingecko='blocks-2',
        protocol=None,
    ),
    # =====================================
    # Hermetica Staking Tokens
    # =====================================
    # sUSDh - Staked USDh (Hermetica)
    'SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.susdh-token-v1': StacksTokenMetadata(
        name='Staked USDh',
        symbol='sUSDh',
        decimals=8,
        coingecko=None,
        protocol='hermetica',
    ),
    # =====================================
    # Zest Protocol Tokens
    # =====================================
    # zUSDh - Zest Protocol USDh supply token
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.zusdh-token': StacksTokenMetadata(
        name='Zest USDh',
        symbol='zUSDh',
        decimals=8,
        coingecko=None,
        protocol='zest',
    ),
    # =====================================
    # Bitflow LP Tokens
    # =====================================
    # Bitflow aeUSDC-USDh Stableswap LP
    'SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-pool-aeusdc-usdh-v-1-2':
        StacksTokenMetadata(
            name='Bitflow aeUSDC-USDh LP',
            symbol='BF-aeUSDC-USDh',
            decimals=6,
            coingecko=None,
            protocol='bitflow',
        ),
    # Bitflow sBTC-pBTC Stableswap LP
    'SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-pool-sbtc-pbtc-v-1-1':
        StacksTokenMetadata(
            name='Bitflow sBTC-pBTC LP',
            symbol='BF-sBTC-pBTC',
            decimals=8,
            coingecko=None,
            protocol='bitflow',
        ),
    # Bitflow STX-aeUSDC XYK LP
    'SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-pool-stx-aeusdc-v-1-2': StacksTokenMetadata(
        name='Bitflow STX-aeUSDC LP',
        symbol='BF-STX-aeUSDC',
        decimals=6,
        coingecko=None,
        protocol='bitflow',
    ),
    # =====================================
    # Bridge Tokens
    # =====================================
    # Pontis pBTC - Bridged BTC
    'SP14NS8MVBRHXMM96BQY0727AJ59SWPV7RMHC0NCG.pontis-bridge-pBTC': StacksTokenMetadata(
        name='Pontis BTC',
        symbol='pBTC',
        decimals=8,
        coingecko=None,
        protocol='pontis',
    ),
    # =====================================
    # City Coins
    # =====================================
    # MiamiCoin v2
    'SP1H1733V5MZ3SZ9XRW9FKYGEZT0JDGEB8Y634C7R.miamicoin-token-v2': StacksTokenMetadata(
        name='MiamiCoin',
        symbol='MIA',
        decimals=6,
        coingecko='miamicoin',
        protocol='citycoin',
    ),
    # MiamiCoin v1
    'SP6VJ9Z094TQ1NQB4GNHK3VZGZGKABCVY3DRJ5YE.miamicoin-token': StacksTokenMetadata(
        name='MiamiCoin',
        symbol='MIA',
        decimals=6,
        coingecko='miamicoin',
        protocol='citycoin',
    ),
    # NewYorkCityCoin v2
    'SPSCWDV3RKV5ZRN1FQD84YE1NQFEDJ9R1F4DYQ11.newyorkcitycoin-token-v2': StacksTokenMetadata(
        name='NewYorkCityCoin',
        symbol='NYC',
        decimals=6,
        coingecko='newyorkcoin',
        protocol='citycoin',
    ),
    # =====================================
    # Other Protocol Tokens
    # =====================================
    # Bitflow token
    'SP3G437RF2PAM7VT3PJ3FYDCDYRKKBJHABDMGVS6V.bitflow': StacksTokenMetadata(
        name='Bitflow',
        symbol='BITFLOW',
        decimals=6,
        coingecko=None,
        protocol='bitflow',
    ),
    # sBTCDAO - sBTC governance token
    'SP1MR5NKZPJX9CGYPH6YKBHAKK3JM581F1A35JXP6.sbtcdao': StacksTokenMetadata(
        name='sBTC DAO',
        symbol='sBTCDAO',
        decimals=6,
        coingecko=None,
        protocol='sbtc',
    ),
    # =====================================
    # Additional Meme/Community Tokens
    # =====================================
    # Corgi token (distinct from Welsh Corgi)
    'SP2EXJYQG612FXBH0J2800K2HHD3Z9P1J48WW39V6.corgi': StacksTokenMetadata(
        name='Corgi',
        symbol='CORGI',
        decimals=6,
        coingecko=None,
        protocol=None,
    ),
    # PLAY token
    'SP1PW804599BZ46B4A0FYH86ED26XPJA7SFYNK1XS.play': StacksTokenMetadata(
        name='Play',
        symbol='PLAY',
        decimals=6,
        coingecko=None,
        protocol=None,
    ),
    # Moscow City Coin
    'SP2PF4VYW8B62TASG7AKFESQ04CKTWM21X09PY837.moscow-city-coin-stxcity': StacksTokenMetadata(
        name='Moscow City Coin',
        symbol='MOSCOW',
        decimals=6,
        coingecko=None,
        protocol=None,
    ),
    # RALEX - ALEX wrapper/related token
    'SP37WN2BYHKZ90T1ATHTCNG8EFYHS3B49KNGS02ZK.RALEX': StacksTokenMetadata(
        name='RALEX',
        symbol='RALEX',
        decimals=8,
        coingecko=None,
        protocol='alex',
    ),
    # Meme token (stxcity)
    'SP3HNEXSXJK2RYNG5P6YSEE53FREX645JPJJ5FBFA.meme-stxcity': StacksTokenMetadata(
        name='Meme',
        symbol='MEME',
        decimals=6,
        coingecko=None,
        protocol=None,
    ),
    # Trump Meme
    'SP6TNST5EKBSTGKBR0R95AF01HPW5747FYRBHKXT.trump-meme': StacksTokenMetadata(
        name='Trump Meme',
        symbol='TRUMP',
        decimals=6,
        coingecko=None,
        protocol=None,
    ),
    # Teiko token
    'SP1T0VY3DNXRVP6HBM75DFWW0199CR0X15PC1D81B.teiko-token-stxcity': StacksTokenMetadata(
        name='Teiko',
        symbol='TEIKO',
        decimals=6,
        coingecko=None,
        protocol=None,
    ),
    # PixelStacks
    'SP14XEKF7G8Q4WFYBSE77XSDMM67GTVF95R4V680.pixelstacks': StacksTokenMetadata(
        name='PixelStacks',
        symbol='PIXEL',
        decimals=6,
        coingecko=None,
        protocol=None,
    ),
    # Faktory Fun token (bonding curve)
    'SPV9K21TBFAK4KNRJXF5DFP8N7W46G4V9RCJDC22.fakfun-faktory': StacksTokenMetadata(
        name='FakFun',
        symbol='FAKFUN',
        decimals=6,
        coingecko=None,
        protocol='faktory',
    ),
    # Bitflow Tokens (wrapper/utility)
    'SP2YKJXBBS2E6GSN2W4CBM3DJ8K4Q4RB4NYBR3C3Q.bitflow-tokens': StacksTokenMetadata(
        name='Bitflow Tokens',
        symbol='BFT',
        decimals=6,
        coingecko=None,
        protocol='bitflow',
    ),
    # Bonding curve token example
    'SP1KNRNZET8ZC5Q9P6F1FFW8YQH45CKMNY132B36S.ned2gsk-bonding-curve': StacksTokenMetadata(
        name='Ned2GSK',
        symbol='NED2GSK',
        decimals=6,
        coingecko=None,
        protocol='faktory',
    ),
    # TardlexLabs token
    'SP1EJYSM3PDXCFKPY09CM2M13FPS26YVTCAH0R95E.TardlexLabsTokenContract': StacksTokenMetadata(
        name='TardlexLabs',
        symbol='TARDLEX',
        decimals=6,
        coingecko=None,
        protocol=None,
    ),
}


def get_curated_token_metadata(contract_id: str) -> StacksTokenMetadata | None:
    """Get curated metadata for a well-known Stacks token.

    Args:
        contract_id: The contract ID (e.g., SP3K8BC0...sbtc-token)

    Returns:
        StacksTokenMetadata if found, None otherwise
    """
    return CURATED_STACKS_TOKENS.get(contract_id)


def micro_stx_to_stx(micro_stx: int) -> FVal:
    """Convert microSTX (smallest unit) to STX.

    Args:
        micro_stx: Amount in microSTX (1 STX = 1,000,000 microSTX)

    Returns:
        Amount in STX as FVal
    """
    return FVal(micro_stx) / (10**STX_DECIMALS)


# Event types that represent outgoing transfers (used for note directionality)
# Defined here to avoid dependency on EVM-specific constants
OUTGOING_EVENT_TYPES: Final = frozenset({
    HistoryEventType.SPEND,
    HistoryEventType.TRANSFER,
    HistoryEventType.DEPOSIT,
})


def get_all_stacks_counterparties() -> set['CounterpartyDetails']:
    """Get all Stacks protocol counterparties for UI filtering.

    Returns a set of CounterpartyDetails for all supported Stacks protocols.
    This function avoids circular imports by importing at runtime.
    """
    from rotkehlchen.chain.decoding.types import CounterpartyDetails
    return {
        CounterpartyDetails(identifier='alex', label='ALEX', image='alex.svg'),
        CounterpartyDetails(identifier='allbridge', label='Allbridge', image='allbridge.svg'),
        CounterpartyDetails(identifier='arkadiko', label='Arkadiko', image='arkadiko.svg'),
        CounterpartyDetails(identifier='bitflow', label='Bitflow', image='bitflow.svg'),
        CounterpartyDetails(identifier='dual-stacking', label='Dual Stacking', image='stacks.svg'),
        CounterpartyDetails(identifier='hermetica', label='Hermetica', image='hermetica.svg'),
        CounterpartyDetails(identifier='pox', label='Proof of Transfer', image='stacks.svg'),
        CounterpartyDetails(identifier='sbtc', label='sBTC', image='sbtc.png'),
        CounterpartyDetails(identifier='send-many', label='Send Many', image='stacks.svg'),
        CounterpartyDetails(
            identifier='stacking-pools', label='Stacking Pools', image='stacks.svg',
        ),
        CounterpartyDetails(
            identifier='stackingdao', label='StackingDAO', image='stackingdao.svg',
        ),
        CounterpartyDetails(identifier='usdcx', label='USDCx', image='usdc.svg'),
        CounterpartyDetails(identifier='velar', label='Velar', image='velar.svg'),
        CounterpartyDetails(identifier='zest', label='Zest', image='zest.svg'),
    }
