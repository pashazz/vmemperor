export type Maybe<T> = T | null;

export interface NewVdi {
  /** Storage repository to create disk on */
  SR: string;
  /** Disk size of a newly created disk in megabytes */
  size: number;
}

export interface AutoInstall {
  /** VM hostname */
  hostname: string;
  /** Network installation URL */
  mirrorUrl?: Maybe<string>;
  /** Name of the newly created user */
  username: string;
  /** User and root password */
  password: string;
  /** User's full name */
  fullname?: Maybe<string>;
  /** Partition scheme (TODO) */
  partition: string;
  /** Static IP configuration, if needed */
  staticIpConfig?: Maybe<NetworkConfiguration>;
}

export interface NetworkConfiguration {
  ip: string;

  gateway: string;

  netmask: string;

  dns0: string;

  dns1?: Maybe<string>;
}

export interface TemplateInput {
  /** Template ID */
  uuid: string;
  /** Should this template be enabled, i.e. used in VMEmperor by users */
  enabled?: Maybe<boolean>;
}

export interface VmInput {
  /** VM ID */
  uuid: string;
  /** VM human-readable name */
  nameLabel?: Maybe<string>;
  /** VM human-readable description */
  nameDescription?: Maybe<string>;
  /** VM domain type: 'pv', 'hvm', 'pv_in_pvh' */
  domainType?: Maybe<string>;
}

export interface VmStartInput {
  /** Should this VM be started and immidiately paused */
  paused?: Maybe<boolean>;
  /** Should this VM be started forcibly */
  force?: Maybe<boolean>;
}

export enum PowerState {
  Halted = "Halted",
  Paused = "Paused",
  Running = "Running",
  Suspended = "Suspended"
}

export enum Table {
  Vms = "VMS"
}

export enum ShutdownForce {
  Hard = "HARD",
  Clean = "CLEAN"
}

export enum Change {
  Initial = "Initial",
  Add = "Add",
  Remove = "Remove",
  Change = "Change"
}

export enum PlaybookTaskState {
  Preparing = "Preparing",
  ConfigurationWarning = "ConfigurationWarning",
  Error = "Error",
  Running = "Running",
  Finished = "Finished",
  Unknown = "Unknown"
}

/** JSON String */
export type JsonString = any;

/** The `DateTime` scalar type represents a DateTime value as specified by [iso8601](https://en.wikipedia.org/wiki/ISO_8601). */
export type DateTime = any;

// ====================================================
// Documents
// ====================================================

export namespace VmEditOptions {
  export type Variables = {
    vm: VmInput;
  };

  export type Mutation = {
    __typename?: "Mutation";

    vm: Maybe<Vm>;
  };

  export type Vm = {
    __typename?: "VMMutation";

    success: boolean;
  };
}

export namespace SelectedItemsQuery {
  export type Variables = {
    tableId: Table;
  };

  export type Query = {
    __typename?: "Query";

    selectedItems: string[];
  };
}

export namespace VmTableSelection {
  export type Variables = {};

  export type Query = {
    __typename?: "Query";

    selectedItems: string[];
  };
}

export namespace VmTableSelect {
  export type Variables = {
    item: string;
    isSelect: boolean;
  };

  export type Mutation = {
    __typename?: "Mutation";

    selectedItems: Maybe<string[]>;
  };
}

export namespace VmTableSelectAll {
  export type Variables = {
    items: string[];
    isSelect: boolean;
  };

  export type Mutation = {
    __typename?: "Mutation";

    selectedItems: Maybe<string[]>;
  };
}

export namespace VmPowerState {
  export type Variables = {};

  export type Query = {
    __typename?: "Query";

    vms: (Maybe<Vms>)[];
  };

  export type Vms = {
    __typename?: "GVM";

    uuid: string;

    powerState: PowerState;
  };
}

export namespace VmSelectedReadyFor {
  export type Variables = {};

  export type Query = {
    __typename?: "Query";

    vmSelectedReadyFor: VmSelectedReadyFor;
  };

  export type VmSelectedReadyFor = {
    __typename?: "VMSelectedIDLists";

    start: string[];

    stop: string[];
  };
}

export namespace PlaybookLaunch {
  export type Variables = {
    id: string;
    vms?: Maybe<(Maybe<string>)[]>;
    variables?: Maybe<JsonString>;
  };

  export type Mutation = {
    __typename?: "Mutation";

    playbookLaunch: Maybe<PlaybookLaunch>;
  };

  export type PlaybookLaunch = {
    __typename?: "PlaybookLaunchMutation";

    taskId: string;
  };
}

export namespace PlaybookList {
  export type Variables = {};

  export type Query = {
    __typename?: "Query";

    playbooks: (Maybe<Playbooks>)[];
  };

  export type Playbooks = {
    __typename?: "GPlaybook";

    requires: Maybe<Requires>;

    name: string;

    variables: Maybe<JsonString>;

    id: string;

    inventory: Maybe<string>;

    description: Maybe<string>;
  };

  export type Requires = {
    __typename?: "PlaybookRequirements";

    osVersion: (Maybe<OsVersion>)[];
  };

  export type OsVersion = {
    __typename?: "OSVersion";

    distro: Maybe<string>;

    name: Maybe<string>;

    uname: Maybe<string>;

    major: Maybe<number>;

    minor: Maybe<number>;
  };
}

export namespace RebootVm {
  export type Variables = {
    uuid: string;
  };

  export type Mutation = {
    __typename?: "Mutation";

    vmReboot: Maybe<VmReboot>;
  };

  export type VmReboot = {
    __typename?: "VMRebootMutation";

    taskId: string;
  };
}

export namespace ShutdownVm {
  export type Variables = {
    uuid: string;
  };

  export type Mutation = {
    __typename?: "Mutation";

    vmShutdown: Maybe<VmShutdown>;
  };

  export type VmShutdown = {
    __typename?: "VMShutdownMutation";

    taskId: string;
  };
}

export namespace StartVm {
  export type Variables = {
    uuid: string;
  };

  export type Mutation = {
    __typename?: "Mutation";

    vmStart: Maybe<VmStart>;
  };

  export type VmStart = {
    __typename?: "VMStartMutation";

    taskId: string;
  };
}

export namespace VmInfo {
  export type Variables = {
    uuid: string;
  };

  export type Query = {
    __typename?: "Query";

    vm: Vm;
  };

  export type Vm = VmInfoFragment.Fragment;
}

export namespace VmInfoUpdate {
  export type Variables = {
    uuid: string;
  };

  export type Subscription = {
    __typename?: "Subscription";

    vm: Maybe<Vm>;
  };

  export type Vm = VmInfoFragment.Fragment;
}

export namespace VmList {
  export type Variables = {};

  export type Query = {
    __typename?: "Query";

    vms: (Maybe<Vms>)[];
  };

  export type Vms = VmListFragment.Fragment;
}

export namespace VmListUpdate {
  export type Variables = {};

  export type Subscription = {
    __typename?: "Subscription";

    vms: Vms;
  };

  export type Vms = {
    __typename?: "GVMsSubscription";

    value: Value;

    changeType: Change;
  };

  export type Value = VmListFragment.Fragment;
}

export namespace VmInfoFragment {
  export type Fragment = {
    __typename?: "GVM";

    uuid: string;

    nameLabel: string;

    nameDescription: string;

    interfaces: Maybe<(Maybe<Interfaces>)[]>;

    disks: Maybe<(Maybe<Disks>)[]>;

    powerState: PowerState;

    osVersion: Maybe<OsVersion>;

    startTime: DateTime;

    domainType: string;
  };

  export type Interfaces = {
    __typename?: "Interface";

    network: Network;

    ip: Maybe<string>;

    ipv6: Maybe<string>;

    id: string;
  };

  export type Network = {
    __typename?: "GNetwork";

    uuid: string;

    nameLabel: string;
  };

  export type Disks = {
    __typename?: "BlockDevice";

    id: string;

    mode: string;

    type: string;

    device: string;

    attached: boolean;

    bootable: boolean;

    VDI: Maybe<Vdi>;
  };

  export type Vdi = {
    __typename?: "DiskImage";

    uuid: string;

    nameDescription: string;

    nameLabel: string;
  };

  export type OsVersion = {
    __typename?: "OSVersion";

    name: Maybe<string>;
  };
}

export namespace VmListFragment {
  export type Fragment = {
    __typename?: "GVM";

    uuid: string;

    nameLabel: string;

    powerState: PowerState;
  };
}

import * as ReactApollo from "react-apollo";
import * as React from "react";

import gql from "graphql-tag";

// ====================================================
// Fragments
// ====================================================

export namespace VmInfoFragment {
  export const FragmentDoc = gql`
    fragment VMInfoFragment on GVM {
      uuid
      nameLabel
      nameDescription
      interfaces {
        network {
          uuid
          nameLabel
        }
        ip
        ipv6
        id
      }
      disks {
        id
        mode
        type
        device
        attached
        bootable
        VDI {
          uuid
          nameDescription
          nameLabel
        }
      }
      powerState
      osVersion {
        name
      }
      startTime
      domainType
    }
  `;
}

export namespace VmListFragment {
  export const FragmentDoc = gql`
    fragment VMListFragment on GVM {
      uuid
      nameLabel
      powerState
    }
  `;
}

// ====================================================
// Components
// ====================================================

export namespace VmEditOptions {
  export const Document = gql`
    mutation VMEditOptions($vm: VMInput!) {
      vm(vm: $vm) {
        success
      }
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.MutationProps<Mutation, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Mutation<Mutation, Variables>
          mutation={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.MutateProps<Mutation, Variables>
  > &
    TChildProps;
  export type MutationFn = ReactApollo.MutationFn<Mutation, Variables>;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Mutation,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Mutation, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace SelectedItemsQuery {
  export const Document = gql`
    query SelectedItemsQuery($tableId: Table!) {
      selectedItems(tableId: $tableId) @client
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.QueryProps<Query, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Query<Query, Variables>
          query={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Query, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Query,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Query, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace VmTableSelection {
  export const Document = gql`
    query VmTableSelection {
      selectedItems(tableId: VMS) @client
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.QueryProps<Query, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Query<Query, Variables>
          query={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Query, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Query,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Query, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace VmTableSelect {
  export const Document = gql`
    mutation VmTableSelect($item: ID!, $isSelect: Boolean!) {
      selectedItems(tableId: VMS, items: [$item], isSelect: $isSelect) @client
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.MutationProps<Mutation, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Mutation<Mutation, Variables>
          mutation={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.MutateProps<Mutation, Variables>
  > &
    TChildProps;
  export type MutationFn = ReactApollo.MutationFn<Mutation, Variables>;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Mutation,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Mutation, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace VmTableSelectAll {
  export const Document = gql`
    mutation VmTableSelectAll($items: [ID!]!, $isSelect: Boolean!) {
      selectedItems(tableId: VMS, items: $items, isSelect: $isSelect) @client
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.MutationProps<Mutation, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Mutation<Mutation, Variables>
          mutation={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.MutateProps<Mutation, Variables>
  > &
    TChildProps;
  export type MutationFn = ReactApollo.MutationFn<Mutation, Variables>;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Mutation,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Mutation, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace VmPowerState {
  export const Document = gql`
    query VmPowerState {
      vms {
        uuid
        powerState
      }
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.QueryProps<Query, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Query<Query, Variables>
          query={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Query, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Query,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Query, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace VmSelectedReadyFor {
  export const Document = gql`
    query VMSelectedReadyFor {
      vmSelectedReadyFor @client {
        start
        stop
      }
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.QueryProps<Query, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Query<Query, Variables>
          query={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Query, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Query,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Query, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace PlaybookLaunch {
  export const Document = gql`
    mutation PlaybookLaunch($id: ID!, $vms: [ID], $variables: JSONString) {
      playbookLaunch(id: $id, vms: $vms, variables: $variables) {
        taskId
      }
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.MutationProps<Mutation, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Mutation<Mutation, Variables>
          mutation={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.MutateProps<Mutation, Variables>
  > &
    TChildProps;
  export type MutationFn = ReactApollo.MutationFn<Mutation, Variables>;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Mutation,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Mutation, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace PlaybookList {
  export const Document = gql`
    query PlaybookList {
      playbooks {
        requires {
          osVersion {
            distro
            name
            uname
            major
            minor
          }
        }
        name
        variables
        id
        inventory
        description
      }
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.QueryProps<Query, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Query<Query, Variables>
          query={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Query, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Query,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Query, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace RebootVm {
  export const Document = gql`
    mutation RebootVm($uuid: ID!) {
      vmReboot(uuid: $uuid) {
        taskId
      }
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.MutationProps<Mutation, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Mutation<Mutation, Variables>
          mutation={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.MutateProps<Mutation, Variables>
  > &
    TChildProps;
  export type MutationFn = ReactApollo.MutationFn<Mutation, Variables>;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Mutation,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Mutation, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace ShutdownVm {
  export const Document = gql`
    mutation ShutdownVM($uuid: ID!) {
      vmShutdown(uuid: $uuid) {
        taskId
      }
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.MutationProps<Mutation, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Mutation<Mutation, Variables>
          mutation={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.MutateProps<Mutation, Variables>
  > &
    TChildProps;
  export type MutationFn = ReactApollo.MutationFn<Mutation, Variables>;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Mutation,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Mutation, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace StartVm {
  export const Document = gql`
    mutation StartVM($uuid: ID!) {
      vmStart(uuid: $uuid) {
        taskId
      }
    }
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.MutationProps<Mutation, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Mutation<Mutation, Variables>
          mutation={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.MutateProps<Mutation, Variables>
  > &
    TChildProps;
  export type MutationFn = ReactApollo.MutationFn<Mutation, Variables>;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Mutation,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Mutation, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace VmInfo {
  export const Document = gql`
    query VMInfo($uuid: ID!) {
      vm(uuid: $uuid) {
        ...VMInfoFragment
      }
    }

    ${VmInfoFragment.FragmentDoc}
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.QueryProps<Query, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Query<Query, Variables>
          query={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Query, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Query,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Query, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace VmInfoUpdate {
  export const Document = gql`
    subscription VMInfoUpdate($uuid: ID!) {
      vm(uuid: $uuid) {
        ...VMInfoFragment
      }
    }

    ${VmInfoFragment.FragmentDoc}
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.SubscriptionProps<Subscription, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Subscription<Subscription, Variables>
          subscription={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Subscription, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Subscription,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<
      TProps,
      Subscription,
      Variables,
      Props<TChildProps>
    >(Document, operationOptions);
  }
}
export namespace VmList {
  export const Document = gql`
    query VMList {
      vms {
        ...VMListFragment
      }
    }

    ${VmListFragment.FragmentDoc}
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.QueryProps<Query, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Query<Query, Variables>
          query={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Query, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Query,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<TProps, Query, Variables, Props<TChildProps>>(
      Document,
      operationOptions
    );
  }
}
export namespace VmListUpdate {
  export const Document = gql`
    subscription VMListUpdate {
      vms {
        value {
          ...VMListFragment
        }
        changeType
      }
    }

    ${VmListFragment.FragmentDoc}
  `;
  export class Component extends React.Component<
    Partial<ReactApollo.SubscriptionProps<Subscription, Variables>>
  > {
    render() {
      return (
        <ReactApollo.Subscription<Subscription, Variables>
          subscription={Document}
          {...(this as any)["props"] as any}
        />
      );
    }
  }
  export type Props<TChildProps = any> = Partial<
    ReactApollo.DataProps<Subscription, Variables>
  > &
    TChildProps;
  export function HOC<TProps, TChildProps = any>(
    operationOptions:
      | ReactApollo.OperationOption<
          TProps,
          Subscription,
          Variables,
          Props<TChildProps>
        >
      | undefined
  ) {
    return ReactApollo.graphql<
      TProps,
      Subscription,
      Variables,
      Props<TChildProps>
    >(Document, operationOptions);
  }
}
import {
  GraphQLResolveInfo,
  GraphQLScalarType,
  GraphQLScalarTypeConfig
} from "graphql";

export type Resolver<Result, Parent = {}, Context = {}, Args = {}> = (
  parent: Parent,
  args: Args,
  context: Context,
  info: GraphQLResolveInfo
) => Promise<Result> | Result;

export interface ISubscriptionResolverObject<Result, Parent, Context, Args> {
  subscribe<R = Result, P = Parent>(
    parent: P,
    args: Args,
    context: Context,
    info: GraphQLResolveInfo
  ): AsyncIterator<R | Result> | Promise<AsyncIterator<R | Result>>;
  resolve?<R = Result, P = Parent>(
    parent: P,
    args: Args,
    context: Context,
    info: GraphQLResolveInfo
  ): R | Result | Promise<R | Result>;
}

export type SubscriptionResolver<
  Result,
  Parent = {},
  Context = {},
  Args = {}
> =
  | ((
      ...args: any[]
    ) => ISubscriptionResolverObject<Result, Parent, Context, Args>)
  | ISubscriptionResolverObject<Result, Parent, Context, Args>;

export type TypeResolveFn<Types, Parent = {}, Context = {}> = (
  parent: Parent,
  context: Context,
  info: GraphQLResolveInfo
) => Maybe<Types>;

export type NextResolverFn<T> = () => Promise<T>;

export type DirectiveResolverFn<TResult, TArgs = {}, TContext = {}> = (
  next: NextResolverFn<TResult>,
  source: any,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;

export namespace QueryResolvers {
  export interface Resolvers<Context = {}, TypeParent = {}> {
    /** All VMs available to user */
    vms?: VmsResolver<(Maybe<Gvm>)[], TypeParent, Context>;

    vm?: VmResolver<Gvm, TypeParent, Context>;
    /** All Networks available to user */
    networks?: NetworksResolver<(Maybe<GNetwork>)[], TypeParent, Context>;
    /** Information about a single network */
    network?: NetworkResolver<GNetwork, TypeParent, Context>;
    /** All Storage repositories available to user */
    srs?: SrsResolver<(Maybe<Gsr>)[], TypeParent, Context>;
    /** Information about a single storage repository */
    sr?: SrResolver<Gsr, TypeParent, Context>;
    /** All Virtual Disk Images (hard disks), available for user */
    vdis?: VdisResolver<(Maybe<Gvdi>)[], TypeParent, Context>;
    /** Information about a single virtual disk image (hard disk) */
    vdi?: VdiResolver<Gvdi, TypeParent, Context>;
    /** All ISO images available for user */
    isos?: IsosResolver<(Maybe<Giso>)[], TypeParent, Context>;
    /** Information about a single ISO image */
    iso?: IsoResolver<Gvdi, TypeParent, Context>;
    /** All templates */
    templates?: TemplatesResolver<(Maybe<GTemplate>)[], TypeParent, Context>;
    /** List of Ansible-powered playbooks */
    playbooks?: PlaybooksResolver<(Maybe<GPlaybook>)[], TypeParent, Context>;
    /** Information about Ansible-powered playbook */
    playbook?: PlaybookResolver<GPlaybook, TypeParent, Context>;

    selectedItems?: SelectedItemsResolver<string[], TypeParent, Context>;

    vmSelectedReadyFor?: VmSelectedReadyForResolver<
      VmSelectedIdLists,
      TypeParent,
      Context
    >;
  }

  export type VmsResolver<
    R = (Maybe<Gvm>)[],
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VmResolver<R = Gvm, Parent = {}, Context = {}> = Resolver<
    R,
    Parent,
    Context,
    VmArgs
  >;
  export interface VmArgs {
    uuid?: Maybe<string>;
  }

  export type NetworksResolver<
    R = (Maybe<GNetwork>)[],
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NetworkResolver<
    R = GNetwork,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, NetworkArgs>;
  export interface NetworkArgs {
    uuid?: Maybe<string>;
  }

  export type SrsResolver<
    R = (Maybe<Gsr>)[],
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type SrResolver<R = Gsr, Parent = {}, Context = {}> = Resolver<
    R,
    Parent,
    Context,
    SrArgs
  >;
  export interface SrArgs {
    uuid?: Maybe<string>;
  }

  export type VdisResolver<
    R = (Maybe<Gvdi>)[],
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VdiResolver<R = Gvdi, Parent = {}, Context = {}> = Resolver<
    R,
    Parent,
    Context,
    VdiArgs
  >;
  export interface VdiArgs {
    uuid?: Maybe<string>;
  }

  export type IsosResolver<
    R = (Maybe<Giso>)[],
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type IsoResolver<R = Gvdi, Parent = {}, Context = {}> = Resolver<
    R,
    Parent,
    Context,
    IsoArgs
  >;
  export interface IsoArgs {
    uuid?: Maybe<string>;
  }

  export type TemplatesResolver<
    R = (Maybe<GTemplate>)[],
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type PlaybooksResolver<
    R = (Maybe<GPlaybook>)[],
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type PlaybookResolver<
    R = GPlaybook,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, PlaybookArgs>;
  export interface PlaybookArgs {
    id?: Maybe<string>;
  }

  export type SelectedItemsResolver<
    R = string[],
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, SelectedItemsArgs>;
  export interface SelectedItemsArgs {
    tableId: Table;
  }

  export type VmSelectedReadyForResolver<
    R = VmSelectedIdLists,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GvmResolvers {
  export interface Resolvers<Context = {}, TypeParent = Gvm> {
    /** a human-readable name */
    nameLabel?: NameLabelResolver<string, TypeParent, Context>;
    /** a human-readable description */
    nameDescription?: NameDescriptionResolver<string, TypeParent, Context>;
    /** Unique constant identifier/object reference */
    ref?: RefResolver<string, TypeParent, Context>;
    /** Unique session-dependent identifier/object reference */
    uuid?: UuidResolver<string, TypeParent, Context>;

    access?: AccessResolver<(Maybe<GAccessEntry>)[], TypeParent, Context>;
    /** Network adapters connected to a VM */
    interfaces?: InterfacesResolver<
      Maybe<(Maybe<Interface>)[]>,
      TypeParent,
      Context
    >;
    /** True if PV drivers are up to date, reported if Guest Additions are installed */
    PVDriversUpToDate?: PvDriversUpToDateResolver<
      Maybe<boolean>,
      TypeParent,
      Context
    >;
    /** PV drivers version, if available */
    PVDriversVersion?: PvDriversVersionResolver<
      Maybe<PvDriversVersion>,
      TypeParent,
      Context
    >;

    disks?: DisksResolver<Maybe<(Maybe<BlockDevice>)[]>, TypeParent, Context>;

    VCPUsAtStartup?: VcpUsAtStartupResolver<number, TypeParent, Context>;

    VCPUsMax?: VcpUsMaxResolver<number, TypeParent, Context>;

    domainType?: DomainTypeResolver<string, TypeParent, Context>;

    guestMetrics?: GuestMetricsResolver<string, TypeParent, Context>;

    installTime?: InstallTimeResolver<DateTime, TypeParent, Context>;

    memoryActual?: MemoryActualResolver<number, TypeParent, Context>;

    memoryStaticMin?: MemoryStaticMinResolver<number, TypeParent, Context>;

    memoryStaticMax?: MemoryStaticMaxResolver<number, TypeParent, Context>;

    memoryDynamicMin?: MemoryDynamicMinResolver<number, TypeParent, Context>;

    memoryDynamicMax?: MemoryDynamicMaxResolver<number, TypeParent, Context>;

    metrics?: MetricsResolver<string, TypeParent, Context>;

    osVersion?: OsVersionResolver<Maybe<OsVersion>, TypeParent, Context>;

    powerState?: PowerStateResolver<PowerState, TypeParent, Context>;

    startTime?: StartTimeResolver<DateTime, TypeParent, Context>;
  }

  export type NameLabelResolver<
    R = string,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NameDescriptionResolver<
    R = string,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type RefResolver<R = string, Parent = Gvm, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type UuidResolver<R = string, Parent = Gvm, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type AccessResolver<
    R = (Maybe<GAccessEntry>)[],
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type InterfacesResolver<
    R = Maybe<(Maybe<Interface>)[]>,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type PvDriversUpToDateResolver<
    R = Maybe<boolean>,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type PvDriversVersionResolver<
    R = Maybe<PvDriversVersion>,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type DisksResolver<
    R = Maybe<(Maybe<BlockDevice>)[]>,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VcpUsAtStartupResolver<
    R = number,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VcpUsMaxResolver<
    R = number,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type DomainTypeResolver<
    R = string,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type GuestMetricsResolver<
    R = string,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type InstallTimeResolver<
    R = DateTime,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MemoryActualResolver<
    R = number,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MemoryStaticMinResolver<
    R = number,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MemoryStaticMaxResolver<
    R = number,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MemoryDynamicMinResolver<
    R = number,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MemoryDynamicMaxResolver<
    R = number,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MetricsResolver<
    R = string,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type OsVersionResolver<
    R = Maybe<OsVersion>,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type PowerStateResolver<
    R = PowerState,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type StartTimeResolver<
    R = DateTime,
    Parent = Gvm,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GAccessEntryResolvers {
  export interface Resolvers<Context = {}, TypeParent = GAccessEntry> {
    access?: AccessResolver<(Maybe<string>)[], TypeParent, Context>;

    userid?: UseridResolver<string, TypeParent, Context>;
  }

  export type AccessResolver<
    R = (Maybe<string>)[],
    Parent = GAccessEntry,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type UseridResolver<
    R = string,
    Parent = GAccessEntry,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace InterfaceResolvers {
  export interface Resolvers<Context = {}, TypeParent = Interface> {
    id?: IdResolver<string, TypeParent, Context>;

    MAC?: MacResolver<string, TypeParent, Context>;

    VIF?: VifResolver<string, TypeParent, Context>;

    ip?: IpResolver<Maybe<string>, TypeParent, Context>;

    ipv6?: Ipv6Resolver<Maybe<string>, TypeParent, Context>;

    network?: NetworkResolver<GNetwork, TypeParent, Context>;

    status?: StatusResolver<Maybe<string>, TypeParent, Context>;

    attached?: AttachedResolver<boolean, TypeParent, Context>;
  }

  export type IdResolver<
    R = string,
    Parent = Interface,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MacResolver<
    R = string,
    Parent = Interface,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VifResolver<
    R = string,
    Parent = Interface,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type IpResolver<
    R = Maybe<string>,
    Parent = Interface,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type Ipv6Resolver<
    R = Maybe<string>,
    Parent = Interface,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NetworkResolver<
    R = GNetwork,
    Parent = Interface,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type StatusResolver<
    R = Maybe<string>,
    Parent = Interface,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type AttachedResolver<
    R = boolean,
    Parent = Interface,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GNetworkResolvers {
  export interface Resolvers<Context = {}, TypeParent = GNetwork> {
    /** a human-readable name */
    nameLabel?: NameLabelResolver<string, TypeParent, Context>;
    /** a human-readable description */
    nameDescription?: NameDescriptionResolver<string, TypeParent, Context>;
    /** Unique constant identifier/object reference */
    ref?: RefResolver<string, TypeParent, Context>;
    /** Unique session-dependent identifier/object reference */
    uuid?: UuidResolver<string, TypeParent, Context>;

    access?: AccessResolver<(Maybe<GAccessEntry>)[], TypeParent, Context>;

    VMs?: VMsResolver<Maybe<(Maybe<Gvm>)[]>, TypeParent, Context>;

    otherConfig?: OtherConfigResolver<Maybe<JsonString>, TypeParent, Context>;
  }

  export type NameLabelResolver<
    R = string,
    Parent = GNetwork,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NameDescriptionResolver<
    R = string,
    Parent = GNetwork,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type RefResolver<
    R = string,
    Parent = GNetwork,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type UuidResolver<
    R = string,
    Parent = GNetwork,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type AccessResolver<
    R = (Maybe<GAccessEntry>)[],
    Parent = GNetwork,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VMsResolver<
    R = Maybe<(Maybe<Gvm>)[]>,
    Parent = GNetwork,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type OtherConfigResolver<
    R = Maybe<JsonString>,
    Parent = GNetwork,
    Context = {}
  > = Resolver<R, Parent, Context>;
}
/** Drivers version. We don't want any fancy resolver except for the thing that we know that it's a dict in VM document */
export namespace PvDriversVersionResolvers {
  export interface Resolvers<Context = {}, TypeParent = PvDriversVersion> {
    major?: MajorResolver<Maybe<number>, TypeParent, Context>;

    minor?: MinorResolver<Maybe<number>, TypeParent, Context>;

    micro?: MicroResolver<Maybe<number>, TypeParent, Context>;

    build?: BuildResolver<Maybe<number>, TypeParent, Context>;
  }

  export type MajorResolver<
    R = Maybe<number>,
    Parent = PvDriversVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MinorResolver<
    R = Maybe<number>,
    Parent = PvDriversVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MicroResolver<
    R = Maybe<number>,
    Parent = PvDriversVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type BuildResolver<
    R = Maybe<number>,
    Parent = PvDriversVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace BlockDeviceResolvers {
  export interface Resolvers<Context = {}, TypeParent = BlockDevice> {
    id?: IdResolver<string, TypeParent, Context>;

    attached?: AttachedResolver<boolean, TypeParent, Context>;

    bootable?: BootableResolver<boolean, TypeParent, Context>;

    device?: DeviceResolver<string, TypeParent, Context>;

    mode?: ModeResolver<string, TypeParent, Context>;

    type?: TypeResolver<string, TypeParent, Context>;

    VDI?: VdiResolver<Maybe<DiskImage>, TypeParent, Context>;
  }

  export type IdResolver<
    R = string,
    Parent = BlockDevice,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type AttachedResolver<
    R = boolean,
    Parent = BlockDevice,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type BootableResolver<
    R = boolean,
    Parent = BlockDevice,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type DeviceResolver<
    R = string,
    Parent = BlockDevice,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type ModeResolver<
    R = string,
    Parent = BlockDevice,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type TypeResolver<
    R = string,
    Parent = BlockDevice,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VdiResolver<
    R = Maybe<DiskImage>,
    Parent = BlockDevice,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GsrResolvers {
  export interface Resolvers<Context = {}, TypeParent = Gsr> {
    /** a human-readable name */
    nameLabel?: NameLabelResolver<string, TypeParent, Context>;
    /** a human-readable description */
    nameDescription?: NameDescriptionResolver<string, TypeParent, Context>;
    /** Unique constant identifier/object reference */
    ref?: RefResolver<string, TypeParent, Context>;
    /** Unique session-dependent identifier/object reference */
    uuid?: UuidResolver<string, TypeParent, Context>;

    PBDs?: PbDsResolver<Maybe<(Maybe<string>)[]>, TypeParent, Context>;

    VDIs?: VdIsResolver<Maybe<(Maybe<DiskImage>)[]>, TypeParent, Context>;

    contentType?: ContentTypeResolver<string, TypeParent, Context>;
  }

  export type NameLabelResolver<
    R = string,
    Parent = Gsr,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NameDescriptionResolver<
    R = string,
    Parent = Gsr,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type RefResolver<R = string, Parent = Gsr, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type UuidResolver<R = string, Parent = Gsr, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type PbDsResolver<
    R = Maybe<(Maybe<string>)[]>,
    Parent = Gsr,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VdIsResolver<
    R = Maybe<(Maybe<DiskImage>)[]>,
    Parent = Gsr,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type ContentTypeResolver<
    R = string,
    Parent = Gsr,
    Context = {}
  > = Resolver<R, Parent, Context>;
}
/** OS version reported by Xen tools */
export namespace OsVersionResolvers {
  export interface Resolvers<Context = {}, TypeParent = OsVersion> {
    name?: NameResolver<Maybe<string>, TypeParent, Context>;

    uname?: UnameResolver<Maybe<string>, TypeParent, Context>;

    distro?: DistroResolver<Maybe<string>, TypeParent, Context>;

    major?: MajorResolver<Maybe<number>, TypeParent, Context>;

    minor?: MinorResolver<Maybe<number>, TypeParent, Context>;
  }

  export type NameResolver<
    R = Maybe<string>,
    Parent = OsVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type UnameResolver<
    R = Maybe<string>,
    Parent = OsVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type DistroResolver<
    R = Maybe<string>,
    Parent = OsVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MajorResolver<
    R = Maybe<number>,
    Parent = OsVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MinorResolver<
    R = Maybe<number>,
    Parent = OsVersion,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GvdiResolvers {
  export interface Resolvers<Context = {}, TypeParent = Gvdi> {
    /** a human-readable name */
    nameLabel?: NameLabelResolver<string, TypeParent, Context>;
    /** a human-readable description */
    nameDescription?: NameDescriptionResolver<string, TypeParent, Context>;
    /** Unique constant identifier/object reference */
    ref?: RefResolver<string, TypeParent, Context>;
    /** Unique session-dependent identifier/object reference */
    uuid?: UuidResolver<string, TypeParent, Context>;

    access?: AccessResolver<(Maybe<GAccessEntry>)[], TypeParent, Context>;

    SR?: SrResolver<Maybe<Gsr>, TypeParent, Context>;

    VMs?: VMsResolver<Maybe<(Maybe<Gvm>)[]>, TypeParent, Context>;

    virtualSize?: VirtualSizeResolver<number, TypeParent, Context>;
  }

  export type NameLabelResolver<
    R = string,
    Parent = Gvdi,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NameDescriptionResolver<
    R = string,
    Parent = Gvdi,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type RefResolver<R = string, Parent = Gvdi, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type UuidResolver<R = string, Parent = Gvdi, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type AccessResolver<
    R = (Maybe<GAccessEntry>)[],
    Parent = Gvdi,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type SrResolver<
    R = Maybe<Gsr>,
    Parent = Gvdi,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VMsResolver<
    R = Maybe<(Maybe<Gvm>)[]>,
    Parent = Gvdi,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VirtualSizeResolver<
    R = number,
    Parent = Gvdi,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GisoResolvers {
  export interface Resolvers<Context = {}, TypeParent = Giso> {
    /** a human-readable name */
    nameLabel?: NameLabelResolver<string, TypeParent, Context>;
    /** a human-readable description */
    nameDescription?: NameDescriptionResolver<string, TypeParent, Context>;
    /** Unique constant identifier/object reference */
    ref?: RefResolver<string, TypeParent, Context>;
    /** Unique session-dependent identifier/object reference */
    uuid?: UuidResolver<string, TypeParent, Context>;

    access?: AccessResolver<(Maybe<GAccessEntry>)[], TypeParent, Context>;

    SR?: SrResolver<Maybe<Gsr>, TypeParent, Context>;

    VMs?: VMsResolver<Maybe<(Maybe<Gvm>)[]>, TypeParent, Context>;

    virtualSize?: VirtualSizeResolver<number, TypeParent, Context>;

    location?: LocationResolver<string, TypeParent, Context>;
  }

  export type NameLabelResolver<
    R = string,
    Parent = Giso,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NameDescriptionResolver<
    R = string,
    Parent = Giso,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type RefResolver<R = string, Parent = Giso, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type UuidResolver<R = string, Parent = Giso, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type AccessResolver<
    R = (Maybe<GAccessEntry>)[],
    Parent = Giso,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type SrResolver<
    R = Maybe<Gsr>,
    Parent = Giso,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VMsResolver<
    R = Maybe<(Maybe<Gvm>)[]>,
    Parent = Giso,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VirtualSizeResolver<
    R = number,
    Parent = Giso,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type LocationResolver<
    R = string,
    Parent = Giso,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GTemplateResolvers {
  export interface Resolvers<Context = {}, TypeParent = GTemplate> {
    /** a human-readable name */
    nameLabel?: NameLabelResolver<string, TypeParent, Context>;
    /** a human-readable description */
    nameDescription?: NameDescriptionResolver<string, TypeParent, Context>;
    /** Unique constant identifier/object reference */
    ref?: RefResolver<string, TypeParent, Context>;
    /** Unique session-dependent identifier/object reference */
    uuid?: UuidResolver<string, TypeParent, Context>;

    access?: AccessResolver<(Maybe<GAccessEntry>)[], TypeParent, Context>;
    /** If a template supports auto-installation, here a distro name is provided */
    osKind?: OsKindResolver<Maybe<string>, TypeParent, Context>;
    /** True if this template works with hardware assisted virtualization */
    hvm?: HvmResolver<boolean, TypeParent, Context>;
    /** True if this template is available for regular users */
    enabled?: EnabledResolver<boolean, TypeParent, Context>;
  }

  export type NameLabelResolver<
    R = string,
    Parent = GTemplate,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NameDescriptionResolver<
    R = string,
    Parent = GTemplate,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type RefResolver<
    R = string,
    Parent = GTemplate,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type UuidResolver<
    R = string,
    Parent = GTemplate,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type AccessResolver<
    R = (Maybe<GAccessEntry>)[],
    Parent = GTemplate,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type OsKindResolver<
    R = Maybe<string>,
    Parent = GTemplate,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type HvmResolver<
    R = boolean,
    Parent = GTemplate,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type EnabledResolver<
    R = boolean,
    Parent = GTemplate,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GPlaybookResolvers {
  export interface Resolvers<Context = {}, TypeParent = GPlaybook> {
    /** Playbook ID */
    id?: IdResolver<string, TypeParent, Context>;
    /** Inventory file path */
    inventory?: InventoryResolver<Maybe<string>, TypeParent, Context>;
    /** Requirements for running this playbook */
    requires?: RequiresResolver<
      Maybe<PlaybookRequirements>,
      TypeParent,
      Context
    >;
    /** Playbook name */
    name?: NameResolver<string, TypeParent, Context>;
    /** Playbook description */
    description?: DescriptionResolver<Maybe<string>, TypeParent, Context>;
    /** Variables available for change to an user */
    variables?: VariablesResolver<Maybe<JsonString>, TypeParent, Context>;
  }

  export type IdResolver<
    R = string,
    Parent = GPlaybook,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type InventoryResolver<
    R = Maybe<string>,
    Parent = GPlaybook,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type RequiresResolver<
    R = Maybe<PlaybookRequirements>,
    Parent = GPlaybook,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NameResolver<
    R = string,
    Parent = GPlaybook,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type DescriptionResolver<
    R = Maybe<string>,
    Parent = GPlaybook,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type VariablesResolver<
    R = Maybe<JsonString>,
    Parent = GPlaybook,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace PlaybookRequirementsResolvers {
  export interface Resolvers<Context = {}, TypeParent = PlaybookRequirements> {
    /** Minimal supported OS versions */
    osVersion?: OsVersionResolver<(Maybe<OsVersion>)[], TypeParent, Context>;
  }

  export type OsVersionResolver<
    R = (Maybe<OsVersion>)[],
    Parent = PlaybookRequirements,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace VmSelectedIdListsResolvers {
  export interface Resolvers<Context = {}, TypeParent = VmSelectedIdLists> {
    start?: StartResolver<string[], TypeParent, Context>;

    stop?: StopResolver<string[], TypeParent, Context>;
  }

  export type StartResolver<
    R = string[],
    Parent = VmSelectedIdLists,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type StopResolver<
    R = string[],
    Parent = VmSelectedIdLists,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace MutationResolvers {
  export interface Resolvers<Context = {}, TypeParent = {}> {
    /** Create a new VM */
    createVm?: CreateVmResolver<Maybe<CreateVm>, TypeParent, Context>;
    /** Edit template options */
    template?: TemplateResolver<Maybe<TemplateMutation>, TypeParent, Context>;
    /** Edit VM options */
    vm?: VmResolver<Maybe<VmMutation>, TypeParent, Context>;
    /** Start VM */
    vmStart?: VmStartResolver<Maybe<VmStartMutation>, TypeParent, Context>;
    /** Shut down VM */
    vmShutdown?: VmShutdownResolver<
      Maybe<VmShutdownMutation>,
      TypeParent,
      Context
    >;
    /** Reboot VM */
    vmReboot?: VmRebootResolver<Maybe<VmRebootMutation>, TypeParent, Context>;
    /** If VM is Running, pause VM. If Paused, unpause VM */
    vmPause?: VmPauseResolver<Maybe<VmPauseMutation>, TypeParent, Context>;
    /** Launch an Ansible Playbook on specified VMs */
    playbookLaunch?: PlaybookLaunchResolver<
      Maybe<PlaybookLaunchMutation>,
      TypeParent,
      Context
    >;

    selectedItems?: SelectedItemsResolver<Maybe<string[]>, TypeParent, Context>;
  }

  export type CreateVmResolver<
    R = Maybe<CreateVm>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, CreateVmArgs>;
  export interface CreateVmArgs {
    /** Number of created virtual CPUs */
    VCPUs?: number;

    disks?: Maybe<(Maybe<NewVdi>)[]>;
    /** Automatic installation parameters, the installation is done via internet. Only available when template.os_kind is not empty */
    installParams?: Maybe<AutoInstall>;
    /** ISO image mounted if conf parameter is null */
    iso?: Maybe<string>;
    /** VM human-readable description */
    nameDescription: string;
    /** VM human-readable name */
    nameLabel: string;
    /** Network ID to connect to */
    network?: Maybe<string>;
    /** RAM size in megabytes */
    ram: number;
    /** Template ID */
    template: string;
  }

  export type TemplateResolver<
    R = Maybe<TemplateMutation>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, TemplateArgs>;
  export interface TemplateArgs {
    /** Template to change */
    template?: Maybe<TemplateInput>;
  }

  export type VmResolver<
    R = Maybe<VmMutation>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, VmArgs>;
  export interface VmArgs {
    /** VM to change */
    vm: VmInput;
  }

  export type VmStartResolver<
    R = Maybe<VmStartMutation>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, VmStartArgs>;
  export interface VmStartArgs {
    options?: Maybe<VmStartInput>;

    uuid: string;
  }

  export type VmShutdownResolver<
    R = Maybe<VmShutdownMutation>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, VmShutdownArgs>;
  export interface VmShutdownArgs {
    /** Force shutdown in a hard or clean way */
    force?: Maybe<ShutdownForce>;

    uuid: string;
  }

  export type VmRebootResolver<
    R = Maybe<VmRebootMutation>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, VmRebootArgs>;
  export interface VmRebootArgs {
    /** Force reboot in a hard or clean way. Default: clean */
    force?: Maybe<ShutdownForce>;

    uuid: string;
  }

  export type VmPauseResolver<
    R = Maybe<VmPauseMutation>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, VmPauseArgs>;
  export interface VmPauseArgs {
    uuid: string;
  }

  export type PlaybookLaunchResolver<
    R = Maybe<PlaybookLaunchMutation>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, PlaybookLaunchArgs>;
  export interface PlaybookLaunchArgs {
    /** Playbook ID */
    id: string;
    /** JSON with key-value pairs representing Playbook variables changed by user */
    variables?: Maybe<JsonString>;
    /** VM UUIDs to run Playbook on. Ignored if this is a Playbook with provided Inventory */
    vms?: Maybe<(Maybe<string>)[]>;
  }

  export type SelectedItemsResolver<
    R = Maybe<string[]>,
    Parent = {},
    Context = {}
  > = Resolver<R, Parent, Context, SelectedItemsArgs>;
  export interface SelectedItemsArgs {
    tableId: Table;

    items: string[];

    isSelect: boolean;
  }
}

export namespace CreateVmResolvers {
  export interface Resolvers<Context = {}, TypeParent = CreateVm> {
    /** Installation task ID */
    taskId?: TaskIdResolver<string, TypeParent, Context>;
  }

  export type TaskIdResolver<
    R = string,
    Parent = CreateVm,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace TemplateMutationResolvers {
  export interface Resolvers<Context = {}, TypeParent = TemplateMutation> {
    success?: SuccessResolver<boolean, TypeParent, Context>;
  }

  export type SuccessResolver<
    R = boolean,
    Parent = TemplateMutation,
    Context = {}
  > = Resolver<R, Parent, Context>;
}
/** This class represents synchronous mutations for VM, i.e. you can change name_label, name_description, etc. */
export namespace VmMutationResolvers {
  export interface Resolvers<Context = {}, TypeParent = VmMutation> {
    success?: SuccessResolver<boolean, TypeParent, Context>;
  }

  export type SuccessResolver<
    R = boolean,
    Parent = VmMutation,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace VmStartMutationResolvers {
  export interface Resolvers<Context = {}, TypeParent = VmStartMutation> {
    /** Start task ID */
    taskId?: TaskIdResolver<string, TypeParent, Context>;
  }

  export type TaskIdResolver<
    R = string,
    Parent = VmStartMutation,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace VmShutdownMutationResolvers {
  export interface Resolvers<Context = {}, TypeParent = VmShutdownMutation> {
    /** Shutdown task ID */
    taskId?: TaskIdResolver<string, TypeParent, Context>;
  }

  export type TaskIdResolver<
    R = string,
    Parent = VmShutdownMutation,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace VmRebootMutationResolvers {
  export interface Resolvers<Context = {}, TypeParent = VmRebootMutation> {
    /** Reboot task ID */
    taskId?: TaskIdResolver<string, TypeParent, Context>;
  }

  export type TaskIdResolver<
    R = string,
    Parent = VmRebootMutation,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace VmPauseMutationResolvers {
  export interface Resolvers<Context = {}, TypeParent = VmPauseMutation> {
    /** Pause/unpause task ID */
    taskId?: TaskIdResolver<string, TypeParent, Context>;
  }

  export type TaskIdResolver<
    R = string,
    Parent = VmPauseMutation,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace PlaybookLaunchMutationResolvers {
  export interface Resolvers<
    Context = {},
    TypeParent = PlaybookLaunchMutation
  > {
    /** Playbook execution task ID */
    taskId?: TaskIdResolver<string, TypeParent, Context>;
  }

  export type TaskIdResolver<
    R = string,
    Parent = PlaybookLaunchMutation,
    Context = {}
  > = Resolver<R, Parent, Context>;
}
/** All subscriptions must return  Observable */
export namespace SubscriptionResolvers {
  export interface Resolvers<Context = {}, TypeParent = {}> {
    /** Updates for all VMs */
    vms?: VmsResolver<GvMsSubscription, TypeParent, Context>;
    /** Updates for a particular VM */
    vm?: VmResolver<Maybe<Gvm>, TypeParent, Context>;
    /** Updates for a particular XenServer Task */
    task?: TaskResolver<Maybe<GTask>, TypeParent, Context>;
    /** Updates for a particular Playbook installation Task */
    playbookTask?: PlaybookTaskResolver<PlaybookTask, TypeParent, Context>;
    /** Updates for all Playbook Tasks */
    playbookTasks?: PlaybookTasksResolver<
      PlaybookTasksSubscription,
      TypeParent,
      Context
    >;
  }

  export type VmsResolver<
    R = GvMsSubscription,
    Parent = {},
    Context = {}
  > = SubscriptionResolver<R, Parent, Context>;
  export type VmResolver<
    R = Maybe<Gvm>,
    Parent = {},
    Context = {}
  > = SubscriptionResolver<R, Parent, Context, VmArgs>;
  export interface VmArgs {
    uuid?: Maybe<string>;
  }

  export type TaskResolver<
    R = Maybe<GTask>,
    Parent = {},
    Context = {}
  > = SubscriptionResolver<R, Parent, Context, TaskArgs>;
  export interface TaskArgs {
    uuid?: Maybe<string>;
  }

  export type PlaybookTaskResolver<
    R = PlaybookTask,
    Parent = {},
    Context = {}
  > = SubscriptionResolver<R, Parent, Context, PlaybookTaskArgs>;
  export interface PlaybookTaskArgs {
    id?: Maybe<string>;
  }

  export type PlaybookTasksResolver<
    R = PlaybookTasksSubscription,
    Parent = {},
    Context = {}
  > = SubscriptionResolver<R, Parent, Context>;
}

export namespace GvMsSubscriptionResolvers {
  export interface Resolvers<Context = {}, TypeParent = GvMsSubscription> {
    /** Change type */
    changeType?: ChangeTypeResolver<Change, TypeParent, Context>;

    value?: ValueResolver<Gvm, TypeParent, Context>;
  }

  export type ChangeTypeResolver<
    R = Change,
    Parent = GvMsSubscription,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type ValueResolver<
    R = Gvm,
    Parent = GvMsSubscription,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GTaskResolvers {
  export interface Resolvers<Context = {}, TypeParent = GTask> {
    /** a human-readable name */
    nameLabel?: NameLabelResolver<string, TypeParent, Context>;
    /** a human-readable description */
    nameDescription?: NameDescriptionResolver<string, TypeParent, Context>;
    /** Unique constant identifier/object reference */
    ref?: RefResolver<string, TypeParent, Context>;
    /** Unique session-dependent identifier/object reference */
    uuid?: UuidResolver<string, TypeParent, Context>;

    access?: AccessResolver<(Maybe<GAccessEntry>)[], TypeParent, Context>;
    /** Task creation time */
    created?: CreatedResolver<DateTime, TypeParent, Context>;
    /** Task finish time */
    finished?: FinishedResolver<DateTime, TypeParent, Context>;
    /** Task progress */
    progress?: ProgressResolver<number, TypeParent, Context>;
    /** Task result if available */
    result?: ResultResolver<Maybe<string>, TypeParent, Context>;
    /** Task result type */
    type?: TypeResolver<Maybe<string>, TypeParent, Context>;
    /** ref of a host that runs this task */
    residentOn?: ResidentOnResolver<Maybe<string>, TypeParent, Context>;
    /** Error strings, if failed */
    errorInfo?: ErrorInfoResolver<
      Maybe<(Maybe<string>)[]>,
      TypeParent,
      Context
    >;
    /** Task status */
    status?: StatusResolver<Maybe<string>, TypeParent, Context>;
  }

  export type NameLabelResolver<
    R = string,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type NameDescriptionResolver<
    R = string,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type RefResolver<R = string, Parent = GTask, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type UuidResolver<R = string, Parent = GTask, Context = {}> = Resolver<
    R,
    Parent,
    Context
  >;
  export type AccessResolver<
    R = (Maybe<GAccessEntry>)[],
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type CreatedResolver<
    R = DateTime,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type FinishedResolver<
    R = DateTime,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type ProgressResolver<
    R = number,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type ResultResolver<
    R = Maybe<string>,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type TypeResolver<
    R = Maybe<string>,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type ResidentOnResolver<
    R = Maybe<string>,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type ErrorInfoResolver<
    R = Maybe<(Maybe<string>)[]>,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type StatusResolver<
    R = Maybe<string>,
    Parent = GTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace PlaybookTaskResolvers {
  export interface Resolvers<Context = {}, TypeParent = PlaybookTask> {
    /** Playbook task ID */
    id?: IdResolver<string, TypeParent, Context>;
    /** Playbook ID */
    playbookId?: PlaybookIdResolver<string, TypeParent, Context>;
    /** Playbook running state */
    state?: StateResolver<PlaybookTaskState, TypeParent, Context>;
    /** Human-readable message: error description or return code */
    message?: MessageResolver<string, TypeParent, Context>;
  }

  export type IdResolver<
    R = string,
    Parent = PlaybookTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type PlaybookIdResolver<
    R = string,
    Parent = PlaybookTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type StateResolver<
    R = PlaybookTaskState,
    Parent = PlaybookTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type MessageResolver<
    R = string,
    Parent = PlaybookTask,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace PlaybookTasksSubscriptionResolvers {
  export interface Resolvers<
    Context = {},
    TypeParent = PlaybookTasksSubscription
  > {
    /** Change type */
    changeType?: ChangeTypeResolver<Change, TypeParent, Context>;

    value?: ValueResolver<PlaybookTask, TypeParent, Context>;
  }

  export type ChangeTypeResolver<
    R = Change,
    Parent = PlaybookTasksSubscription,
    Context = {}
  > = Resolver<R, Parent, Context>;
  export type ValueResolver<
    R = PlaybookTask,
    Parent = PlaybookTasksSubscription,
    Context = {}
  > = Resolver<R, Parent, Context>;
}

export namespace GAclXenObjectResolvers {
  export interface Resolvers {
    __resolveType: ResolveType;
  }
  export type ResolveType<
    R = "GVM" | "GNetwork" | "GVDI" | "GISO" | "GTemplate" | "GTask",
    Parent = Gvm | GNetwork | Gvdi | Giso | GTemplate | GTask,
    Context = {}
  > = TypeResolveFn<R, Parent, Context>;
}

export namespace DiskImageResolvers {
  export interface Resolvers {
    __resolveType: ResolveType;
  }
  export type ResolveType<
    R = "GVDI" | "GISO",
    Parent = Gvdi | Giso,
    Context = {}
  > = TypeResolveFn<R, Parent, Context>;
}

export namespace GXenObjectResolvers {
  export interface Resolvers {
    __resolveType: ResolveType;
  }
  export type ResolveType<
    R = "GSR",
    Parent = Gsr,
    Context = {}
  > = TypeResolveFn<R, Parent, Context>;
}

/** Directs the executor to skip this field or fragment when the `if` argument is true. */
export type SkipDirectiveResolver<Result> = DirectiveResolverFn<
  Result,
  SkipDirectiveArgs,
  {}
>;
export interface SkipDirectiveArgs {
  /** Skipped when true. */
  if: boolean;
}

/** Directs the executor to include this field or fragment only when the `if` argument is true. */
export type IncludeDirectiveResolver<Result> = DirectiveResolverFn<
  Result,
  IncludeDirectiveArgs,
  {}
>;
export interface IncludeDirectiveArgs {
  /** Included when true. */
  if: boolean;
}

/** Marks an element of a GraphQL schema as no longer supported. */
export type DeprecatedDirectiveResolver<Result> = DirectiveResolverFn<
  Result,
  DeprecatedDirectiveArgs,
  {}
>;
export interface DeprecatedDirectiveArgs {
  /** Explains why this element was deprecated, usually also including a suggestion for how to access supported similar data. Formatted using the Markdown syntax (as specified by [CommonMark](https://commonmark.org/). */
  reason?: string;
}

export interface JSONStringScalarConfig
  extends GraphQLScalarTypeConfig<JsonString, any> {
  name: "JSONString";
}
export interface DateTimeScalarConfig
  extends GraphQLScalarTypeConfig<DateTime, any> {
  name: "DateTime";
}

export interface IResolvers<Context = {}> {
  Query?: QueryResolvers.Resolvers<Context>;
  Gvm?: GvmResolvers.Resolvers<Context>;
  GAccessEntry?: GAccessEntryResolvers.Resolvers<Context>;
  Interface?: InterfaceResolvers.Resolvers<Context>;
  GNetwork?: GNetworkResolvers.Resolvers<Context>;
  PvDriversVersion?: PvDriversVersionResolvers.Resolvers<Context>;
  BlockDevice?: BlockDeviceResolvers.Resolvers<Context>;
  Gsr?: GsrResolvers.Resolvers<Context>;
  OsVersion?: OsVersionResolvers.Resolvers<Context>;
  Gvdi?: GvdiResolvers.Resolvers<Context>;
  Giso?: GisoResolvers.Resolvers<Context>;
  GTemplate?: GTemplateResolvers.Resolvers<Context>;
  GPlaybook?: GPlaybookResolvers.Resolvers<Context>;
  PlaybookRequirements?: PlaybookRequirementsResolvers.Resolvers<Context>;
  VmSelectedIdLists?: VmSelectedIdListsResolvers.Resolvers<Context>;
  Mutation?: MutationResolvers.Resolvers<Context>;
  CreateVm?: CreateVmResolvers.Resolvers<Context>;
  TemplateMutation?: TemplateMutationResolvers.Resolvers<Context>;
  VmMutation?: VmMutationResolvers.Resolvers<Context>;
  VmStartMutation?: VmStartMutationResolvers.Resolvers<Context>;
  VmShutdownMutation?: VmShutdownMutationResolvers.Resolvers<Context>;
  VmRebootMutation?: VmRebootMutationResolvers.Resolvers<Context>;
  VmPauseMutation?: VmPauseMutationResolvers.Resolvers<Context>;
  PlaybookLaunchMutation?: PlaybookLaunchMutationResolvers.Resolvers<Context>;
  Subscription?: SubscriptionResolvers.Resolvers<Context>;
  GvMsSubscription?: GvMsSubscriptionResolvers.Resolvers<Context>;
  GTask?: GTaskResolvers.Resolvers<Context>;
  PlaybookTask?: PlaybookTaskResolvers.Resolvers<Context>;
  PlaybookTasksSubscription?: PlaybookTasksSubscriptionResolvers.Resolvers<
    Context
  >;
  GAclXenObject?: GAclXenObjectResolvers.Resolvers;
  DiskImage?: DiskImageResolvers.Resolvers;
  GXenObject?: GXenObjectResolvers.Resolvers;
  JsonString?: GraphQLScalarType;
  DateTime?: GraphQLScalarType;
}

export interface IDirectiveResolvers<Result> {
  skip?: SkipDirectiveResolver<Result>;
  include?: IncludeDirectiveResolver<Result>;
  deprecated?: DeprecatedDirectiveResolver<Result>;
}

// ====================================================
// Scalars
// ====================================================

// ====================================================
// Interfaces
// ====================================================

export interface GAclXenObject {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  access: (Maybe<GAccessEntry>)[];
}

export interface DiskImage {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  SR?: Maybe<Gsr>;

  VMs?: Maybe<(Maybe<Gvm>)[]>;

  virtualSize: number;
}

export interface GXenObject {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;
}

// ====================================================
// Types
// ====================================================

export interface Query {
  /** All VMs available to user */
  vms: (Maybe<Gvm>)[];

  vm: Gvm;
  /** All Networks available to user */
  networks: (Maybe<GNetwork>)[];
  /** Information about a single network */
  network: GNetwork;
  /** All Storage repositories available to user */
  srs: (Maybe<Gsr>)[];
  /** Information about a single storage repository */
  sr: Gsr;
  /** All Virtual Disk Images (hard disks), available for user */
  vdis: (Maybe<Gvdi>)[];
  /** Information about a single virtual disk image (hard disk) */
  vdi: Gvdi;
  /** All ISO images available for user */
  isos: (Maybe<Giso>)[];
  /** Information about a single ISO image */
  iso: Gvdi;
  /** All templates */
  templates: (Maybe<GTemplate>)[];
  /** List of Ansible-powered playbooks */
  playbooks: (Maybe<GPlaybook>)[];
  /** Information about Ansible-powered playbook */
  playbook: GPlaybook;

  selectedItems: string[];

  vmSelectedReadyFor: VmSelectedIdLists;
}

export interface Gvm extends GAclXenObject {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  access: (Maybe<GAccessEntry>)[];
  /** Network adapters connected to a VM */
  interfaces?: Maybe<(Maybe<Interface>)[]>;
  /** True if PV drivers are up to date, reported if Guest Additions are installed */
  PVDriversUpToDate?: Maybe<boolean>;
  /** PV drivers version, if available */
  PVDriversVersion?: Maybe<PvDriversVersion>;

  disks?: Maybe<(Maybe<BlockDevice>)[]>;

  VCPUsAtStartup: number;

  VCPUsMax: number;

  domainType: string;

  guestMetrics: string;

  installTime: DateTime;

  memoryActual: number;

  memoryStaticMin: number;

  memoryStaticMax: number;

  memoryDynamicMin: number;

  memoryDynamicMax: number;

  metrics: string;

  osVersion?: Maybe<OsVersion>;

  powerState: PowerState;

  startTime: DateTime;
}

export interface GAccessEntry {
  access: (Maybe<string>)[];

  userid: string;
}

export interface Interface {
  id: string;

  MAC: string;

  VIF: string;

  ip?: Maybe<string>;

  ipv6?: Maybe<string>;

  network: GNetwork;

  status?: Maybe<string>;

  attached: boolean;
}

export interface GNetwork extends GAclXenObject {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  access: (Maybe<GAccessEntry>)[];

  VMs?: Maybe<(Maybe<Gvm>)[]>;

  otherConfig?: Maybe<JsonString>;
}

/** Drivers version. We don't want any fancy resolver except for the thing that we know that it's a dict in VM document */
export interface PvDriversVersion {
  major?: Maybe<number>;

  minor?: Maybe<number>;

  micro?: Maybe<number>;

  build?: Maybe<number>;
}

export interface BlockDevice {
  id: string;

  attached: boolean;

  bootable: boolean;

  device: string;

  mode: string;

  type: string;

  VDI?: Maybe<DiskImage>;
}

export interface Gsr extends GXenObject {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  PBDs?: Maybe<(Maybe<string>)[]>;

  VDIs?: Maybe<(Maybe<DiskImage>)[]>;

  contentType: string;
}

/** OS version reported by Xen tools */
export interface OsVersion {
  name?: Maybe<string>;

  uname?: Maybe<string>;

  distro?: Maybe<string>;

  major?: Maybe<number>;

  minor?: Maybe<number>;
}

export interface Gvdi extends GAclXenObject, DiskImage {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  access: (Maybe<GAccessEntry>)[];

  SR?: Maybe<Gsr>;

  VMs?: Maybe<(Maybe<Gvm>)[]>;

  virtualSize: number;
}

export interface Giso extends GAclXenObject, DiskImage {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  access: (Maybe<GAccessEntry>)[];

  SR?: Maybe<Gsr>;

  VMs?: Maybe<(Maybe<Gvm>)[]>;

  virtualSize: number;

  location: string;
}

export interface GTemplate extends GAclXenObject {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  access: (Maybe<GAccessEntry>)[];
  /** If a template supports auto-installation, here a distro name is provided */
  osKind?: Maybe<string>;
  /** True if this template works with hardware assisted virtualization */
  hvm: boolean;
  /** True if this template is available for regular users */
  enabled: boolean;
}

export interface GPlaybook {
  /** Playbook ID */
  id: string;
  /** Inventory file path */
  inventory?: Maybe<string>;
  /** Requirements for running this playbook */
  requires?: Maybe<PlaybookRequirements>;
  /** Playbook name */
  name: string;
  /** Playbook description */
  description?: Maybe<string>;
  /** Variables available for change to an user */
  variables?: Maybe<JsonString>;
}

export interface PlaybookRequirements {
  /** Minimal supported OS versions */
  osVersion: (Maybe<OsVersion>)[];
}

export interface VmSelectedIdLists {
  start: string[];

  stop: string[];
}

export interface Mutation {
  /** Create a new VM */
  createVm?: Maybe<CreateVm>;
  /** Edit template options */
  template?: Maybe<TemplateMutation>;
  /** Edit VM options */
  vm?: Maybe<VmMutation>;
  /** Start VM */
  vmStart?: Maybe<VmStartMutation>;
  /** Shut down VM */
  vmShutdown?: Maybe<VmShutdownMutation>;
  /** Reboot VM */
  vmReboot?: Maybe<VmRebootMutation>;
  /** If VM is Running, pause VM. If Paused, unpause VM */
  vmPause?: Maybe<VmPauseMutation>;
  /** Launch an Ansible Playbook on specified VMs */
  playbookLaunch?: Maybe<PlaybookLaunchMutation>;

  selectedItems?: Maybe<string[]>;
}

export interface CreateVm {
  /** Installation task ID */
  taskId: string;
}

export interface TemplateMutation {
  success: boolean;
}

/** This class represents synchronous mutations for VM, i.e. you can change name_label, name_description, etc. */
export interface VmMutation {
  success: boolean;
}

export interface VmStartMutation {
  /** Start task ID */
  taskId: string;
}

export interface VmShutdownMutation {
  /** Shutdown task ID */
  taskId: string;
}

export interface VmRebootMutation {
  /** Reboot task ID */
  taskId: string;
}

export interface VmPauseMutation {
  /** Pause/unpause task ID */
  taskId: string;
}

export interface PlaybookLaunchMutation {
  /** Playbook execution task ID */
  taskId: string;
}

/** All subscriptions must return  Observable */
export interface Subscription {
  /** Updates for all VMs */
  vms: GvMsSubscription;
  /** Updates for a particular VM */
  vm?: Maybe<Gvm>;
  /** Updates for a particular XenServer Task */
  task?: Maybe<GTask>;
  /** Updates for a particular Playbook installation Task */
  playbookTask: PlaybookTask;
  /** Updates for all Playbook Tasks */
  playbookTasks: PlaybookTasksSubscription;
}

export interface GvMsSubscription {
  /** Change type */
  changeType: Change;

  value: Gvm;
}

export interface GTask extends GAclXenObject {
  /** a human-readable name */
  nameLabel: string;
  /** a human-readable description */
  nameDescription: string;
  /** Unique constant identifier/object reference */
  ref: string;
  /** Unique session-dependent identifier/object reference */
  uuid: string;

  access: (Maybe<GAccessEntry>)[];
  /** Task creation time */
  created: DateTime;
  /** Task finish time */
  finished: DateTime;
  /** Task progress */
  progress: number;
  /** Task result if available */
  result?: Maybe<string>;
  /** Task result type */
  type?: Maybe<string>;
  /** ref of a host that runs this task */
  residentOn?: Maybe<string>;
  /** Error strings, if failed */
  errorInfo?: Maybe<(Maybe<string>)[]>;
  /** Task status */
  status?: Maybe<string>;
}

export interface PlaybookTask {
  /** Playbook task ID */
  id: string;
  /** Playbook ID */
  playbookId: string;
  /** Playbook running state */
  state: PlaybookTaskState;
  /** Human-readable message: error description or return code */
  message: string;
}

export interface PlaybookTasksSubscription {
  /** Change type */
  changeType: Change;

  value: PlaybookTask;
}

// ====================================================
// Arguments
// ====================================================

export interface VmQueryArgs {
  uuid?: Maybe<string>;
}
export interface NetworkQueryArgs {
  uuid?: Maybe<string>;
}
export interface SrQueryArgs {
  uuid?: Maybe<string>;
}
export interface VdiQueryArgs {
  uuid?: Maybe<string>;
}
export interface IsoQueryArgs {
  uuid?: Maybe<string>;
}
export interface PlaybookQueryArgs {
  id?: Maybe<string>;
}
export interface SelectedItemsQueryArgs {
  tableId: Table;
}
export interface CreateVmMutationArgs {
  /** Number of created virtual CPUs */
  VCPUs?: number;

  disks?: Maybe<(Maybe<NewVdi>)[]>;
  /** Automatic installation parameters, the installation is done via internet. Only available when template.os_kind is not empty */
  installParams?: Maybe<AutoInstall>;
  /** ISO image mounted if conf parameter is null */
  iso?: Maybe<string>;
  /** VM human-readable description */
  nameDescription: string;
  /** VM human-readable name */
  nameLabel: string;
  /** Network ID to connect to */
  network?: Maybe<string>;
  /** RAM size in megabytes */
  ram: number;
  /** Template ID */
  template: string;
}
export interface TemplateMutationArgs {
  /** Template to change */
  template?: Maybe<TemplateInput>;
}
export interface VmMutationArgs {
  /** VM to change */
  vm: VmInput;
}
export interface VmStartMutationArgs {
  options?: Maybe<VmStartInput>;

  uuid: string;
}
export interface VmShutdownMutationArgs {
  /** Force shutdown in a hard or clean way */
  force?: Maybe<ShutdownForce>;

  uuid: string;
}
export interface VmRebootMutationArgs {
  /** Force reboot in a hard or clean way. Default: clean */
  force?: Maybe<ShutdownForce>;

  uuid: string;
}
export interface VmPauseMutationArgs {
  uuid: string;
}
export interface PlaybookLaunchMutationArgs {
  /** Playbook ID */
  id: string;
  /** JSON with key-value pairs representing Playbook variables changed by user */
  variables?: Maybe<JsonString>;
  /** VM UUIDs to run Playbook on. Ignored if this is a Playbook with provided Inventory */
  vms?: Maybe<(Maybe<string>)[]>;
}
export interface SelectedItemsMutationArgs {
  tableId: Table;

  items: string[];

  isSelect: boolean;
}
export interface VmSubscriptionArgs {
  uuid?: Maybe<string>;
}
export interface TaskSubscriptionArgs {
  uuid?: Maybe<string>;
}
export interface PlaybookTaskSubscriptionArgs {
  id?: Maybe<string>;
}
