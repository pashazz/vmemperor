import {
  ApolloClient,
  ApolloError,
  FetchPolicy,
  OperationVariables,
  SubscriptionOptions,
} from 'apollo-client';
import { DocumentNode } from 'graphql';
import {useCallback, useEffect, useRef, useState} from 'react';
import isEqual from 'react-fast-compare';
import {Omit} from "react-apollo-hooks/lib/utils";
import {useApolloClient, QueryHookResult, QueryHookOptions, useQuery} from "react-apollo-hooks";
import {call} from "redux-saga/effects";


export type OnSubscriptionData<TData> = (
  options: OnSubscriptionDataOptions<TData>
) => any;

export interface OnSubscriptionDataOptions<TData> {
  client: ApolloClient<any>;
  subscriptionData: SubscriptionHookResult<TData>;
}

export interface SubscriptionHookOptions<TData, TVariables>
  extends Omit<SubscriptionOptions<TVariables>, 'query'> {
  shouldResubscribe?: any;
  onSubscriptionData?: OnSubscriptionData<TData>;
}

export interface SubscriptionHookResult<TData> {
  data?: TData;
  error?: ApolloError;
  loading: boolean;
}

export function useSubscription<TData = any, TVariables = OperationVariables>(
  query: DocumentNode,
  options?: SubscriptionHookOptions<TData, TVariables>
): SubscriptionHookResult<TData> {
  const prevOptions = useRef<null | SubscriptionHookOptions<TData, TVariables>>(
    null
  );
  const onSubscriptionData = useRef<null | OnSubscriptionData<TData>>(null);
  const client = useApolloClient();
  const [result, setResult] = useState<SubscriptionHookResult<TData>>({
    loading: true,
  });

  let shouldResubscribe;
  if (options) {
    onSubscriptionData.current = options.onSubscriptionData || null;

    shouldResubscribe = options.shouldResubscribe;
    if (typeof shouldResubscribe === 'function') {
      shouldResubscribe = !!shouldResubscribe();
    }
  }

  let inputs;
  if (shouldResubscribe === false) {
    // never resubscribe
    inputs = [];
  } else if (shouldResubscribe === undefined) {
    inputs = [
      query,
      isEqual(prevOptions.current, options) ? prevOptions.current : options,
    ];
  }

  useEffect(() => {
    if (options) {
      prevOptions.current = options;
    }
    const subscription = client
      .subscribe({
        ...options,
        query,
      })
      .subscribe({
        error: error => {
          setResult({ loading: false, data: result.data, error });
        },
        next: nextResult => {
          const newResult = {
            data: nextResult.data,
            error: undefined,
            loading: false,
          };
          setResult(newResult);
          if (onSubscriptionData.current) {
            onSubscriptionData.current({ client, subscriptionData: newResult });
          }
        },
      });
    return () => {
      subscription.unsubscribe();
    };
  }, inputs);

  return result;
}

export type UseQuery2UpdateQuery<TData, TSubscriptionData> = (
  previousQueryResult: TData,
  options: {
    subscriptionData: SubscriptionHookResult<TSubscriptionData>;
  }
) => TData;

/**
 * Wrapped version of `useQuery` that fixes the return type to include
 * `undefined`, and exposes a `useSubscribeToMore` hook.
 * Source: https://github.com/trojanowski/react-apollo-hooks/pull/37#issuecomment-460006967
 */
export const useQuery2 = <TData, TVariables = OperationVariables>(query: DocumentNode, opts?: QueryHookOptions<TVariables>) => {
  const result: QueryHookResult<TData, TVariables> = useQuery(query, opts);

  // Using a ref here allows the `onSubscriptionData` closure to access the latest value.
  const resultRef = useRef(result);
  resultRef.current = result;

  return {
    ...result,
    data: result.data as Partial<TData>,
    useSubscribeToMore: <TSubscriptionData, TSubscriptionVariables = OperationVariables>(
      subscriptionQuery: DocumentNode,
      subscriptionOptions: {
        variables?: TSubscriptionVariables;
        fetchPolicy?: FetchPolicy;
        updateQuery: UseQuery2UpdateQuery<TData, TSubscriptionData>;
        // `updateQuery` is implicitly memoised, and mandating this param forces
        // the consumer to think about that.
        updateQueryInputs?: ReadonlyArray<unknown>;
      }
    ) => {
      const { updateQuery, updateQueryInputs, ...passThroughOptions } = subscriptionOptions;
      const callback : OnSubscriptionData<TSubscriptionData> =
        ({subscriptionData}) =>  {
          resultRef.current.updateQuery(previousQueryResult =>
            updateQuery(previousQueryResult, {subscriptionData})
          );
        };
      const memoCallback = updateQueryInputs
        ? useCallback<OnSubscriptionData<TSubscriptionData>>(callback, updateQueryInputs)
        : callback;

      useSubscription<TSubscriptionData, TSubscriptionVariables>(subscriptionQuery, {
        ...passThroughOptions,
        onSubscriptionData: memoCallback
      });
    }
  };
};
