import React, {Reducer, ReducerState, useCallback, useReducer} from 'react';
import {useSubscription} from "../../hooks/subscription";
import {
  Change,
  DeleteVm,
  PowerState,
  ShutdownVm,
  StartVm,
  VmList,
  VmListFragment,
  VmListUpdate,
  VmStateForButtonToolbar,
  VmTableSelect,
  VmTableSelectAll,
  VmTableSelection
} from '../../generated-models';
import StatefulTable, {ColumnType} from "../StatefulTable";
import {RouteComponentProps} from "react-router";
import filterFactory, {textFilter} from 'react-bootstrap-table2-filter'
import tableStyle from "./table.css";
import {useApolloClient, useMutation, useQuery} from "react-apollo-hooks";
import {Map, Set} from 'immutable';
import {ButtonGroup, ButtonToolbar} from "reactstrap";
import {dataIdFromObject, handleAddOfValue, handleAddRemove, handleRemoveOfValueByUuid} from "../../utils/cacheUtils";
import StartButton from "../../components/StartButton";
import StopButton from "../../components/StopButton";
import RecycleBinButton from "../../components/RecycleBinButton";

function nameFormatter(column, colIndex, {sortElement, filterElement}) {
  return (
    <div style={{display: 'flex', flexDirection: 'column'}}>
      {column.text}
      {filterElement}
      {sortElement}
    </div>
  );
}

function plainFormatter(column, colIndex, {sortElement, filterElement}) {
  return (
    <div style={{display: 'flex', flexDirection: 'column'}}>
      {column.text}
      {filterElement}
      {sortElement}
    </div>
  );
}


type VmColumnType = ColumnType<VmListFragment.Fragment>;

const columns: VmColumnType[] = [
  {
    dataField: 'nameLabel',
    text: 'Name',
    filter: textFilter(),
    headerFormatter: nameFormatter,
    headerClasses: 'align-self-baseline'

  },
  {
    dataField: "powerState",
    text: 'Status',
    headerFormatter: plainFormatter,
    headerClasses: 'align-self-baseline'

  }
];


function rowClasses(row: VmListFragment.Fragment, rowIndex) {
  switch (row.powerState) {
    case 'Halted':
      return 'table-danger';
    case 'Running':
      return 'table-success';
    default:
      return "";
  }
}

interface State {
  selectedForStart: Set<string>;
  selectedForStop: Set<string>;
  selectedForTrash: Set<string>;
  wholeSelectionByPowerState: Map<string, PowerState>;
}

interface Action {
  type: "Add" | "Change" | "Remove";
  uuid: string;

}

type VMListReducer = Reducer<State, Action>;


const initialState: ReducerState<VMListReducer> = {
  selectedForStart: Set.of<string>(),
  selectedForStop: Set.of<string>(),
  selectedForTrash: Set.of<string>(),
  wholeSelectionByPowerState: Map<string, PowerState>()
};

export default function ({history}: RouteComponentProps) {
  const {
    data: {vms},
  } = useQuery<VmList.Query>(VmList.Document);

  const client = useApolloClient();

  const reducer: VMListReducer = (state, action) => {
    //Read fragment associated with this VM in the cache
    const info = client.cache.readFragment<VmListFragment.Fragment>({
      fragment: VmListFragment.FragmentDoc,
      id: dataIdFromObject({
        uuid: action.uuid,
        __typename: "GVM",
      }),
    });
    console.log("Got associated info: ", info, "Action:", action.type);
    console.log("State:", state);

    if (action.type === 'Add' && state.wholeSelectionByPowerState.has(action.uuid))
      return state;

    switch (action.type) {
      case "Change":
        if (!state.wholeSelectionByPowerState.has(action.uuid) ||
          (state.wholeSelectionByPowerState[action.uuid] === info.powerState))
          return state;
      case "Add":
        return {
          selectedForStart: info.powerState !== PowerState.Running
            ? state.selectedForStart.add(action.uuid)
            : state.selectedForStart.remove(action.uuid),
          selectedForStop: info.powerState !== PowerState.Halted
            ? state.selectedForStop.add(action.uuid)
            : state.selectedForStop.remove(action.uuid),
          selectedForTrash: info.powerState === PowerState.Halted
            ? state.selectedForTrash.add(action.uuid)
            : state.selectedForTrash.remove(action.uuid),
          wholeSelectionByPowerState: state.wholeSelectionByPowerState.set(action.uuid, info.powerState)

        };
      case "Remove":
        return {
          selectedForStart: state.selectedForStart.remove(action.uuid),
          selectedForStop: state.selectedForStop.remove(action.uuid),
          selectedForTrash: state.selectedForTrash.remove(action.uuid),
          wholeSelectionByPowerState: state.wholeSelectionByPowerState.remove(action.uuid)
        }

    }
  };
  const [{selectedForStart, selectedForStop, selectedForTrash, wholeSelectionByPowerState}, dispatch] = useReducer<VMListReducer>(reducer, initialState);

  const onDoubleClick = useCallback((e: React.MouseEvent, row: VmListFragment.Fragment, index) => {
    e.preventDefault();
    history.push(`/vmsettings/${row.uuid}`);
  }, [history]);

  useSubscription<VmListUpdate.Subscription>(VmListUpdate.Document,
    {
      onSubscriptionData({client, subscriptionData}) {
        //Changing is handled automatically, here we're handling removal & addition
        const change = subscriptionData.vms;
        switch (change.changeType) {
          case Change.Add:
          case Change.Remove:
            console.log("Add/Remove: ", change);
            handleAddRemove(client, VmList.Document, 'vms', change);
            break;
          case Change.Change: //Update our internal state
            dispatch({
              type: "Change",
              uuid: change.value.uuid,
            });
            break;
          default:
            break;
        }
      }
    });


  const startVm = useMutation<StartVm.Mutation, StartVm.Variables>(
    StartVm.Document);
  const onStartVm = async () => {
    console.log("Staring...", selectedForStart);
    for (const id of selectedForStart.toArray()) {
      await startVm({
        variables: {
          uuid: id
        },
      });

    }
  };
  const stopVm = useMutation<ShutdownVm.Mutation, ShutdownVm.Variables>(
    ShutdownVm.Document);
  const onStopVm = async () => {
    for (const id of selectedForStop.toArray()) {
      console.log("Stopping...", id);
      await stopVm(
        {
          variables: {
            uuid: id
          },
        }
      );
    }
  };

  const deleteVm = useMutation<DeleteVm.Mutation, DeleteVm.Variables>(
    DeleteVm.Document);
  const onDeleteVm = async () => {
    for (const id of selectedForTrash.toArray()) {
      await deleteVm(
        {
          variables: {
            uuid: id
          }
        });
    }
  };


  return (
    <React.Fragment>
      <ButtonToolbar>
        <ButtonGroup size="lg">
          <StartButton
            onClick={onStartVm}
            disabled={selectedForStart.size == 0}/>

          <StopButton
            onClick={onStopVm}
            disabled={selectedForStop.size == 0}/>
        </ButtonGroup>
        <ButtonGroup className="ml-auto">
          <RecycleBinButton
            onClick={onDeleteVm}
            disabled={selectedForTrash.size == 0}/>
        </ButtonGroup>
      </ButtonToolbar>
      <StatefulTable
        keyField="uuid"
        refetchQueriesOnSelect={
          [
            {
              query: VmStateForButtonToolbar.Document
            }
          ]
        }
        data={vms}
        tableSelectOne={VmTableSelect.Document}
        tableSelectMany={VmTableSelectAll.Document}
        tableSelectionQuery={VmTableSelection.Document}
        columns={columns}

        props={
          {
            filter: filterFactory(),
            style: tableStyle,
            noDataIndication: "No VMs available... create something new!",
            striped: true,
            hover: true,
            rowClasses,
          }
        }
        onDoubleClick={onDoubleClick}
        onSelect={(key, isSelect) => dispatch({
          type: isSelect ? "Add" : "Remove",
          uuid: key,
        })}
      />
    </React.Fragment>)


}
