import {defaultDataIdFromObject} from "apollo-cache-inmemory";
import {DocumentNode} from "graphql";
import {DataProxy} from "apollo-cache";

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

interface Value {
  uuid: string
}


export function handleRemoveOfValueByUuid<QueryType>(client: DataProxy,
                                        listQueryDocument : DocumentNode,
                                        listFieldName : string,
                                        value: Value) {
  console.log("Removal of value: ", value.uuid);
  const query = client.readQuery<QueryType>({
    query: listQueryDocument
  });
  const newQuery: typeof query = {
    ...query,
    [listFieldName]: query[listFieldName].filter(item => item.uuid !== value.uuid)
  };
  client.writeQuery<QueryType>({
    query: listQueryDocument,
    data: newQuery
  });
}


export function handleAddOfValue<QueryType>(client: DataProxy,
                                                     listQueryDocument : DocumentNode,
                                                     listFieldName : string,
                                                     value: Value) {
  console.log("Removal of value: ", value.uuid);
  const query = client.readQuery<QueryType>({
    query: listQueryDocument
  });
  const newQuery: typeof query = {
    ...query,
    [listFieldName]: [...query[listFieldName], value],
  };
  client.writeQuery<QueryType>({
    query: listQueryDocument,
    data: newQuery
  });
}
