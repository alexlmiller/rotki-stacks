# Frontend Implementation Patterns

Vue.js and TypeScript patterns for Stacks integration.

---

## Script Setup Order

Always follow this exact order:

```typescript
// 1. Imports
import { ref, computed } from 'vue';
import { get, set } from '@vueuse/shared';

// 2. defineX macros
definePage({ name: 'accounts-stacks' });
const props = defineProps<{ id: string }>();
const emit = defineEmits<{ 'update:value': [value: string] }>();

// 3. i18n and router (ALWAYS include useScope)
const { t } = useI18n({ useScope: 'global' });
const router = useRouter();

// 4. Reactive state (ALWAYS explicit types)
const isLoading = ref<boolean>(false);
const data = ref<Data>();

// 5. Pinia stores
const store = useExampleStore();

// 6. Composables
// 7. Computed properties
// 8. Methods
// 9. Watchers
// 10. Lifecycle hooks
```

---

## Account Page

**File**: `frontend/app/src/pages/accounts/stacks/index.vue`

```vue
<script setup lang="ts">
import AccountBalancesDefaultPage from '@/components/accounts/AccountBalancesDefaultPage.vue';

definePage({
  name: 'accounts-stacks',
});

const { t } = useI18n({ useScope: 'global' });
</script>

<template>
  <AccountBalancesDefaultPage
    category="stacks"
    :title="t('navigation_menu.accounts_sub.stacks')"
  />
</template>
```

---

## Chain Enum

**File**: `frontend/common/src/blockchain/index.ts`

```typescript
export enum Blockchain {
  // ... existing
  STACKS = 'stacks',
}
```

---

## Explorer URLs

**File**: `frontend/app/src/types/asset/asset-urls.ts`

```typescript
export const explorerUrls: AssetExplorerUrls = {
  [Blockchain.STACKS]: {
    address: 'https://explorer.hiro.so/address/',
    block: 'https://explorer.hiro.so/block/',
    token: 'https://explorer.hiro.so/token/',
    transaction: 'https://explorer.hiro.so/txid/',
  },
};
```

---

## Chain Type Helper

**File**: `frontend/app/src/composables/info/chains.ts`

```typescript
function isStacksChain(info: ChainInfo): info is ChainInfo {
  return info.type === 'stacks';
}

const stacksChainsData = computed<ChainInfo[]>(() =>
  get(supportedChains).filter(isStacksChain)
);

const isStacksChains = (chain: MaybeRef<string>): boolean => {
  const chains = get(stacksChainsData);
  return chains.some(x => x.id === get(chain));
};
```

---

## Localization

**File**: `frontend/app/src/locales/en.json`

Keys must be **alphabetically ordered**:

```json
{
  "blockchain_balances": {
    "stacks": "Stacks Address"
  },
  "navigation_menu": {
    "accounts_sub": {
      "stacks": "Stacks @:navigation_menu.accounts"
    }
  }
}
```

---

## Styling Rules

1. **Use Tailwind CSS only** - no scoped styles
2. **No CSS modules** except for TransitionGroup animations
3. Migrate legacy styled components when modifying them

```vue
<!-- Correct -->
<template>
  <div class="flex items-center gap-2 p-4">
    ...
  </div>
</template>

<!-- Incorrect - no scoped styles -->
<style scoped>
.container { ... }
</style>
```

---

## Props and Emits

Use generic syntax, not object syntax:

```typescript
// Correct
defineProps<{
  title: string;
  count?: number;
}>();

defineEmits<{
  'update:msg': [msg: string];
  'submit': [data: FormData];
}>();

// Incorrect
defineProps({
  title: String,
  count: Number,
});
```

---

## Refs and Computed

Always use explicit types and VueUse `get()`/`set()`:

```typescript
// Correct
const isVisible = ref<boolean>(true);
const count = ref<number>(0);
const doubled = computed<number>(() => get(count) * 2);

function increment(): void {
  set(count, get(count) + 1);
}

// Incorrect
const isVisible = ref(true);
const count = ref(0);
const doubled = computed(() => count.value * 2);
```

---

## Pinia Store Structure

```typescript
export const useExampleStore = defineStore('example', () => {
  // 1. State
  const items = ref<Item[]>([]);
  const loading = ref<boolean>(false);

  // 2. Getters
  const itemCount = computed<number>(() => get(items).length);

  // 3. Actions
  async function fetchItems(): Promise<void> {
    set(loading, true);
    try {
      const data = await api.getItems();
      set(items, data);
    } finally {
      set(loading, false);
    }
  }

  // 4. Watchers (optional)

  return { items, loading, itemCount, fetchItems };
});
```

---

## Assets

**Logo**: `frontend/app/public/assets/images/protocols/stacks.svg`
- SVG format
- 100x100 viewBox recommended

**Protocol logos** (for decoders):
- `sbtc.svg`
- `stackingdao.svg`
- `hermetica.svg`
