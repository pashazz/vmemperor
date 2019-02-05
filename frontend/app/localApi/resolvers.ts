import {
  ButtonConfigurationVmList,
  IResolvers,
  MutationResolvers,
  QueryResolvers,
  SelectedItemsQuery,
  VmEditOptions,
  VmPowerState,
  VmTableSelection
} from "../generated-models";

import {ApolloCache} from 'apollo-cache';
import VmListButtonConfigurationResolver = QueryResolvers.VmListButtonConfigurationResolver;
import SelectedItemsResolver = MutationResolvers.SelectedItemsResolver;
import {Set} from 'immutable';
import SelectedItemsArgs = QueryResolvers.SelectedItemsArgs;
/* This is workaround. See:  https://github.com/dotansimha/graphql-code-generator/issues/1133 */
interface StringIndexSignatureInterface {
  [index: string]: any
}

/* This is workaround, unless ApolloClient has its own context type */
interface Context {
  cache: ApolloCache<any>
}

type StringIndexed<T> = T & StringIndexSignatureInterface;
type LocalResolvers = StringIndexed<IResolvers>

/*
function genericTableOneSelector(selectionQuery)
  : Resolver<string[],{}, {}, SelectOneVariablesArgs> {
  return (parent1, args, context, info )   => {
    const query = selectionQuery;
    //@ts-ignore
    const previous : string[] = context.cache.readQuery({query});
    let data : string[] = [];
    if (previous) {
      if (!args.isSelect) {
        data = previous.filter(item => item !== args.item);
      } else {
        if (!previous.includes(args.item)) {
          data = [...previous, args.item];
        } else {
          data = previous;
        }
      }
    }
    //@ts-ignore
    context.cache.writeQuery({query, data});
    return data;
  }
}

function genericTableManySelector(selectionQuery)
  :  Resolver<string[],{}, {}, SelectManyVariablesArgs> {
  return (parent1, args, context, info) => {
    const query = selectionQuery;
    //@ts-ignore
    const previous : string[] = context.cache.readQuery({query})
    let data: string[] = [];
    if (previous) {
      if (!args.isSelect) {
        data = previous.filter(item => args.items.includes(item));
      } else {
        data = previous;
        for (const item of args.items) {
          if (!data.includes(item)) {
            data = [...data, item];
          }
        }
      }
    }
    //@ts-ignore
    context.cache.writeQuery({query, data});
    return data;
  }
}
*/

const selectedItems : SelectedItemsResolver<string[], {}, Context> =
  (parent1, args, context, info) => {
    const previous = context.cache.readQuery<SelectedItemsQuery.Query, SelectedItemsQuery.Variables>(
      {query: SelectedItemsQuery.Document,
        variables: {
          tableId: args.tableId
        }
      }
    );

    const getData = () : typeof previous => {
      const dataSet = Set.of(...previous.selectedItems);
      if (!args.isSelect) {
        return {
          selectedItems: dataSet.subtract(args.items).toArray()
        }
      }
      else {
        return {
          selectedItems: dataSet.union(args.items).toArray()
        }
      }
    };


    const data = getData();
    context.cache.writeQuery<SelectedItemsQuery.Query, SelectedItemsQuery.Variables>({
      query: SelectedItemsQuery.Document,
      variables: {tableId: args.tableId},
      data,
      });
      return data.selectedItems;
  };



const vmListButtonConfiguration :
  VmListButtonConfigurationResolver<ButtonConfigurationVmList, {}, Context> =
  (parent1, args, context, info) => {
    const tableSelection : VmTableSelection.Query =
      //@ts-ignore
      context.cache.readQuery<VmTableSelection.Query, VmTableSelection.Variables>({query: VmTableSelection.Document});

    const powerStates : VmPowerState.Query =
      //@ts-ignore
    context.cache.readQuery({query: VmPowerState.Document});

    //const notHalted = powerStates.vms.filter(vm => vm.powerState !==)

    return {
      start: false,
      stop: false,
      trash: false,
    }
  };
export const resolvers : LocalResolvers = {
  Mutation: {
    selectedItems,
    vmListButtonConfiguration
  }
};
