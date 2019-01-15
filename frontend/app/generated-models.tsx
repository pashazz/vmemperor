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

export enum ShutdownForce {
  Hard = "HARD",
  Clean = "CLEAN"
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

  export type Vm = {
    __typename?: "GVM";

    uuid: string;

    nameLabel: string;

    nameDescription: string;

    interfaces: Maybe<(Maybe<Interfaces>)[]>;

    powerState: string;

    osVersion: Maybe<OsVersion>;

    startTime: DateTime;

    domainType: string;
  };

  export type Interfaces = {
    __typename?: "Interface";

    network: Network;

    ip: Maybe<string>;

    ipv6: Maybe<string>;
  };

  export type Network = {
    __typename?: "GNetwork";

    uuid: string;

    nameLabel: string;
  };

  export type OsVersion = {
    __typename?: "OSVersion";

    name: Maybe<string>;
  };
}

import * as ReactApollo from "react-apollo";
import * as React from "react";

import gql from "graphql-tag";

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
        }
        powerState
        osVersion {
          name
        }
        startTime
        domainType
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
