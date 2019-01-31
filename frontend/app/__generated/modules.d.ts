declare module "*/editVm.graphql" {
  import { DocumentNode } from "graphql";
  const defaultDocument: DocumentNode;
  const VMEditOptions: DocumentNode;

  export { VMEditOptions };

  export default defaultDocument;
}

declare module "*/playbookLaunch.graphql" {
  import { DocumentNode } from "graphql";
  const defaultDocument: DocumentNode;
  const PlaybookLaunch: DocumentNode;

  export { PlaybookLaunch };

  export default defaultDocument;
}

declare module "*/playbooks.graphql" {
  import { DocumentNode } from "graphql";
  const defaultDocument: DocumentNode;
  const PlaybookList: DocumentNode;

  export { PlaybookList };

  export default defaultDocument;
}

declare module "*/rebootVm.graphql" {
  import { DocumentNode } from "graphql";
  const defaultDocument: DocumentNode;
  const RebootVm: DocumentNode;

  export { RebootVm };

  export default defaultDocument;
}

declare module "*/shutdownVm.graphql" {
  import { DocumentNode } from "graphql";
  const defaultDocument: DocumentNode;
  const ShutdownVM: DocumentNode;

  export { ShutdownVM };

  export default defaultDocument;
}

declare module "*/startVm.graphql" {
  import { DocumentNode } from "graphql";
  const defaultDocument: DocumentNode;
  const StartVM: DocumentNode;

  export { StartVM };

  export default defaultDocument;
}

declare module "*/vminfo.graphql" {
  import { DocumentNode } from "graphql";
  const defaultDocument: DocumentNode;
  const VMInfo: DocumentNode;
  const VMInfoUpdate: DocumentNode;

  export { VMInfo, VMInfoUpdate };

  export default defaultDocument;
}
