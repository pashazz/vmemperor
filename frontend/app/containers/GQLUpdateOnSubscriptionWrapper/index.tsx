
import { QueryProps } from 'react-apollo';
import { UpdateQueryFn } from 'apollo-client/core/watchQueryOptions';
import { DocumentNode } from 'graphql';
import React, {useEffect} from 'react';

interface FunctionalComponentProps <TResponseType> {
  child: React.ComponentType;
  dataProperty: string;
  data: TResponseType;
  subscribe?: () => () => any;
}

interface Props<TResponseType, TVariables, TSubscriptionResponseType> {
  queryComponent: React.ComponentType<Partial<QueryProps<TResponseType, TVariables>>>;
  child: React.ComponentType;
  subscription?: DocumentNode; // Document with response type of TSubscriptionResponseType
  variables: TVariables;
  updateQuery?: UpdateQueryFn<TResponseType, TVariables, TSubscriptionResponseType>;
  dataProperty: string;
}

function GQLUpdateOnSubscriptionWrapper<TResponseType>({ child, dataProperty, data, subscribe, ...props } : FunctionalComponentProps<TResponseType> & any)
{
  if (subscribe) {
    useEffect(() => {
      const unsubscribe = subscribe();
      return () => {
        unsubscribe();
      }
    });
  }
  const childProps = {...props, [dataProperty]: data};
  const Child = child;
  return (<Child {...childProps}/>);
}

export default class GQLQueryContainer<TResponseType, TVariables, TSubscriptionResponseType>
  extends React.PureComponent<Props<TResponseType, TVariables, TSubscriptionResponseType>> {

  static defaultProps = {
    dataProperty: "data"
  };

  render() {
    const Component = this.props.queryComponent;
    return (
      <Component variables={{ ...this.props.variables }}>
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
          let optionalProps : Partial<FunctionalComponentProps<TResponseType>> = {};
          if (this.props.subscription && this.props.updateQuery)
          {
            optionalProps = {
              subscribe: () =>
                subscribeToMore({
                  document: this.props.subscription,
                  variables: { ...this.props.variables },
                  updateQuery: this.props.updateQuery,
                })
            };
          }

          return (
            <GQLUpdateOnSubscriptionWrapper
              data={data}
              child={this.props.child}
              dataProperty={this.props.dataProperty}
              {...optionalProps}
            />
          );
        }
        }
      </Component>
    );
  }
}
