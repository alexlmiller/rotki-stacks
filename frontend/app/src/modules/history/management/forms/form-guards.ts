import type {
  EvmHistoryEvent,
  EvmSwapEvent,
  GroupEditableHistoryEvents,
  HistoryEvent,
  SolanaEvent,
  SolanaSwapEvent,
  StacksEvent,
  SwapEvent,
} from '@/types/history/events/schemas';
import { HistoryEventEntryType } from '@rotki/common';
import { isEvmEvent, isEvmSwapEvent, isSolanaEvent, isSolanaSwapEvent, isStacksEvent } from '@/utils/history/events';

export function isGroupEditableHistoryEvent(event: HistoryEvent): event is GroupEditableHistoryEvents {
  return event.entryType === HistoryEventEntryType.ASSET_MOVEMENT_EVENT
    || event.entryType === HistoryEventEntryType.SWAP_EVENT;
}

export function isSwapEvent(event: HistoryEvent): event is SwapEvent {
  return event.entryType === HistoryEventEntryType.SWAP_EVENT;
}

export const EVM_EVENTS = [
  HistoryEventEntryType.EVM_EVENT,
  HistoryEventEntryType.EVM_SWAP_EVENT,
] as const;

export function isEvmTypeEvent(type: HistoryEventEntryType): boolean {
  return Array.prototype.includes.call(EVM_EVENTS, type);
}

export const SOLANA_EVENTS = [
  HistoryEventEntryType.SOLANA_EVENT,
  HistoryEventEntryType.SOLANA_SWAP_EVENT,
] as const;

export function isSolanaTypeEvent(type: HistoryEventEntryType): boolean {
  return Array.prototype.includes.call(SOLANA_EVENTS, type);
}

export const STACKS_EVENTS = [
  HistoryEventEntryType.STACKS_EVENT,
] as const;

export function isStacksTypeEvent(type: HistoryEventEntryType): boolean {
  return Array.prototype.includes.call(STACKS_EVENTS, type);
}

const SWAP_EVENTS = [
  HistoryEventEntryType.SWAP_EVENT,
  HistoryEventEntryType.EVM_SWAP_EVENT,
  HistoryEventEntryType.SOLANA_SWAP_EVENT,
] as const;

export function isSwapTypeEvent(type: HistoryEventEntryType): boolean {
  return Array.prototype.includes.call(SWAP_EVENTS, type);
}

export type DecodableEventType = EvmHistoryEvent | EvmSwapEvent | SolanaEvent | SolanaSwapEvent | StacksEvent;

export function isEventDecodable(event: HistoryEvent): DecodableEventType | undefined {
  if (isEvmEvent(event) || isEvmSwapEvent(event) || isSolanaEvent(event) || isSolanaSwapEvent(event) || isStacksEvent(event)) {
    return event;
  }
  return undefined;
}
