import {defaultDataIdFromObject} from "apollo-cache-inmemory";
import {DocumentNode} from "graphql";
import {DataProxy} from "apollo-cache";
import {Change} from "./generated-models";

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

interface ValueChange {
  changeType: Change,
  value: Value,
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

export function handleAddRemove(client: DataProxy,
                                listQueryDocument: DocumentNode,
                                listFieldName : string,
                                change: ValueChange) {
  switch (change.changeType) {
    case Change.Add:
      handleAddOfValue(client, listQueryDocument, listFieldName, change.value);
      break;
    case Change.Remove:
      handleRemoveOfValueByUuid(client, listQueryDocument, listFieldName, change.value);
      break;
    default:
      break;
  }

}
