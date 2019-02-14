import {useSubscription} from "../../hooks/subscription";
import {PlaybookTaskUpdate} from "../../generated-models";

interface Props {
  taskId: string,
}

const PlaybookWatcher = ({taskId}: Props) => {
  const data = useSubscription<PlaybookTaskUpdate.Subscription, PlaybookTaskUpdate.Variables>(PlaybookTaskUpdate.Document,
    {
      variables: {}
    });
};
