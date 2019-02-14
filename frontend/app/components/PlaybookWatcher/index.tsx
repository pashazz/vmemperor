import {useSubscription} from "../../hooks/subscription";
import {PlaybookTaskUpdate} from "../../generated-models";

interface Props {
  taskId: string,
}

const PlaybookWatcher = ({taskId}: Props) => {
  

  useSubscription<PlaybookTaskUpdate.Subscription, PlaybookTaskUpdate.Variables>(PlaybookTaskUpdate.Document,
    {
      variables: {
        id: taskId
      }
    });
};
