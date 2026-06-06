<script setup lang="ts">
import AccountBalancesDefaultPage from '@/modules/accounts/AccountBalancesDefaultPage.vue';
import { NoteLocation } from '@/modules/core/common/notes';

definePage({
  meta: {
    noteLocation: NoteLocation.ACCOUNTS_STACKS,
  },
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
