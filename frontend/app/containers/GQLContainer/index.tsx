import React from "react";
import {QueryProps} from "react-apollo";
import {UpdateQueryFn} from "apollo-client/core/watchQueryOptions";
import {DocumentNode} from "graphql";

interface UpdateableProps<TResponseType>{
  update: () => any;
  data: TResponseType;
}

interface Props<TResponseType,TVariables, TSubscriptionResponseType> {
  queryComponent: React.ComponentType<Partial<QueryProps<TResponseType, TVariables>>>;
  child: React.ComponentType<UpdateableProps<TResponseType>>;
  subscription?: DocumentNode; //Document with response type of TSubscriptionResponseType
  variables?: TVariables;
  updateQuery?: UpdateQueryFn<TResponseType, TVariables, TSubscriptionResponseType>;

}
export class GQLContainer<TResponseType, TVariables, TSubscriptionResponseType>
  extends React.PureComponent<Props<TResponseType, TVariables, TSubscriptionResponseType>> {

  render() {
    const Component = this.props.queryComponent;
    const Child = this.props.child;
    return (
      <Component variables={{...this.props.variables}}>
        {({ data, error, loading, subscribeToMore }) => {
          if (error)
          {
            return (
              <div>
                <h1>
                  {error.message}
                </h1>
              </div>
            );

          }
          if (loading)
          {
            return '...';
          }
          return (
            <Child
              update={ () =>
                subscribeToMore({
                  document: this.props.subscription,
                  variables: {...this.props.variables},
                  updateQuery: this.props.updateQuery,
                })}
              data={data}
            />
          )
        }
        }
      </Component>
    )
  }
}
