/*
 *
 * CreateVm actions
 *
 */

import {
  SET_POOLS,
  SET_ISOS,
  SET_NETWORKS,
  SET_NETWORK,
  LOAD_NETWORK,
  TOGGLE_MODAL,
  CREATE_VM,
  SET_TEMPLATES,
} from './constants';

export function setPools(pools) {
  return {
    type: SET_POOLS,
    pools,
  };
}

export const setIsos = (isos) => {
  return {
    type: SET_ISOS,
    isos
  }

};

export const setNetworks = (networks) => {
  return {
    type: SET_NETWORKS,
    networks
  }
};

export function createVM(form) {
  return {
    type: CREATE_VM,
    form,
  };
}

export function toggleModal() {
  return {
    type: TOGGLE_MODAL,
  };
}

export function setTemplates(templates) {
  return{
    type: SET_TEMPLATES,
    templates
  }
}
