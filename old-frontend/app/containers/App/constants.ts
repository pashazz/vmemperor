/*
 * AppConstants
 * Each action has a corresponding type, which the reducer knows and picks up on.
 * To avoid weird typos between the reducer and the actions, we save them as
 * constants here. We prefix them with 'yourproject/YourComponent' so we avoid
 * reducers accidentally picking up actions they shouldn't.
 *
 * Follow this format:
 * export const YOUR_ACTION_CONSTANT = 'yourproject/YourContainer/YOUR_ACTION_CONSTANT';
 */

export const DEFAULT_LOCALE = 'en';

export const NEW_MESSAGE = 'emperor/global/NEW_MESSAGE';
export const AUTH = 'emperor/global/AUTH';
export const LOGOUT = 'emperor/global/LOGOUT';
export const SET_SESSION = 'emperor/global/SET_SESSION';
export const VMLIST_MESSAGE = 'emperor/global/VMLIST_MESSAGE';
export const AUTHENTICATED = 'emperor/global/authenticated';
export const LOGGED_OUT = 'emperor/global/logged_out';
export const VMLIST_URL="/api/vmlist";

export const VM_STATE_RUNNING="Running";
export const VM_STATE_HALTED="Halted";
export const VM_STATE_SUSPENDED="Suspended";
export const VM_STATE_PAUSED="Paused";

export const VM_RUN = 'emperor/global/VM_RUN';
export const VM_HALT = 'emperor/global/VM_HALT';
export const VM_DELETE = 'emperor/global/VM_DELETE';

export const VM_REBOOT = 'emperor/global/VM_REBOOT';

export const ADD_TO_WAIT_LIST = 'emperor/global/ADD_TO_WAIT_LIST';
export const REMOVE_FROM_WAIT_LIST = 'emperor/global/REMOVE_FROM_WAIT_LIST';

export const VM_RUN_ERROR = 'emperor/global/VM_RUN_ERROR';

