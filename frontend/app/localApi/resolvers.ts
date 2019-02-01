import {IResolvers, Resolver} from "../generated-models";
import {GetVmTableSelectionForSelectMutation} from "../api/local/vmsTable.graphql";
import {SelectOneVariablesArgs,  SelectManyVariablesArgs} from "../containers/ControlledTable";

/* This is workaround. See:  https://github.com/dotansimha/graphql-code-generator/issues/1133 */
interface StringIndexSignatureInterface {
  [index: string]: any
}
type StringIndexed<T> = T & StringIndexSignatureInterface;
type LocalResolvers = StringIndexed<IResolvers>

function genericTableOneSelector<KeyType>(selectionQuery)
  : Resolver<KeyType[],{}, {}, SelectOneVariablesArgs<KeyType>>  {
  return (parent1, args, context, info )   => {
    const query = selectionQuery;
    //@ts-ignore
    const previous : KeyType[] = context.cache.readQuery({query});
    let data : typeof previous  = null;
    if (!args.isSelect) {
      data = previous.filter(item => item !== args.item);
    }
    else {
      if (!previous.includes(args.item)) {
        data = [...previous, args.item];
      }
      else{
        data = previous;
      }
    }
    //@ts-ignore
    context.cache.writeQuery({query, data});
    return data;
  }
}

function genericTableManySelector<KeyType>(selectionQuery)
  :  Resolver<KeyType[],{}, {}, SelectManyVariablesArgs<KeyType>> {
  return (parent1, args, context, info) => {
    const query = selectionQuery;
    //@ts-ignore
    const previous: KeyType[] = context.cache.readQuery({query});
    let data: typeof previous = null;
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
    //@ts-ignore
    context.cache.writeQuery({query, data});
    return data;
  }
}
export const resolvers : LocalResolvers = {
  Mutation: {
    selectVmTableItem: genericTableOneSelector(GetVmTableSelectionForSelectMutation),
    selectVmTableItems: genericTableManySelector(GetVmTableSelectionForSelectMutation),
  }
};
