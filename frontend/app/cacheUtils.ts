import {defaultDataIdFromObject} from "apollo-cache-inmemory";

export const  dataIdFromObject = (object) => {
  // @ts-ignore
  if (object.uuid)
  {
    // @ts-ignore
    return `${object.__typename}:${object.uuid}`
  }
  else if (object.__typename === 'Interface')
  {
    return null; //Interfaces do not have unique ID's, we'd rather link them with their VMs
  }
  else {
    return defaultDataIdFromObject(object);
  }
};

export interface CacheWatcher<T> {
  complete: boolean;
  result: T;
}
